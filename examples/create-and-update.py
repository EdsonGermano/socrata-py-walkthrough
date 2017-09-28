from socrata.authorization import Authorization
from socrata import Socrata
import os
import uuid

auth = Authorization(
  "dsmp-nbe.test-socrata.com",
  os.environ['SOCRATA_USERNAME'],
  os.environ['SOCRATA_PASSWORD']
)

socrata = Socrata(auth)
# Just so you can run this script a lot and not have config name collisions
config_name = 'parking-config-%s' % str(uuid.uuid4())

# Create the dataset initially
with open('../files/parking.csv', 'rb') as file:
    (revision, output) = socrata.create(
        name = "parking"
    ).csv(file)

    print("Created", revision.ui_url())

    # Create a config fr updating in the future
    (ok, config) = output.build_config(config_name, 'replace')
    assert ok, config

    print("Created configuration", config_name)

    (ok, job) = revision.apply(output_schema = output)
    assert ok, job
    # Let's wait for the upsert to finish before opening a new revision
    job.wait_for_finish()



# Update step
(ok, view) = socrata.views.lookup(revision.view_id())
assert ok, view

with open('../files/parking-updated.csv', 'rb') as updated_file:
    (rev, job) = socrata.using_config(config_name, view).csv(updated_file)
    rev.open_in_browser()

