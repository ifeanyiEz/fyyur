#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
from re import search
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify, abort
from sqlalchemy import func
import logging
from logging import Formatter, FileHandler, error
from flask_wtf import Form
from forms import *
import sys
from models import *

# REFERENCES:
# https://flask-migrate.readthedocs.io/en/latest/
# https://readthedocs.org/projects/flask-sqlalchemy/downloads/pdf/2.x/,
# https://stackoverflow.com/questions/49820972/flask-sqlalchemys-create-all-does-not-create-tables
# https://www.postgresql.org/docs/8.2/server-start.html
# https://python-adv-web-apps.readthedocs.io/en/latest/index.html#
# https://docs.python.org/3/library/datetime.html
# https://docs.python.org/3/library/time.html#time.strptime
# https://www.programiz.com/python-programming
# https://sqlalchemy-searchable.readthedocs.io/en/latest/installation.html
# https://www.digitalocean.com/community/tutorials/build-a-crud-web-app-with-python-and-flask-part-one
# https://stackoverflow.com/questions/42154602/how-to-get-form-data-in-flask
# https://stackoverflow.com/questions/4629684/filtering-on-a-left-join-in-sqlalchemy
# https://stackoverflow.com/questions/38987/how-do-i-merge-two-dictionaries-in-a-single-expression-taking-union-of-dictiona
# https://stackoverflow.com/questions/43829017/can-i-run-a-query-within-a-query-using-sqlalchemy
# https://stackoverflow.com/questions/20041277/flask-sqlalchemy-number-of-results-in-query
# https://stackoverflow.com/questions/41270319/how-do-i-query-an-association-table-in-sqlalchemy
# https://www.kimsereylam.com/sqlalchemy/2020/01/24/alembic-operations.html#modify-constraint
# https://docs.sqlalchemy.org/en/14/core/type_basics.html
# https://amitosh.medium.com/full-text-search-fts-with-postgresql-and-sqlalchemy
# https://technobytz.com/like-and-ilike-for-pattern-matching-in-postgresql.html 
# https://stackoverflow.com/questions/41270319/how-do-i-query-an-association-table-in-sqlalchemy
# https://www.unsplash.com/photos
# https://www.pexels.com/photos


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

# List of recently added venues and artists to show on home page.

  venue_data = []                                                                           #Data for venues to be displayed on home page. This must be a list of records and is set to an empty list
  artist_data = []                                                                          #Data for artists to be displayed on home page. This is also a list of records and is set to an empty list

  recent_venues = db.session.query(Venue).order_by(Venue.created.desc()).limit(10)          #Query the DB for venues, presented in descending order of the time of creation. Extract only the first 10
  for location in recent_venues:                                                            #Each record or location in the query result is a dictionary with key-value pairs
    location_data = {}                                                                      #For each location, query the DB for shows where the value of the location.id appears in the shows table. Get a total count.
    upcoming_shows = db.session.query(func.count(Show.c.venue_id).label("upcoming")).filter((location.id == Show.c.venue_id) & (Show.c.start_time > datetime.now())).all()
    for show in upcoming_shows:                                                             #Extract the details for each location and populate the dictionary
      location_data['id'] = location.id
      location_data['name'] = location.name
      location_data['city'] = location.city
      location_data['state'] = location.state
      location_data['phone'] = location.phone
      venue_data.append(location_data)                                                      #Append the resulting dictionary to the list of dictionaries in venue_data

  recent_artists = db.session.query(Artist).order_by(Artist.created.desc()).limit(10)       #Query the DB for artists, presented in descending order of the time of creation. Extract only the first 10
  for band in recent_artists:                                                               #Each record or band in the query result is a dictionary with key-value pairs
    band_data = {}                                                                          #For each band, query the DB for shows where the value of the band.id appears in the shows table. Get a total count.
    upcoming_shows = db.session.query(func.count(Show.c.artist_id).label("upcoming")).filter((band.id == Show.c.artist_id) & (Show.c.start_time > datetime.now())).all()
    for show in upcoming_shows:                                                             #Extract the details for each band and populate the dictionary
      band_data['id'] = band.id
      band_data['name'] = band.name
      band_data['city'] = band.city
      band_data['state'] = band.state
      band_data['phone'] = band.phone
      artist_data.append(band_data)                                                         #Append the resulting dictionary to the list of dictionaries in artist_data


  return render_template('pages/home.html', venue_data = venue_data, artist_data = artist_data)


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # COMPLETE: replace with real venues data.
  # num_shows should be aggregated based on number of upcoming shows per venue.

                                                                                            #The demo data suggests the data to be a list containing a dictionaries in which there is another list of dictionaries

  data = []                                                                                 #Data is set to an empty list
  
  places = db.session.query(Venue.city, Venue.state).distinct(Venue.city, Venue.state).order_by(Venue.state).all()  #Query the DB for venues and return only city and state values (called places) without repetitions 
  city_venues = db.session.query(Venue.id, Venue.name, Venue.city, Venue.state).all()                               #Query the DB again for all venues (city_venues), returning relevant details only
  for place in places:
    place_data = {                                                                          #Collect the details for each place into a dictionary, and set the value for the "venues" (in the place) to an empty list
      "city": place.city,
      "state": place.state,
      "venues": []
    }
    data.append(place_data)                                                                 #Append the details for each place to the list of dictionaries in data

  for place_set in data:                                                                    #To fill out our empty "venues" list, we run through the contents of data (place_sets) one at a time
    for city_venue in city_venues:                                                          #For each place set in data, we go through our city_venues query result to extract actual venue locations
      location = {}                                                                         #Each location is a dictionary
      if city_venue.city == place_set.get("city"):                                          #When we find a match between city in our city_venues query results and city in data, query the DB for upcoming shows
        upcoming_shows = db.session.query(func.count(Show.c.venue_id).label("upcoming")).filter((city_venue.id == Show.c.venue_id) & (Show.c.start_time > datetime.now())).all()
        for show in upcoming_shows:                                                         #Collect the details for each location into a dictionary
          location["id"] = city_venue.id
          location["name"] = city_venue.name
          location["num_upcoming_shows"] = show.upcoming
        place_set["venues"].append(location)                                                #Appennd the location dictionary to the list of dictionaries in venues.
  
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

  # COMPLETE: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

  response = {}                                                                             #Demo data shows response to be a dictionary in which there's a list of dictionaries
  data = []                                                                                 #We call the list of dictionaries data
  search_text = (request.form['search_term']).strip()                                       #Users may include blank spaces in their search. Remove leading or trailing blank spaces from user entries
                                                                                            #Query the DB for venues. Search for the input string or similar in the name, city or state columns
  venue_search = Venue.query.filter(Venue.name.ilike('%' + search_text + '%') | Venue.city.ilike('%' + search_text + '%') | Venue.state.ilike('%' + search_text + '%'))                 
  for result in venue_search:
    result_data = {}                                                                        #For every record in the search results, query the DB for shows. Count upcoming shows, where the result.id matches venue_id.
    upcoming_shows = db.session.query(func.count(Show.c.venue_id).label("upcoming")).filter((result.id == Show.c.venue_id) & (Show.c.start_time > datetime.now())).all()
    for show in upcoming_shows:                                                             #Extract result_data, including the count of upcoming shows
      result_data['id'] = result.id
      result_data['name'] = result.name
      result_data['num_upcoming_shows'] = show.upcoming
      data.append(result_data)                                                              #Append result_data to the list of dictionaries in data

  response["count"] = len([result for result in venue_search])                              #The number of records in the search results that have matching text
  response["data"] = data 
  

  # response = {
  #   "count": 1,
  #   "data": [{
  #      "id": 2,
  #      "name": "The Dueling Pianos Bar",
  #      "num_upcoming_shows": 0,
  #   }]
  # }

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # COMPLETE: replace with real venue data from the venues table, using venue_id
  
  past_shows = []                                                                           #Sample data shows past shows to be a list containing dictionaries
  upcoming_shows = []                                                                       #Sample data also shows upcoming shows to be a list made up of dictionaries
  data = {}                                                                                 #Data is presented as a dictionanries whose contents include the above lists as well

  venue = Venue.query.get_or_404(venue_id)                                                  #Query the DB for venues and fetch the venue with the given ID
                                                                                            #Then query the DB again. Join shows and venues; extract all past shows where the given venue id appears in the shows table.
  venue_past_shows = db.session.query(Show).join(Venue).filter((Show.c.venue_id == venue_id) & (Show.c.start_time <= datetime.now())).all()
  for past_show in venue_past_shows:                                                                                             #For each past show, get the artist's information in a dictionary
    artist_info = {}
    past_show_artists = db.session.query(Artist).join(Show).filter(Artist.id == past_show.artist_id).all()                       
    for past_show_artist in past_show_artists:
      artist_info['artist_id'] = past_show.artist_id
      artist_info['artist_name'] = past_show_artist.name
      artist_info['artist_image_link'] = past_show_artist.image_link
      artist_info['start_time'] = past_show.start_time.strftime("%m/%d/%Y, %H:%M")
      past_shows.append(artist_info)                                                                                             #Append the artist's information to the contents of the past_shows list

                                                                                            #Now, query the DB joining shows and venues, extracting all future shows where given venue id appears in the shows table
  venue_upcoming_shows = db.session.query(Show).join(Venue).filter((Show.c.venue_id == venue_id) & (Show.c.start_time > datetime.now())).all()
  for upcoming_show in venue_upcoming_shows:                                                                                    #For each future show, get the artist's information in a dictionary
    artist_infos = {}
    upcoming_show_artists = db.session.query(Artist).join(Show).filter(Artist.id == upcoming_show.artist_id).all()
    for upcoming_show_artist in upcoming_show_artists:
      artist_infos['artist_id'] = upcoming_show.artist_id
      artist_infos['artist_name'] = upcoming_show_artist.name
      artist_infos['artist_image_link'] = upcoming_show_artist.image_link
      artist_infos['start_time'] = upcoming_show.start_time.strftime("%m/%d/%Y, %H:%M")
      upcoming_shows.append(artist_infos)                                                                                        #Append the artist's information to the contents of the upcoming_shows list
      

  data['id'] = venue.id                                                                                                          #Then put everything together in the data dictionary
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
  form = VenueForm(request.form)                                                              #Call the VenueForm class and create an instance of it
  error = False                                                                               #Assume there are no errors at the start
  try:
    name = form.name.data                                                                     #Capture the content of each form field to a variable
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
                                                                                              #Instantiate a new venue and, using the Venue class, fromat the data in the manner expected by the DB
    venue = Venue(name = name, city = city, state = state, address = address, phone = phone, image_link = image_link, genres = genres, facebook_link = facebook_link, website_link = website_link, seeking_talent = seeking_talent, seeking_description = seeking_description)
    print(venue)
    db.session.add(venue)                                                                     #Insert the new venue to the venue table of the DB
    db.session.commit()                                                                       #Confirm the insertion
# on successful db insert, flash success
    flash('Venue ' + form.name.data + ' was successfully listed!')                            #Flash a message on the screen to show successful insertion
# COMPLETE: modify data to be the data object returned from db insertion
  except:
    error = True                                                                              #If there's an error, do not create the venue then print a message that shows the error.
    db.session.rollback()
    print(sys.exc_info())
# COMPLETE: on unsuccessful db insert, flash an error instead.
# e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
# see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    flash('An error occurred. Venue ' + form.name.data + ' could not be listed.')             #Flash a message on the screen to show unsuccessful insertion
  finally:
    db.session.close                                                                          #Close the session
  if error:
    abort (400)                                                                               
  else:
    return redirect(url_for('index'))

#  Delete Venue
#  ----------------------------------------------------------------

@app.route('/venues/<venue_id>', methods=['POST'])
def delete_venue(venue_id):

  # COMPLETE: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  
  try:
    for_deletion = Venue.query.filter_by(id = venue_id).first_or_404()                        #Query the DB for venues and look the venue with the given id. Assign the result to a variable
    if for_deletion:                                                                          #If there's a result, set it to the current session
      current_session = db.object_session(for_deletion)
      current_session.delete(for_deletion)                                                    #Delete current session
      current_session.commit()                                                                #Confirm session deletion
      flash('Venue ' + for_deletion.name + ' was successfully deleted!')                      #Flash a message on screen to show successful deletion
      return redirect(url_for('index'))                                                       #Return to home page
  except:
    db.session.rollback()                                                                     #If there are any issues, do not perform the delete
    print(sys.exc_info())                                                                     #Print the issues and return to venues page
    return redirect(url_for('venues'))
  finally:
    db.session.close()                                                                        #Close session

  # COMPLETE BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  #return None

  #return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():

  # COMPLETE: replace with real data returned from querying the database

  data = []                                                         

  bands = Artist.query.order_by(Artist.id).all()
  for band in bands:
    upcoming_shows = db.session.query(func.count(Show.c.artist_id).label("upcoming")).filter((band.id == Show.c.artist_id) & (Show.c.start_time > datetime.now())).all()
    for show in upcoming_shows:
      band_data = {}
      band_data['id'] = band.id
      band_data['name'] = band.name
      band_data['num_upcoming_shows'] = show.upcoming
      data.append(band_data)
      

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

  # COMPLETE: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

  data = []
  search_text = (request.form['search_term']).strip()

  artist_search = Artist.query.filter(Artist.name.ilike('%' + search_text + '%') | Artist.city.ilike('%' + search_text + '%') | Artist.state.ilike('%' + search_text + '%'))

  for result in artist_search:
    result_data = {}
    upcoming_shows = db.session.query(func.count(Show.c.artist_id).label("upcoming")).filter((result.id == Show.c.artist_id) & (Show.c.start_time > datetime.now())).all()
    for show in upcoming_shows:
      result_data['id'] = result.id
      result_data['name'] = result.name
      result_data['num_upcoming_shows'] = show.upcoming
      data.append(result_data)

  response = {
      "count": len([result for result in artist_search]),
      "data": data
  }

  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 4,
  #     "name": "Guns N Petals",
  #     "num_upcoming_shows": 0,
  #   }]
  # }

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
    venue_info = {}
    past_show_venues = db.session.query(Venue).join(Show).filter(Venue.id == past_show.venue_id).all()
    for past_show_venue in past_show_venues:
      venue_info['venue_id'] = past_show.venue_id
      venue_info['venue_name'] = past_show_venue.name
      venue_info['venue_image_link'] = past_show_venue.image_link
      venue_info['start_time'] = past_show.start_time.strftime("%m/%d/%Y, %H:%M")
      past_shows.append(venue_info)

  artist_upcoming_shows = db.session.query(Show).join(Artist).filter((Show.c.artist_id == artist_id) & (Show.c.start_time > datetime.now())).all()
  for upcoming_show in artist_upcoming_shows:
    venue_infos = {}
    upcoming_show_venues = db.session.query(Venue).join(Show).filter(Venue.id == upcoming_show.venue_id).all()
    for upcoming_show_venue in upcoming_show_venues:
      venue_infos['venue_id'] = upcoming_show.venue_id
      venue_infos['venue_name'] = upcoming_show_venue.name
      venue_infos['venue_image_link'] = upcoming_show_venue.image_link
      venue_infos['start_time'] = upcoming_show.start_time.strftime("%m/%d/%Y, %H:%M")
      upcoming_shows.append(venue_infos)
  
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
    venue.state = form.state.data
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
    return redirect(url_for('index'))


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
    show = Show.insert().values(artist_id = artist_id, venue_id = venue_id, start_time = start_time)          #The insert() function is used because Show is of the Table class.
    db.session.execute(show)                                                                                  #Same reason why the execute() function is used instead of add()
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
    return redirect(url_for('index'))

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
