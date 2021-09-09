import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import backref
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from flask_migrate import Migrate
from forms import *
import sys
from app import db


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

# TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.


show = db.Table('show',
                db.Column('Artist_id', db.Integer, db.ForeignKey(
                    'Artist.id'), primary_key=True),
                db.Column('Venue_id', db.Integer, db.ForeignKey(
                    'Venue.id'), primary_key=True),
                db.Column('start_time', db.DateTime),
                )


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    website_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(500))
    artists = db.relationship('Artist', secondary=show,
                              backref=db.backref('Venue', lazy=True))

    def __repr__(self):
        return 'Venue {} {} {} {} {} {} {} {} {} {} {} {}'.format(self.id, self.name, self.city, self.state, self.address, self.phone, self.genres, self.facebook_link, self.image_link, self.website_link, self.seeking_talent, self.seeking_description)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    website_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(500))

    def __repr__(self):
      return 'Artist {} {} {} {} {} {} {} {} {} {} {}'.format(self.id, self.name, self.city, self.state, self.phone, self.genres, self.facebook_link, self.image_link, self.website_link, self.seeking_venue, self.seeking_description)
