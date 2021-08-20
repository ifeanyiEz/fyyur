from datetime import datetime
from os import error
from flask_wtf import Form
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField, BooleanField
from wtforms.validators import DataRequired, AnyOf, URL, ValidationError
import enum
from enum import Enum, unique


class Genres(Enum):
    Alternative = 'Alternative'
    Blues = 'Blues'
    Classical = 'Classical'
    Country = 'Country'
    Electronic = 'Electronic'
    Folk = 'Folk'
    Funk = 'Funk'
    Hip_Hop = 'Hip-Hop'
    Heavy_Metal = 'Heavy Metal'
    Instrumental = 'Instrumental'
    Jazz = 'Jazz'
    Musical_Theatre = 'Musical Theatre'
    Pop = 'Pop'
    Punk = 'Punk'
    R_n_B = 'R&B'
    Reggae = 'Reggae'
    Rock_n_Roll = 'Rock n Roll'
    Soul = 'Soul'
    Other = 'Other'

    @classmethod
    def genre_names(cls):
        valid_choices = [(genre.name, genre.value) for genre in Genres]
        return valid_choices

    @classmethod
    def validate_genre(cls):
        valid_values = [genre.value for genre in Genres]
        message = 'This is an invalid genre. Valid genres are: {}'.format(valid_values)
        def validate_field(form, field):
            error = False
            for field_entry in field.data:
                if field_entry not in valid_values:
                    error = True
            if error:
                raise ValidationError(message)
        return validate_field
            
