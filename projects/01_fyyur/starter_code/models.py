#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from os import name
import dateutil.parser
from flask import Flask
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import backref
from flask_migrate import Migrate
from forms import *


#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# COMPLETE: connect to a local postgresql database

migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

# COMPLETE: implement any missing fields, as a database migration using Flask-Migrate

# COMPLETE Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

Show = db.Table('shows', 
    db.Column('id', db.Integer, primary_key=True),
    db.Column('artist_id', db.Integer, db.ForeignKey('artist.id'), nullable=False),
    db.Column('venue_id', db.Integer, db.ForeignKey('venue.id'), nullable=False),
    db.Column('start_time', db.DateTime, unique=True, nullable=False),
)


class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
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
    created = db.Column(db.DateTime, default=datetime.now)
    artists = db.relationship('Artist', secondary=Show, backref=db.backref('venue', lazy=True))

    def __repr__(self):
        return 'Venue {} {} {} {} {} {} {} {} {} {} {} {} {}'.format(self.id, self.name, self.city, self.state, self.address, self.phone, self.genres, self.facebook_link, self.image_link, self.website_link, self.seeking_talent, self.seeking_description, self.created)

    # COMPLETE: implement any missing fields, as a database migration using Flask-Migrate


class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String(120)), nullable=False)
    facebook_link = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    website_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(500))
    created = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
      return 'Artist {} {} {} {} {} {} {} {} {} {} {} {}'.format(self.id, self.name, self.city, self.state, self.phone, self.genres, self.facebook_link, self.image_link, self.website_link, self.seeking_venue, self.seeking_description, self.created)
