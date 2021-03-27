import os
from decouple import config
SECRET_KEY = os.urandom(32)
USERNAME = config('USER')
KEY = config('KEY')
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True


# TODO IMPLEMENT DATABASE URL
SQLALCHEMY_DATABASE_URI = f'postgresql://{USERNAME}:{KEY}@127.0.0.1:5432/fyyur'
SQLALCHEMY_TRACK_MODIFICATIONS = False

