from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Length
from app.models import User

class LanguageForm(FlaskForm):
    name    = StringField('language', validators=[DataRequired()])
    compile = StringField('compile', validators=[DataRequired(), Length(min=1, max=200)])
    submit  = SubmitField('Submit')

class ResultForm(FlaskForm):
    name    = StringField('result', validators=[DataRequired()])
    submit  = SubmitField('Submit')