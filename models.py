#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
from config import * 

class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120),nullable=True)
    genres = db.Column(db.String)
    image_link = db.Column(db.String(500),nullable=True)
    facebook_link = db.Column(db.String(120),nullable=True)
    website_link = db.Column(db.String(120),nullable=True)
    talent=db.Column(db.Boolean,nullable=True)
    description = db.Column(db.String(500),nullable=True)
    show = db.relationship('Show',backref='venue',lazy=True)

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120),nullable=True)
    genres = db.Column(db.String(120))
    image = db.Column(db.String(500))
    facebook = db.Column(db.String(120),nullable=True)
    website = db.Column(db.String,nullable=True)
    venue = db.Column(db.Boolean,nullable=True)
    description = db.Column(db.String,nullable=True)
    shows = db.relationship('Show',backref='artist',lazy=True)

class Show(db.Model):
  __tablename__ = 'show'

  id = db.Column(db.Integer,primary_key=True)
  start_time = db.Column(db.DateTime,nullable=False)
  venue_id = db.Column(db.Integer,db.ForeignKey('venue.id'),nullable=False)
  artist_id = db.Column(db.Integer,db.ForeignKey('artist.id'),nullable=False)
