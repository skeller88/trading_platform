import os

# https://stackoverflow.com/questions/19972669/python-not-finding-module
# use __package__ attribute and sys.path modification in order to run locally without needing to create a deployment
# package

import sys
from pip._vendor.distlib.compat import raw_input


if __name__ == '__main__' and __package__ is None:
    __package__ = 'core'
    sys.path.append(os.getcwd())

from trading_platform.storage.setup_db import setup_local_sql_alchemy


sys.stdout.write('Are you sure you want to run this script? This will delete all existing data in the database. Type \"yes\" to run:    ')
choice = raw_input().lower()

if choice == 'yes':
    setup_local_sql_alchemy()