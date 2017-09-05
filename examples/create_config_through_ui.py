from examples.auth import authorization
from socrata import Socrata
import gntp.notifier

socrata = Socrata(authorization)

with open('files/Permits.csv', 'rb') as file:
    # Let's make a socrata view, open a revision on it, and then
    # upload and validate our data
    (revision, output_schema) = socrata.create(
        name = "using a config",
        description = "~~my first dataset~~"
    ).csv(file)

    (ok, output_schema) = output_schema.wait_for_finish()
    assert ok, output_schema


    revision.open_in_browser()

    print("Click on the 'Review Data' button to view the output schema")

    print("Then click on the Address column's dropdown and click 'Use as georeference', and add a geocoded column")

    print("Maybe you also want to change types of columns")

    _ = input("Click 'Save' in the UI and then hit enter to continue\n>>> ")

    # Get the output schema that is currently set
    (ok, output_schema) = revision.get_output_schema()
    assert ok, output_schema

    name = input("What would you like to name this config?\n>>>")

    (ok, config) = output_schema.build_config(name, "update")
    assert ok, config
    print("Config created")
    print("Look at the 'columns' attribute, Notice how the transformations you built through the UI are saved in this config:\n")

    print(config)

    # Now you could carry on from this point in the docs
    # https://github.com/socrata/socrata-py#using_config
    # You might look up the view by doing...
    #
    # (ok, view) = socrata.views.lookup(revision.attributes['fourfour'])
    #
