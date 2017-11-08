from socrata.authorization import Authorization
from socrata import Socrata
import os

auth = Authorization(
  "data.transportation.gov",
  os.environ['SOCRATA_USERNAME'],
  os.environ['SOCRATA_PASSWORD']
)

with open('/home/chris/Downloads/1000.csv', 'rb') as file:
  (revision, output) = Socrata(auth).create(
      name = "usdot",
      description = "a description"
  ).csv(file)


  (ok, output) = output\
      .change_column_metadata('coredata_position', 'field_name').to('coredata_position_lat')\
      .change_column_metadata('coredata_position_1', 'field_name').to('coredata_position_long')\
      .add_column('coredata_point', 'CoreData Point', 'make_point(to_number(coredata_position), to_number(coredata_position_1))', 'this is a point column')\
      .run()

  assert ok, output

  revision.open_in_browser()
