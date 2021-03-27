from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
db = SQLAlchemy()


class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_desc = db.Column(db.String(500))
    shows = db.relationship('Show', backref='venue', 
                            cascade="all, delete-orphan" , lazy='joined')

    def get_past_shows(self):
      past_shows = []
      for show in self.shows:
        if show.start_time <= datetime.now():
          past_shows.append(show)
      return past_shows
    
    def get_upcoming_shows(self):
      upcoming_shows = []
      for show in self.shows:
        if show.start_time > datetime.now():
          upcoming_shows.append(show)
      return upcoming_shows

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_desc = db.Column(db.String(500))
    shows = db.relationship('Show', backref='artist',
                            cascade="all, delete-orphan" , lazy='joined')

    def get_past_shows(self):
      past_shows = []
      for show in self.shows:
        if show.start_time <= datetime.now():
          past_shows.append(show)
      return past_shows
    
    def get_upcoming_shows(self):
      upcoming_shows = []
      for show in self.shows:
        if show.start_time > datetime.now():
          upcoming_shows.append(show)
      return upcoming_shows

class Show(db.Model):
  __tablename__ = 'show'
  id = db.Column(db.Integer, primary_key=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)
  start_time = db.Column(db.DateTime, nullable=False)