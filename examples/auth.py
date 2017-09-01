import os
from socrata.authorization import Authorization

authorization = Authorization(
  'chris.test-socrata.com',
  os.environ['SOCRATA_USERNAME'],
  os.environ['SOCRATA_PASSWORD']
)
