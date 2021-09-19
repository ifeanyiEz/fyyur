#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
from os import name
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import backref
import logging
from logging import Formatter, FileHandler, error
from flask_wtf import Form
from flask_migrate import Migrate
from forms import *
import sys

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database

migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

# TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

Show = db.Table('shows',
  db.Column('id', db.Integer, primary_key=True),
  db.Column('artist_id', db.Integer, db.ForeignKey('artist.id'), nullable=False),
  db.Column('venue_id', db.Integer, db.ForeignKey('venue.id'), nullable=False),
  db.Column('start_time', db.DateTime),
)


class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String(120)), nullable=False)
    facebook_link = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    website_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(500))
    artists = db.relationship('Artist', secondary=Show,
                              backref=db.backref('venue', lazy=True))

    def __repr__(self):
        return 'Venue {} {} {} {} {} {} {} {} {} {} {} {}'.format(self.id, self.name, self.city, self.state, self.address, self.phone, self.genres, self.facebook_link, self.image_link, self.website_link, self.seeking_talent, self.seeking_description)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate


class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String(120)), nullable=False)
    facebook_link = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    website_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(500))

    def __repr__(self):
      return 'Artist {} {} {} {} {} {} {} {} {} {} {}'.format(self.id, self.name, self.city, self.state, self.phone, self.genres, self.facebook_link, self.image_link, self.website_link, self.seeking_venue, self.seeking_description)


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
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
  # COMPLETE: replace with real venues data.
  # num_shows should be aggregated based on number of upcoming shows per venue.

  data = []

  places = db.session.query(Venue.city, Venue.state).distinct(Venue.city, Venue.state).order_by(Venue.state).all()
  city_venues = db.session.query(Venue.id, Venue.name, Venue.city, Venue.state).all()
  for place in places:
    place_data = {
      "city": place.city,
      "state": place.state,
      "venues": []
    }
    data.append(place_data)
  for place_set in data:
    for city_venue in city_venues:
      location = {}
      if city_venue.city == place_set.get("city"):
        location["id"] = city_venue.id
        location["name"] = city_venue.name
        place_set["venues"].append(location)
  
# data=[{
#  "city": "San Francisco",
#  "state": "CA",
#  "venues": [{
#    "id": 1,
#    "name": "The Musical Hop",
#    "num_upcoming_shows": 0,
#  }, {
#    "id": 3,
#    "name": "Park Square Live Music & Coffee",
#    "num_upcoming_shows": 1,
#  }]
# }, {
#  "city": "New York",
#  "state": "NY",
#  "venues": [{
#    "id": 2,
#    "name": "The Dueling Pianos Bar",
#    "num_upcoming_shows": 0,
#  }]
# }]

  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  response={
    "count": 1,
    "data": [{
      "id": 2,
      "name": "The Dueling Pianos Bar",
      "num_upcoming_shows": 0,
    }]
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # COMPLETE: replace with real venue data from the venues table, using venue_id
  
  past_shows = []
  upcoming_shows = []
  data = {}

  venue = Venue.query.get_or_404(venue_id)

  venue_past_shows = db.session.query(Show).join(Venue).filter((Show.c.venue_id == venue_id) & (Show.c.start_time <= datetime.now())).all()
  for past_show in venue_past_shows:
    past_show_artists = db.session.query(Artist).join(Show).filter(Artist.id == past_show.artist_id).all()
    for past_show_artist in past_show_artists:
      past_shows.append({
          'artist_id': past_show.artist_id,
          'artist_name': past_show_artist.name,
          'artist_image_link': past_show_artist.image_link,
          'start_time': past_show.start_time.strftime("%m/%d/%Y, %H:%M")
      })

  venue_upcoming_shows = db.session.query(Show).join(Venue).filter((Show.c.venue_id == venue_id) & (Show.c.start_time > datetime.now())).all()
  for upcoming_show in venue_upcoming_shows:
    upcoming_show_artists = db.session.query(Artist).join(Show).filter(Artist.id == upcoming_show.artist_id).all()
    for upcoming_show_artist in upcoming_show_artists:
      upcoming_shows.append({
          'artist_id': upcoming_show.artist_id,
          'artist_name': upcoming_show_artist.name,
          'artist_image_link': upcoming_show_artist.image_link,
          'start_time': upcoming_show.start_time.strftime("%m/%d/%Y, %H:%M")
      })

  data['id'] = venue.id
  data['name'] = venue.name
  data['genres'] = venue.genres
  data['address'] = venue.address
  data['city'] = venue.city
  data['state'] = venue.state
  data['phone'] = venue.phone
  data['website'] = venue.website_link
  data['facebook_link'] = venue.facebook_link
  data['seeking_talent'] = venue.seeking_talent
  data['seeking_description'] = venue.seeking_description
  data['image_link'] = venue.image_link
  data['past_shows'] = past_shows
  data['upcoming_shows'] = upcoming_shows
  data['past_shows_count'] = len(past_shows)
  data['upcoming_shows_count'] = len(upcoming_shows)

  #data1={
  #  "id": 1,
  # "name": "The Musical Hop",
  # "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
  #  "address": "1015 Folsom Street",
  #  "city": "San Francisco",
  #  "state": "CA",
  #  "phone": "123-123-1234",
  #  "website": "https://www.themusicalhop.com",
  #  "facebook_link": "https://www.facebook.com/TheMusicalHop",
  #  "seeking_talent": True,
  #  "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
  #  "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #  "past_shows": [{
  #    "artist_id": 4,
  #    "artist_name": "Guns N Petals",
  #    "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #    "start_time": "2019-05-21T21:30:00.000Z"
  #  }],
  #  "upcoming_shows": [],
  #  "past_shows_count": 1,
  #  "upcoming_shows_count": 0,
  #}

  #data2={
  #  "id": 2,
  #  "name": "The Dueling Pianos Bar",
  #  "genres": ["Classical", "R&B", "Hip-Hop"],
  #  "address": "335 Delancey Street",
  #  "city": "New York",
  #  "state": "NY",
  #  "phone": "914-003-1132",
  #  "website": "https://www.theduelingpianos.com",
  #  "facebook_link": "https://www.facebook.com/theduelingpianos",
  #  "seeking_talent": False,
  #  "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
  #  "past_shows": [],
  #  "upcoming_shows": [],
  #  "past_shows_count": 0,
  #  "upcoming_shows_count": 0,
  #}
  #data3={
  #  "id": 3,
  #  "name": "Park Square Live Music & Coffee",
  #  "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
  #  "address": "34 Whiskey Moore Ave",
  #  "city": "San Francisco",
  #  "state": "CA",
  #  "phone": "415-000-1234",
  #  "website": "https://www.parksquarelivemusicandcoffee.com",
  #  "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
  #  "seeking_talent": False,
  #  "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #  "past_shows": [{
  #    "artist_id": 5,
  #    "artist_name": "Matt Quevedo",
  #    "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #    "start_time": "2019-06-15T23:00:00.000Z"
  #  }],
  #  "upcoming_shows": [{
  #    "artist_id": 6,
  #    "artist_name": "The Wild Sax Band",
  #    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #    "start_time": "2035-04-01T20:00:00.000Z"
  #  }, {
  #    "artist_id": 6,
  #    "artist_name": "The Wild Sax Band",
  #    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #    "start_time": "2035-04-08T20:00:00.000Z"
  #  }, {
  #    "artist_id": 6,
  #    "artist_name": "The Wild Sax Band",
  #    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #    "start_time": "2035-04-15T20:00:00.000Z"
  #  }],
  #  "past_shows_count": 1,
  #  "upcoming_shows_count": 1,
  #}
  #data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[1]
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
# COMPLETE: insert form data as a new Venue record in the db, instead
  form = VenueForm(request.form)
  error = False
  try:
    name = form.name.data
    city = form.city.data
    state = form.state.data
    address = form.address.data
    phone = form.phone.data
    image_link = form.image_link.data
    genres = form.genres.data
    facebook_link = form.facebook_link.data
    website_link = form.website_link.data
    seeking_talent = form.seeking_talent.data
    seeking_description = form.seeking_description.data
    venue = Venue(name = name, city = city, state = state, address = address, phone = phone, image_link = image_link, genres = genres, facebook_link = facebook_link, website_link = website_link, seeking_talent = seeking_talent, seeking_description = seeking_description)
    print(venue)
    db.session.add(venue)
    db.session.commit()
# on successful db insert, flash success
    flash('Venue ' + form.name.data + ' was successfully listed!')
# COMPLETE: modify data to be the data object returned from db insertion
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
# COMPLETE: on unsuccessful db insert, flash an error instead.
# e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
# see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    flash('An error occurred. Venue ' + form.name.data + ' could not be listed.')
  finally:
    db.session.close
  if error:
    abort (400)
  else:
    #return jsonify(body)
    return render_template('pages/home.html')

#  Delete Venue
#  ----------------------------------------------------------------

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    Venue.query.filter_by(venue_id).delete()
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  #return None
  return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # COMPLETE: replace with real data returned from querying the database
  data = []
  bands = Artist.query.order_by(Artist.id).all()
  for artist in bands:
    data.append({
      "id": artist.id,
      "name": artist.name
    })

  #data=[{
  #  "id": 4,
  #  "name": "Guns N Petals",
  #}, {
  #  "id": 5,
  #  "name": "Matt Quevedo",
  #}, {
  #  "id": 6,
  #  "name": "The Wild Sax Band",
  #}]
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
  # COMPLETE: replace with real artist data from the artist table, using artist_id
  data = {}
  past_shows = []
  upcoming_shows = []

  artist = Artist.query.get_or_404(artist_id)

  artist_past_shows = db.session.query(Show).join(Artist).filter((Show.c.artist_id == artist_id) & (Show.c.start_time <= datetime.now())).all()
  for past_show in artist_past_shows:
    past_show_venues = db.session.query(Venue).join(Show).filter(Venue.id == past_show.venue_id).all()
    for past_show_venue in past_show_venues:
      past_shows.append({
          'venue_id': past_show.venue_id,
          'venue_name': past_show_venue.name,
          'venue_image_link': past_show_venue.image_link,
          'start_time': past_show.start_time.strftime("%m/%d/%Y, %H:%M")
      })

  artist_upcoming_shows = db.session.query(Show).join(Artist).filter((Show.c.artist_id == artist_id) & (Show.c.start_time > datetime.now())).all()
  for upcoming_show in artist_upcoming_shows:
    upcoming_show_venues = db.session.query(Venue).join(Show).filter(Venue.id == upcoming_show.venue_id).all()
    for upcoming_show_venue in upcoming_show_venues:
      upcoming_shows.append({
          'venue_id': upcoming_show.venue_id,
          'venue_name': upcoming_show_venue.name,
          'venue_image_link': upcoming_show_venue.image_link,
          'start_time': upcoming_show.start_time.strftime("%m/%d/%Y, %H:%M")
      })
  
  data['id'] = artist.id
  data['name'] = artist.name
  data['genres'] = artist.genres
  data['city'] = artist.city
  data['state'] = artist.state
  data['phone'] = artist.phone
  data['website'] = artist.website_link
  data['facebook_link'] = artist.facebook_link
  data['seeking_venue'] = artist.seeking_venue
  data['seeking_description'] = artist.seeking_description
  data['image_link'] = artist.image_link
  data['past_shows'] = past_shows
  data['upcoming_shows'] = upcoming_shows
  data['past_shows_count'] = len(past_shows)
  data['upcoming_shows_count'] = len(upcoming_shows)

  #data1={
  #  "id": 4,
  #  "name": "Guns N Petals",
  #  "genres": ["Rock n Roll"],
  #  "city": "San Francisco",
  #  "state": "CA",
  #  "phone": "326-123-5000",
  #  "website": "https://www.gunsnpetalsband.com",
  #  "facebook_link": "https://www.facebook.com/GunsNPetals",
  #  "seeking_venue": True,
  #  "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #  "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #  "past_shows": [{
  #    "venue_id": 1,
  #    "venue_name": "The Musical Hop",
  #    "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #    "start_time": "2019-05-21T21:30:00.000Z"
  #  }],
  #  "upcoming_shows": [],
  #  "past_shows_count": 1,
  #  "upcoming_shows_count": 0,
  #}
  #data2={
  #  "id": 5,
  #  "name": "Matt Quevedo",
  #  "genres": ["Jazz"],
  #  "city": "New York",
  #  "state": "NY",
  #  "phone": "300-400-5000",
  #  "facebook_link": "https://www.facebook.com/mattquevedo923251523",
  #  "seeking_venue": False,
  #  "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #  "past_shows": [{
  #    "venue_id": 3,
  #    "venue_name": "Park Square Live Music & Coffee",
  #    "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #    "start_time": "2019-06-15T23:00:00.000Z"
  #  }],
  #  "upcoming_shows": [],
  #  "past_shows_count": 1,
  #  "upcoming_shows_count": 0,
  #}
  #data3={
  #  "id": 6,
  #  "name": "The Wild Sax Band",
  #  "genres": ["Jazz", "Classical"],
  #  "city": "San Francisco",
  #  "state": "CA",
  #  "phone": "432-325-5432",
  #  "seeking_venue": False,
  #  "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #  "past_shows": [],
  #  "upcoming_shows": [{
  #    "venue_id": 3,
  #    "venue_name": "Park Square Live Music & Coffee",
  #    "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #    "start_time": "2035-04-01T20:00:00.000Z"
  #  }, {
  #    "venue_id": 3,
  #    "venue_name": "Park Square Live Music & Coffee",
  #    "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #    "start_time": "2035-04-08T20:00:00.000Z"
  #  }, {
  #    "venue_id": 3,
  #    "venue_name": "Park Square Live Music & Coffee",
  #    "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #    "start_time": "2035-04-15T20:00:00.000Z"
  #  }],
  #  "past_shows_count": 0,
  #  "upcoming_shows_count": 3,
  #}
  #data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.get_or_404(artist_id)
  form = ArtistForm(obj = artist)

  #artist={
  #  "id": 4,
  #  "name": "Guns N Petals",
  #  "genres": ["Rock n Roll"],
  #  "city": "San Francisco",
  #  "state": "CA",
  #  "phone": "326-123-5000",
  #  "website": "https://www.gunsnpetalsband.com",
  #  "facebook_link": "https://www.facebook.com/GunsNPetals",
  #  "seeking_venue": True,
  #  "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #  "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  #}
  # COMPLETE: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):

  # COMPLETE: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  artist = Artist.query.get_or_404(artist_id)
  form = ArtistForm(obj = artist)
  error = False
  try:
    artist.name = form.name.data
    artist.city = form.city.data
    artist.state = form.state.data
    artist.phone = form.phone.data
    artist.genres = form.genres.data
    artist.facebook_link = form.facebook_link.data
    artist.image_link = form.image_link.data
    artist.website_link = form.website_link.data
    artist.seeking_venue = form.seeking_venue.data
    artist.seeking_description = form.seeking_description.data
    db.session.commit()
    flash('Artist ' + form.name.data + ' was successfully updated!')
  except:
    error = True
    flash('An error ocoured. Artist ' + form.name.data + ' could not be updated!')
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    abort (404)
  else:
    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.get_or_404(venue_id)
  form = VenueForm(obj = venue)

  #venue={
  #  "id": 1,
  #  "name": "The Musical Hop",
  #  "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
  #  "address": "1015 Folsom Street",
  #  "city": "San Francisco",
  #  "state": "CA",
  #  "phone": "123-123-1234",
  #  "website": "https://www.themusicalhop.com",
  #  "facebook_link": "https://www.facebook.com/TheMusicalHop",
  #  "seeking_talent": True,
  #  "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
  #  "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  #}
  # COMPLETE: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):

  venue = Venue.query.get_or_404(venue_id)
  form = VenueForm(obj=venue)
  error = False
  try:
    venue.name = form.name.data
    venue.city = form.city.data
    venue.state = form.city.data
    venue.address = form.address.data
    venue.phone = form.phone.data
    venue.genres = form.genres.data
    venue.facebook_link = form.facebook_link.data
    venue.image_link = form.image_link.data
    venue.website_link = form.website_link.data
    venue.seeking_talent = form.seeking_talent.data
    venue.seeking_description = form.seeking_description.data
    db.session.commit()
    flash('Venue ' + form.name.data + ' was successfully updated!')
  except:
    error = True
    flash('An error ocoured. Venue ' + form.name.data + ' could not be updated!')
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    abort (400)
  else:
  # COMPLETE: take values from the form submitted, and update existing
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
  # COMPLETE: insert form data as a new Venue record in the db, instead
  # COMPLETE: modify data to be the data object returned from db insertion
  form = ArtistForm(request.form)
  error = False
  try:
    name = form.name.data
    city = form.city.data
    state = form.state.data
    phone = form.phone.data
    genres = form.genres.data
    facebook_link = form.facebook_link.data
    image_link = form.image_link.data
    website_link = form.website_link.data
    seeking_venue = form.seeking_venue.data
    seeking_description = form.seeking_description.data
    artist = Artist(name = name, city = city, state = state, phone = phone, genres = genres, facebook_link = facebook_link, image_link = image_link, website_link = website_link, seeking_venue = seeking_venue, seeking_description = seeking_description)
    db.session.add(artist)
    db.session.commit()
  # on successful db insert, flash success
    flash('Artist ' + form.name.data + ' was successfully listed!')
  except:
    erro = True
    db.session.rollback()
    print(sys.exc_info())
  # COMPLETE: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    flash('An error occurred. Artist ' + form.name.data + ' could not be listed.')
  finally:
    db.session.close()
  if error:
    abort (400)
  else:
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # COMPLETE: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data = []
  shows = db.session.query(Show).order_by(Show.c.start_time).all()
  for show in shows:
    venue = Venue.query.filter_by(id = show.venue_id).first_or_404()
    artist = Artist.query.filter_by(id = show.artist_id).first_or_404()
    data.append({
      "venue_id": show.venue_id,
      "venue_name": venue.name,
      "artist_id": show.artist_id,
      "artist_name": artist.name,
      "artist_image_link": artist.image_link,
      "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
    })
    

  #data=[{
  #  "venue_id": 1,
  #  "venue_name": "The Musical Hop",
  #  "artist_id": 4,
  #  "artist_name": "Guns N Petals",
  #  "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #  "start_time": "2019-05-21T21:30:00.000Z"
  #}, {
  #  "venue_id": 3,
  #  "venue_name": "Park Square Live Music & Coffee",
  #  "artist_id": 5,
  #  "artist_name": "Matt Quevedo",
  #  "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #  "start_time": "2019-06-15T23:00:00.000Z"
  #}, {
  #  "venue_id": 3,
  #  "venue_name": "Park Square Live Music & Coffee",
  #  "artist_id": 6,
  #  "artist_name": "The Wild Sax Band",
  #  "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #  "start_time": "2035-04-01T20:00:00.000Z"
  #}, {
  #  "venue_id": 3,
  #  "venue_name": "Park Square Live Music & Coffee",
  #  "artist_id": 6,
  #  "artist_name": "The Wild Sax Band",
  #  "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #  "start_time": "2035-04-08T20:00:00.000Z"
  #}, {
  #  "venue_id": 3,
  #  "venue_name": "Park Square Live Music & Coffee",
  #  "artist_id": 6,
  #  "artist_name": "The Wild Sax Band",
  #  "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #  "start_time": "2035-04-15T20:00:00.000Z"
  #}]
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # COMPLETE: insert form data as a new Show record in the db, instead
  form = ShowForm(request.form)
  error = False
  try:
    artist_id = form.artist_id.data
    venue_id = form.venue_id.data
    start_time = form.start_time.data
    show = Show.insert().values(artist_id = artist_id, venue_id = venue_id, start_time = start_time)
    db.session.execute(show)
    db.session.commit()
  # on successful db insert, flash success
    flash('Show was successfully listed!')
  # COMPLETE: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  finally:
    db.session.close()
  if error:
    abort (400)
  else:
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
