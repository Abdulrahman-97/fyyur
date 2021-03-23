#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)
# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
current_date =  datetime.now().strftime('%Y-%m-%d %H:%S:%M') # get current time
class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_desc = db.Column(db.String(500))
    shows = db.relationship('Show', backref='venue', lazy=True)

    
    def get_past_shows(self):
      past_shows = []
      for show in self.shows:
        if show.start_time <= current_date:
          past_shows.append(show)
      return past_shows
    
    def get_upcoming_shows(self):
      upcoming_shows = []
      for show in self.shows:
        if show.start_time > current_date:
          upcoming_shows.append(show)
      return upcoming_shows
    
    def get_shows(self):
      return self.shows

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_desc = db.Column(db.String(500))
    shows = db.relationship('Show', backref='artist', lazy=True)

    def get_past_shows(self):
      past_shows = []
      for show in self.shows:
        if show.start_time <= current_date:
          past_shows.append(show)
      return past_shows
    
    def get_upcoming_shows(self):
      upcoming_shows = []
      for show in self.shows:
        if show.start_time > current_date:
          upcoming_shows.append(show)
      return upcoming_shows
    
    def get_shows(self):
      return self.shows

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Show(db.Model):
  __tablename__ = 'Show'
  id = db.Column(db.Integer, primary_key=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
  start_time = db.Column(db.String(120), nullable=False)

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

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
  data = []
  # query venues ordered by city ascending
  venues = db.session.query(Venue).order_by(Venue.city.asc()).all()

  city = venues[0].city # first city
  state = venues[0].state # first state
  venues_list = []
  for venue in venues:
    if city != venue.city: # if city is changed, add all related venues to city_dic, then appeand to data
      city_dic = {
        'city': city,
        'state': state,
        'venues': venues_list
      }
      data.append(city_dic)
      city = venue.city
      state = venue.state
      venues_list = []
    # get the number of upcoming shows for venue
    num_upcoming_shows = len(venue.get_upcoming_shows())
    venue_dic = {
      'id': venue.id,
      'name': venue.name,
      'num_upcoming_shows': num_upcoming_shows
    }
    # appeand venue_dic to the list of venues
    venues_list.append(venue_dic)
  ## appeand the last element to data list
  data.append({
    'city': city,
    'state': state,
    'venues': venues_list
  })
  
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # get search term provided by user
  search_term = request.form.get('search_term', '')
  # query venues that include the search_term using ilike which supports case-insensitive filtering
  venues = db.session.query(Venue).filter(Venue.name.ilike(f'%{search_term}%')).all()
  data = []
  for venue in venues:
    num_upcoming_shows = venue.get_upcoming_shows()
    data.append({
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows": num_upcoming_shows,
    })
  response={
    "count": len(venues),
    "data": data
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # query venue information
  venue = db.session.query(Venue).filter(Venue.id == venue_id).first()
  # get past shows and upcoming shows info
  past_shows = venue.get_past_shows()
  upcoming_shows = venue.get_upcoming_shows()
  

  past_shows_list = []
  for show in past_shows:
    past_shows_list.append({
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": show.start_time
    })
  upcoming_shows_list = []
  for show in upcoming_shows:
    upcoming_shows_list.append({
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": show.start_time
    })
  data={
    "id": venue_id,
    "name": venue.name,
    "genres": venue.genres.translate({ord(i): None for i in '}{'}).split(','),
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_desc,
    "image_link": venue.image_link,
    "past_shows": past_shows_list,
    "upcoming_shows": upcoming_shows_list,
    "past_shows_count": len(past_shows_list),
    "upcoming_shows_count": len(upcoming_shows_list),
  }
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  error = False
  form = VenueForm()
  try:
    venue = Venue(
      name=form['name'].data,
      city=form['city'].data,
      state=form['state'].data,
      address=form['address'].data,
      phone=form['phone'].data,
      image_link=form['image_link'].data,
      facebook_link=form['facebook_link'].data,
      genres=form['genres'].data,
      website=form['website'].data,
      seeking_talent=form['seeking_talent'].data,
      seeking_desc=form['seeking_desc'].data
    )
    db.session.add(venue)
    db.session.commit()
  except:
    db.session.rollback()
    error = True
  finally:
    db.session.close()
    if error:
      # TODO: on unsuccessful db insert, flash an error instead.
      flash('An error occurred. Venue ' + form['name'].data + ' could not be listed.')
    else:
      # on successful db insert, flash success
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')


  

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  error = False
  try:
      venue = Venue.query.get(venue_id)
      db.session.delete(venue)
      db.session.commit()
  except:
      db.session.rollback()
      error = True
  finally:
      db.session.close()
  if error:
      flash(f'An error occurred. Venue {venue.name} could not be deleted.')
  else:
      flash(f'Venue {venue.name} was successfully deleted!')
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return redirect(url_for('index'), code=200)

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  artists = db.session.query(Artist.id, Artist.name).all()
  data = []
  for artist in artists:
    data.append({
      "id": artist[0],
      "name": artist[1]
    })
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # get search term provided by user
  search_term = request.form.get('search_term', '')
  # query artists that include the search_term using ilike which supports case-insensitive filtering
  artists = db.session.query(Artist).filter(Artist.name.ilike(f'%{search_term}%')).all()
  data = []
  for artist in artists:
    num_upcoming_shows = len(artist.get_upcoming_shows())
    data.append({
      "id": artist.id,
      "name": artist.name,
      "num_upcoming_shows": num_upcoming_shows,
    })
  response={
    "count": len(artists),
    "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # query artist information
  artist = db.session.query(Artist).filter(Artist.id == artist_id).first()
  # get past shows and upcoming shows info
  past_shows = artist.get_past_shows()
  upcoming_shows = artist.get_upcoming_shows()

  past_shows_list = []
  for show in past_shows:
    past_shows_list.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "venue_image_link": show.venue.image_link,
      "start_time": show.start_time
    })
  upcoming_shows_list = []
  for show in upcoming_shows:
    upcoming_shows_list.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "venue_image_link": show.venue.image_link,
      "start_time": show.start_time
        })
  data = {
    "id": artist_id,
    "name": artist.name,
    "genres": artist.genres.translate({ord(i): None for i in '}{'}).split(','),
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_desc,
    "image_link": artist.image_link,
    "past_shows": past_shows_list,
    "upcoming_shows": upcoming_shows_list,
    "past_shows_count": len(past_shows_list),
    "upcoming_shows_count": len(upcoming_shows_list),
  }
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  print(artist)
  if artist:
    form.name.data = artist.name
    form.city.data = artist.city
    form.state.data = artist.state
    form.phone.data = artist.phone
    form.genres.data = artist.genres
    form.facebook_link.data = artist.facebook_link
    form.image_link.data = artist.image_link
    form.website.data = artist.website
    form.seeking_venue.data = artist.seeking_venue
    form.seeking_desc.data = artist.seeking_desc
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  error = False
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  try:
    artist.name = form.name.data 
    artist.city = form.city.data 
    artist.state = form.state.data
    artist.phone = form.phone.data 
    artist.genres = form.genres.data
    artist.facebook_link = form.facebook_link.data
    artist.image_link = form.image_link.data
    artist.website = form.website.data
    artist.seeking_venue = form.seeking_venue.data
    artist.seeking_desc = form.seeking_desc.data

    db.session.commit()
  except:
    db.session.rollback()
    error = True
  finally:
    db.session.close()
    if error:
      # TODO: on unsuccessful db insert, flash an error instead.
      flash('An error occurred. Artist ' + form['name'].data + ' could not be edited.')
    else:
      # on successful db insert, flash success
      flash('Artist ' + form['name'].data + ' was successfully edited!')
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  if venue:
    form.name.data = venue.name
    form.city.data = venue.city
    form.state.data = venue.state
    form.address.data = venue.address
    form.phone.data = venue.phone
    form.genres.data = venue.genres
    form.facebook_link.data = venue.facebook_link
    form.image_link.data = venue.image_link
    form.website.data = venue.website
    form.seeking_talent.data = venue.seeking_talent
    form.seeking_desc.data = venue.seeking_desc
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new 
  error = False
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  try:
    venue.name = form.name.data 
    venue.city = form.city.data 
    venue.state = form.state.data
    venue.address = form.address.data
    venue.phone = form.phone.data 
    venue.genres = form.genres.data
    venue.facebook_link = form.facebook_link.data
    venue.image_link = form.image_link.data
    venue.website = form.website.data
    venue.seeking_talent = form.seeking_talent.data
    venue.seeking_desc = form.seeking_desc.data

    db.session.commit()
  except:
    db.session.rollback()
    error = True
  finally:
    db.session.close()
    if error:
      # TODO: on unsuccessful db insert, flash an error instead.
      flash('An error occurred. Venue ' + form['name'].data + ' could not be edited.')
    else:
      # on successful db insert, flash success
      flash('Venue ' + form['name'].data + ' was successfully edited!')
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
  form = ArtistForm()
  try:
    artist = Artist(
      name=form['name'].data,
      city=form['city'].data,
      state=form['state'].data,
      phone=form['phone'].data,
      image_link=form['image_link'].data,
      facebook_link=form['facebook_link'].data,
      genres=form['genres'].data,
      website=form['website'].data,
      seeking_venue=form['seeking_venue'].data,
      seeking_desc=form['seeking_desc'].data,
    )
    db.session.add(artist)
    db.session.commit()
  except:
    db.session.rollback()
    error = True
  finally:
    db.session.close()
    if error:
      # TODO: on unsuccessful db insert, flash an error instead.
      flash('An error occurred. Artist ' + form['name'].data + ' could not be listed.')
    else:
      # on successful db insert, flash success
      flash('Artist ' + form['name'].data + ' was successfully listed!')

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # query shows information 
  shows = Show.query.all()
  data = []
  for show in shows:
    data.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": show.start_time
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
  error = False
  form = ShowForm()
  try:
    show = Show(
      artist_id=form.artist_id.data,
      venue_id=form.venue_id.data,
      start_time=form.start_time.data
    )
    db.session.add(show)
    db.session.commit()
  except:
    db.session.rollback()
    error = True
  finally:
    db.session.close()
    if error:
      # TODO: on unsuccessful db insert, flash an error instead.
      flash('An error occurred. Show could not be listed.')
    else:
      # on successful db insert, flash success
      flash('Show was successfully listed!')

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
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
