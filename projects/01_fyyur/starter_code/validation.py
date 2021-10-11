from datetime import datetime
from os import error
from flask_wtf import Form
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField, BooleanField
from wtforms.validators import DataRequired, AnyOf, URL, ValidationError
import enum
from enum import Enum, unique

#References: 
# https://docs.python.org/3/library/enum.html,
# https://wtforms.readthedocs.io/en/2.3.x/validators/
# https://www.geeksforgeeks.org/enum-in-python/, 
# https://www.codegrepper.com/code-examples/python/python+implement+enum+restriction, 
# https://codeyarns.com/tech/2013-05-01-how-to-use-enum-in-python.html,
# https://stackoverflow.com/questions/43160780/python-flask-wtform-selectfield-with-enum-values-not-a-valid-choice-upon-valid,
# https://wtforms.readthedocs.io/en/2.3.x/fields/
# https://docs.sqlalchemy.org/en/14/core/type_basics.html?highlight=enum#sqlalchemy.types.Enum
# https://lala-rustamli.medium.com/casting-populated-table-column-to-enum-in-flask-with-sqlalchemy-f44fe404d9ae
# https://www.programiz.com/python-programming

class Genres(Enum):                                                                                         #Declare an enum class Genres with names and corresponding values of the class members
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


    @classmethod                                                                                                #Define a function genre_names as a method of the class Genres
    def genre_names(cls):
        valid_choices = [(genre.name, genre.value) for genre in Genres]                                         #Restrict valid choices to the list of name-value pairs in Genres
        return valid_choices

    @classmethod                                                                                                #Define a function, validate_genres, as a method of the class Genres
    def validate_genre(cls):                        
        valid_values = [genre.value for genre in Genres]                                                        #Make a list of genre values from the enum class Genres. Values are valid if they are in the list.
        message = 'You have entered an invalid genre. Valid genres must bbe one of: {}'.format(valid_values)    #A caution message for invalid generes
        def validate_field(form, field):                                                                        #A function to check the value within the form field for validity
            for field_entry in field.data:                                                                      #Since we expect multiple entries in the field, we run through them one at a time
                if field_entry not in valid_values:                                                             #If any entry is not in the list of valid values, raise the validation error
                    raise ValidationError(message)
        return validate_field
            
