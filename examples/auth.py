import os
from socrata.authorization import Authorization

authorization = Authorization(
  'localhost',
  os.environ['SOCRATA_LOCAL_USER'],
  os.environ['SOCRATA_LOCAL_PASS']
)
authorization.live_dangerously()
