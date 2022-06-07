import os

SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True


# Connect to the database
SQLALCHEMY_DATABASE_URI='postgresql://mwiks-dev:1455@localhost/fyurr'
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Imports
#----------------------------------------------------------------------------#

import sys
import dateutil.parser
import babel
from flask import Flask,render_template, request, flash, redirect, url_for, abort
import logging
from logging import Formatter, FileHandler
from forms import *
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_moment import Moment
from flask import Flask

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

