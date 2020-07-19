import os

# EMAIL
CONTACT_MAIL = os.environ['CONTACT_MAIL']
EMAIL = os.environ['EMAIL']
PASSWORD = os.environ['EMAIL_PASSWORD']

# BOT PLATFORM ACCOUNTS
STAKE_USERNAME = os.environ['STAKE_USERNAME']
STAKE_PASSWORD = os.environ['STAKE_PASSWORD']
STAKE_TOKEN = os.environ['STAKE_TOKEN']

# TWO FACTOR AUTHENTICATOR
import pyotp
TOTP = pyotp.TOTP(os.environ['STAKE_TFA'])

# SETTINGS
REGISTRATION_STATUS = os.environ['REGISTRATION_STATUS']
SECRET_KEY = os.environ['SECRET_KEY']

# PROFILE
LEVEL_TITLES = {
'Newbie': (0, 100),
'Novice': (100, 200),
'Initiate': (201, 750),
'Adept': (751, 1000),
'Member': (1001, 2500),
'Master': (2501, 5000),
'Chief': (10001, 50000),
'Veteran': (50001, 100000),
'VIP': (100001, 1500000),
'Lord': (1500001, float("inf"))
}

# AMAZON WEB SERVICES
AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
AWS_STORAGE_BUCKET_NAME = os.environ['AWS_STORAGE_BUCKET_NAME']

# HOSTS
HOSTS = os.environ['ALLOWED_HOSTS'].split(",")