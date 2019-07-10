import os
from smart_getenv import getenv

instance_dir = os.path.abspath(os.path.dirname(__file__))

SECRET_KEY = getenv('SECRET_KEY', default='')

DEBUG = getenv('DEBUG', type=bool, default=False)

SQLALCHEMY_DATABASE_URI = '{schema}://{user}:{pwd}@{host}/{dbname}'.format(
  schema=getenv('DATABASE_SCHEMA', default='sqlite'),
  user=getenv('MYSQL_USER', default=''),
  pwd=getenv('MYSQL_PASSWORD', default=''),
  host=getenv('DATABASE_HOST', default=''),
  dbname=getenv('MYSQL_DATABASE', default=''))

WHOOSH_BASE = os.path.join(
    os.path.abspath(os.path.dirname(os.path.dirname(__file__))),
    'whoosh_index'
)

FILES_DIR = os.path.join(instance_dir, 'files')

SERVER_NAME = getenv('SERVER_NAME', default='localhost')

# email server
MAIL_SERVER = getenv('MAIL_SERVER', default='')
MAIL_PORT = getenv('MAIL_PORT')
MAIL_USE_TLS = getenv('MAIL_USE_TLS', type=bool, default=False)
MAIL_USE_SSL = getenv('MAIL_USE_SSL', type=bool, default=False)
MAIL_USERNAME = getenv('MAIL_USERNAME', default='')
MAIL_PASSWORD = getenv('MAIL_PASSWORD', default='')

NOTIFY_EMAILS = getenv('NOTIFY_EMAILS', default='').split(',')

# UNSPSCs codes
UNSPSC_CODES = getenv('UNSPSC_CODES', default='').split(',')

USERNAME = getenv('USERNAME', default='')
PASSWORD = getenv('PASSWORD', default='')


TED_USERNAME = getenv('TED_USERNAME', default='')
TED_PASSWORD = getenv('TED_PASSWORD', default='')

CPV_CODES = getenv('CPV_CODES', default='').split(',')


# at first run, TED worker will download notices more recent than
# current_date - TED_DAY_AGO (by default 30 days)
TED_DAYS_AGO = getenv('TED_DAYS_AGO', type=int, default=30)

TED_COUNTRIES = getenv('TED_COUNTRIES', default='').split(',')
TED_DOC_TYPES = getenv('TED_DOC_TYPES', default='').split(',')
TED_AUTH_TYPE = getenv('TED_AUTH_TYPE', default='')

DISABLE_UNGM_DOWNLOAD = getenv('DISABLE_UNGM_DOWNLOAD', type=bool, default=False)

# Set this as the maximum number of tries scraper will attempt to get data from
# UNGM.
MAX_UNGM_REQUESTS = getenv('MAX_UNGM_REQUESTS', type=int, default=3)

# Set this as being a list representing a sequence of number of days.
# If, for example, 3 is in that list, mail alerts are sent to mail when
# there are 3 or less days remaining until deadline for each favourite tender is
# achieved.
DEADLINE_NOTIFICATIONS = getenv('DEADLINE_NOTIFICATIONS', default='').split(',')

