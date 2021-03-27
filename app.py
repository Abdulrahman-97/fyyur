#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import ( Flask, 
                    render_template, 
                    request, Response, 
                    flash, 
                    redirect, 
                    url_for)
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from models import db, Venue, Artist, Show

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app, db)


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
  if venues:
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
  # venue = db.session.query(Venue).filter(Venue.id == venue_id).first()
  venue = Venue.query.get_or_404(venue_id)
  print(venue.name)
  # get past shows and upcoming shows info
  past_shows = venue.get_past_shows()
  upcoming_shows = venue.get_upcoming_shows()
  

  past_shows_list = []
  for show in past_shows:
    past_shows_list.append({
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
    })
  upcoming_shows_list = []
  for show in upcoming_shows:
    upcoming_shows_list.append({
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
    })
  data={
    "id": venue_id,
    "name": venue.name,
    "genres": venue.genres,
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
  form = VenueForm(request.form, meta={'csrf': False})
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  error = False
  form = VenueForm(request.form, meta={'csrf': False})
  if form.validate():
    try:
      venue = Venue()
      form.populate_obj(venue)
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
  else:
    message = []
    for field, err in form.errors.items():
        message.append(field + ' ' + '|'.join(err))
    flash('Errors ' + str(message))

  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')


  

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  error = False
  try:
      venue = Venue.query.get_or_404(venue_id)
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
  artist = Artist.query.get_or_404(artist_id)
  # get past shows and upcoming shows info
  past_shows = artist.get_past_shows()
  upcoming_shows = artist.get_upcoming_shows()

  past_shows_list = []
  for show in past_shows:
    past_shows_list.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "venue_image_link": show.venue.image_link,
      "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
    })
  upcoming_shows_list = []
  for show in upcoming_shows:
    upcoming_shows_list.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "venue_image_link": show.venue.image_link,
      "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
        })
  data = {
    "id": artist_id,
    "name": artist.name,
    "genres": artist.genres,
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
  artist = Artist.query.get_or_404(artist_id)
  form = ArtistForm(obj=artist)
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  error = False
  form = ArtistForm(request.form, meta={'csrf': False})
  if form.validate():
    try:
      artist = Artist.query.get_or_404(artist_id)
      form.populate_obj(artist)
      db.session.commit()
    except:
      db.session.rollback()
      error = True
    finally:
      db.session.close()
      if error:
        # TODO: on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Artist ' + form.name.data + ' could not be edited.')
      else:
        # on successful db insert, flash success
        flash('Artist ' + form.name.data + ' was successfully edited!')
  else:
    message = []
    for field, err in form.errors.items():
        message.append(field + ' ' + '|'.join(err))
    flash('Errors ' + str(message))
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.get_or_404(venue_id)
  form = VenueForm(obj=venue)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new 
  error = False
  form = VenueForm(request.form, meta={'csrf': False})
  if form.validate():
    try:
      venue = Venue.query.get_or_404(venue_id)
      form.populate_obj(venue)
      db.session.commit()
    except:
      db.session.rollback()
      error = True
    finally:
      db.session.close()
      if error:
        # TODO: on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Venue ' + form.name.data + ' could not be edited.')
      else:
        # on successful db insert, flash success
        flash('Venue ' + form.name.data + ' was successfully edited!')
  else:
    message = []
    for field, err in form.errors.items():
        message.append(field + ' ' + '|'.join(err))
    flash('Errors ' + str(message))
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm(request.form)
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  error = False
  form = ArtistForm(request.form, meta={'csrf': False})
  if form.validate():
    try:
      artist = Artist()
      form.populate_obj(artist)
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
  else:
    message = []
    for field, err in form.errors.items():
        message.append(field + ' ' + '|'.join(err))
    flash('Errors ' + str(message))

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
      "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
    })
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm(request.form, meta={'csrf': False})
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  error = False
  form = ShowForm()
  try:
    show = Show()
    form.populate_obj(show)
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
