import os

SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))


# Connect to the database
SQLALCHEMY_DATABASE_URI = 'postgresql://mwiks-dev:1455@localhost/fyurr'
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Enable debug mode.
DEBUG = True

