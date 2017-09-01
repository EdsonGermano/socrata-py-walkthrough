import webbrowser
from examples.auth import authorization
import os
from socrata import Socrata
from examples.adventure.util import interaction, back, prompt, setup_logging, dedent
from prettytable import PrettyTable
from os import listdir
from os.path import isfile, join

socrata = Socrata(authorization)

def print_rows(output_schema, rows):
    headers = [oc['field_name'] for oc in output_schema.attributes['output_columns']]
    t = PrettyTable(headers)

    def format_cell(cell):
        if 'ok' in cell:
            return cell['ok']
        return 'Error(%s)' % cell['error']['message']['english']

    for row in rows:
        row_list = [format_cell(row[h]) for h in headers]
        t.add_row(row_list)

    print(t)

def print_data(output_schema):
    def run():
        (ok, rows) = output_schema.rows(limit = 40, offset = 0)
        assert ok, rows
        print_rows(output_schema, rows)
    return run

def print_errors(output_schema):
    def run():
        # This is a streaming response, hence iter_lines()
        (ok, errors) = output_schema.schema_errors()
        assert ok, errors
        print_rows(output_schema, errors)
    return run

def print_output_schema(output_schema):
    def run():
        print(output_schema)
    return run

def print_row_counts(output_schema):
    def run():
        input_schema = output_schema.parent
        print('Total rows:', input_schema.attributes['total_rows'])
        print('Error rows:', output_schema.attributes['error_count'])
    return run

def add_column(revision, output_schema):
    def run():
        field_name = prompt('Enter the field name that you would like your new column to have')
        expr = prompt('Enter the SoQL expression which will populate the data in your column')

        (ok, new_output_schema) = output_schema.add_column(
            field_name, field_name, expr
        ).run()

        if not ok:
            print('Failed to add column!\n', new_output_schema)
            add_column(revision, output_schema)()
        else:
            print("New output schema created!")
        use_output_schema(revision, new_output_schema)()
    return run


def drop_column(revision, output_schema):
    def run():
        field_name = prompt('Column field name')

        (ok, new_output_schema) = output_schema.drop_column(
            field_name
        ).run()

        if not ok:
            print('Failed to drop column!\n', new_output_schema)
            drop_column(revision, output_schema)()
        use_output_schema(revision, new_output_schema)()
    return run

def transform_column_data(revision, output_schema):
    def run():
        field_name = prompt('Enter the field name of the column to change')
        expr = prompt('Enter the SoQL expression which will populate the data in your column')

        (ok, new_output_schema) = output_schema.change_column_transform(
            field_name
        ).to(expr).run()

        if not ok:
            print('Failed to change column!\n', new_output_schema)
            transform_column_data(revision, output_schema)()
        else:
            print("New output schema created!")

        use_output_schema(revision, new_output_schema)()
    return run


def change_column_metadata(revision, output_schema):
    def run():
        field_name = prompt('Enter the field name of the column to change')
        attr = prompt('Enter the attribute you want to change, one of "field_name", "description", "display_name"')
        attr_value = prompt('Enter the new value of the attribute')

        (ok, new_output_schema) = output_schema.change_column_metadata(
            field_name, attr
        ).to(attr_value).run()

        if not ok:
            print('Failed to change column!\n', new_output_schema)
            change_column_metadata(revision, output_schema)()
        else:
            print("New output schema created!")

        use_output_schema(revision, new_output_schema)()
    return run


def help_transform(revision, output_schema):
    def run():
        url = "http://docs.socratapublishing.apiary.io/#reference/0/inputschema/create-a-new-schema"
        print("Opening", url)
        webbrowser.open(url, new = 2)
    return run

def transform_output_schema(revision, output_schema):
    def run():
        columns = [c['field_name'] for c in output_schema.parent.attributes['input_columns']]

        ex1 = 'to_number(`%s`) + 42' % columns[0]
        ex2 = 'to_text(`%s`) || ", " || to_text(`%s`)' % (columns[0], columns[1])

        interaction(
            dedent("""
            Transform your InputSchema. The columns from your
            input file can be referenced in your expression. They are:

            {columns}

            You can reference these columns in the expressions you build in SoQL.
            Example expressions:

            {ex1}
            to add 42 to the column

            or

            {ex2}
            to concatenate two columns together

            So if we have a column called "foo" in our OutputSchema,
            and its transform is {ex1}, all of the data in the "foo" column
            will be the result of that expression being run on each row.

            You can:
            """).format(
                columns = ', '.join(columns),
                ex1 = ex1,
                ex2 = ex2
            ),
            [
                ('Return', back),
                ('Add a column', add_column(revision, output_schema)),
                ('Drop a column', drop_column(revision, output_schema)),
                ('Transform a column', transform_column_data(revision, output_schema)),
                ('Change a column\'s metadata', change_column_metadata(revision, output_schema)),
                ('Help', help_transform(revision, output_schema))
            ]
        )
    return run

def apply_revision(revision, output_schema):
    def run():
        (ok, job) = revision.apply(output_schema = output_schema)
        assert ok, job

        def progress(job):
            def s(l):
                if l['details']:
                    return l['stage'] + ' ' + str(l['details'])
                return l['stage']
            print(
                'I have done these things: ' + ', '.join(reversed([s(l) for l in job.attributes['log']]))
            )

        (ok, job) = job.wait_for_finish(progress = progress)
        assert ok, job

        (ok, view) = socrata.views.lookup(revision.attributes['fourfour'])
        assert ok, view

        def print_url():
            print(view.ui_url())

        interaction(
            """
            You have reached the end of your adventure, you can:
            """,
            [
                ('Open the view in a browser', browse(view)),
                ('View the view url', print_url)
            ]
        )

    return run

def use_output_schema(revision, output_schema):
    def run():
        interaction(
            dedent("""
            You have an OutputSchema with id = {id}. The columns are:

            {columns}

            An OutputSchema is staged data that can be applied via a Revision, to
            a View. An OutputSchema is how we validate data for errors,
            as well as transform it into new data. An OutputSchema comes from an InputSchema.
            An InputSchema is your data exactly as it appeared in your Source file. An OutputSchema
            is the result of Transforms being applied to your InputSchema.
            """).format(
                id = output_schema.attributes['id'],
                columns = ', '.join([oc['field_name'] for oc in output_schema.attributes['output_columns']])
            ),
            [
                ('Return', back),
                ('View errors of the output data', print_errors(output_schema)),
                ('View row counts in output data', print_row_counts(output_schema)),
                ('View a page of the data', print_data(output_schema)),
                ('View the output schema', print_output_schema(output_schema)),
                ('Do a transform: change the column data, metadata, or add and drop columns', transform_output_schema(revision, output_schema)),
                ('Apply this data to the view', apply_revision(revision, output_schema)),
                ('Open the revision in a browser, scroll down and click the "Preview Data" button to see the OutputSchema', browse(revision))
            ]
        )
    return run

def upload_csv(revision):
    def run():
        def get_file():
            files = 'files'
            examples = [join(files, f) for f in listdir(files) if isfile(join(files, f))]

            print("Examples:")
            for e in examples:
                print(e)

            path = prompt('Enter the file path')

            if not os.path.exists(path):
                print("That path doesn't exist!")
                return get_file()
            return path

        path = get_file()


        (ok, upload) = revision.create_upload(os.path.basename(path))
        assert ok, upload

        with open(path, 'rb') as file:
            (ok, upload) = upload.csv(file)
            assert ok, upload

            interaction(
                dedent("""
                You have successfully uploaded your file.
                """),
                [
                    ('Return', back),
                    ('Interact with the schema and data', use_output_schema(revision, upload.get_latest_input_schema().get_latest_output_schema()))
                ]
            )

    return run


def browse(thing):
    def run():
        thing.open_in_browser()
    return run

def create():
    name = prompt('Enter the dataset name')
    description = prompt('Enter the dataset description')
    (ok, revision) = socrata.new({
        'name': name,
        'description': description
    })

    interaction(
        dedent("""
        A Revision holds the changes to an existing dataset.
        When you load a Revision in the UI, like here

        {uri}

        you are looking at staged changes (of data, metadata, or both),
        that can be applied at some point in the future to the actual
        Socrata View. When the chages are applied, you will be able to
        query and make visualizations from the View.

        You have created your revision, what would you like to do?
        """.format(uri = revision.ui_url())),
        [
            ('Return', back),
            ('Upload a csv', upload_csv(revision)),
            ('Open the revision in a browser', browse(revision))
        ]
    )


setup_logging()
interaction(
    dedent("""
    You are in a dark room.

    There are no doors, but you do have internet access
    and a terminal. You can create things in Socrata from here.
    """),
    [
        ('Create a new dataset and revision', create)
    ]
)
