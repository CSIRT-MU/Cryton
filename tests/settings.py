from cryton.hive.settings import *

DATABASES["default"] = {"ENGINE": "django.db.backends.sqlite3", "NAME": "cryton", "OPTIONS": {"timeout": 30}}
