#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import sys
import dateutil.parser
import babel
from flask import Flask, jsonify, render_template, request, flash, redirect, url_for, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler

from sqlalchemy import JSON
from forms import *
from flask_migrate import Migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)


# TODO: connect to a local postgresql database
migrate = Migrate(app,db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

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

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  if isinstance(value,str):
    date = dateutil.parser.parse(value)
  else:
    date = value
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  venues = []
  cities = db.session.query(Venue.city,Venue.state)
  for city in cities:
    venue = db.session.query(Venue).filter_by(city=city.city,state=city.state)
    print(venue)
    for venue in venue:
      # upcoming_shows_count = db.session.query(Show).filter_by(venue_id=venue.id).count()
      venues.append({
        'city':city.city,
        'state':city.state,
        "venues":[{
          'id':venue.id,
          'name':venue.name,
          'num_upcoming_shows':db.session.query(Show).filter_by(venue_id=venue.id).count()
        }]
      })    
  return render_template('pages/venues.html', areas=venues)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  venue = db.session.query(Venue).filter(Venue.name.ilike('%' + request.form.get('search_term') + '%')).all()
  response = {
        "count": len(venue),
        "data": venue
    }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  
  venue = Artist.query.get(venue_id)
  now = datetime.now()
  data = venue.__dict__
  shows = db.session.query(Show).filter_by(venue_id=venue_id)
  past_shows = shows.filter(Show.start_time < now).all()
  upcoming_shows =  shows.filter(Show.start_time >= now).all()
  upcoming_shows_count = len(upcoming_shows)
  past_shows_count = len(past_shows)
  # print(past_shows)
  data['past_shows'] = past_shows
  data['upcoming_shows'] = upcoming_shows
  data['upcoming_shows_count']= upcoming_shows_count
  data['past_shows_count'] = past_shows_count  
  
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST','GET'])
def create_venue_submission():
  error= False
  try:
    name = request.form['name']
    city= request.form['city']
    state = request.form['state']
    address = request.form['address']
    phone = request.form['phone']
    genres = request.form['genres']
    image_link = request.form['image_link']
    facebook_link = request.form['facebook_link']
    website_link = request.form['website_link']
    talent = request.form['seeking_talent']
    description = request.form['seeking_description']
    if talent == 'y':
      talent = True
    else:
      talent = False
    venue_data = Venue(name=name,city=city,state=state,address=address,phone=phone,genres=genres,image_link=image_link,facebook_link=facebook_link,website_link=website_link,talent=talent,description=description)
    print(venue_data.name)
    db.session.add(venue_data)
    db.session.commit()
    # on successful db insert, flash success
    flash('Venue ' + venue_data.name + ' was successfully listed!')
  except:
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()  
  if error:
    flash('An error occurred. Venue could not be listed.')
  else:
    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  error = False
  venue = Venue.query.get(venue_id)

  if venue is None:
    abort(400)
  try:
    db.session.delete(venue)
    db.session.commit()
    flash('Venue deleted successfully!')
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
    flash('Error occurred: Venue could not be deleted.')
  finally:
    db.session.close()

  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data = Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  response={
    "count": 1,
    "data": [{
      "id": 4,
      "name": "Guns N Petals",
      "num_upcoming_shows": 0,
    }]
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  artist = Artist.query.get(artist_id)
  now = datetime.now()
  data = artist.__dict__
  shows = db.session.query(Show).filter_by(artist_id=artist_id)
  past_shows = shows.filter(Show.start_time < now).all()
  upcoming_shows =  shows.filter(Show.start_time >= now).all()
  upcoming_shows_count = len(upcoming_shows)
  past_shows_count = len(past_shows)
  # print(past_shows)
  data['past_shows'] = past_shows
  data['upcoming_shows'] = upcoming_shows
  data['upcoming_shows_count']= upcoming_shows_count
  data['past_shows_count'] = past_shows_count

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  error = False
  try:
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    phone = request.form['phone']
    image = request.form['image_link']
    genres = request.form['genres']
    facebook = request.form['facebook_link']
    website = request.form['website_link']
    venue = request.form.get('seeking_venue')
    description = request.form['seeking_description']
    if venue == 'y':
      venue = True
    else:
      venue = False
    artist_data = Artist(name=name,city=city,state=state,phone=phone,genres=genres,image=image,facebook=facebook,website=website,description=description,venue=venue)
    print(artist_data)
    db.session.add(artist_data)
    db.session.commit()
    flash('Artist ' + artist_data.name + ' was successfully listed!')
  except:
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Artist ' + artist_data.name + ' could not be listed.')
  else:
  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  now = datetime.now()
  data = []
  shows =Show.query.all()
  for show in shows:
    artist = Artist.query.get(show.artist_id)
    venue = Venue.query.get(show.venue_id)
    if show.start_time > now:
      data.append({
        'venue_id':show.venue_id,
        'artist_id':show.artist_id,
        'start_time':show.start_time,
        'artist_name':artist.name,
        'artist_image_link':artist.image,
        'venue_name':venue.name
      })

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()

  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  # on successful db insert, flash success
  try:
    artist = request.form['artist_id']
    venue = request.form['venue_id']
    date = request.form['start_time']
    show_data = Show(artist_id=artist,venue_id=venue,start_time=date)
    print(show_data)
    db.session.add(show_data)
    db.session.commit()
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
  app.debug = True
  app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
