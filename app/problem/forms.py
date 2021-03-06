from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, IntegerField, SelectField
from wtforms.validators import ValidationError, DataRequired, Length, NumberRange
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from app.models import User, Language
from app.problem import bp

class CreateProblemForm(FlaskForm):
    title           = StringField('title', validators=[DataRequired()])
    time_limit      = IntegerField('time_limit(s)',
        validators=[NumberRange(min=1, max=60)],
        default=1)
    memory_limit    = IntegerField('memory_limit(MB)',
        validators=[NumberRange(min=1, max=4096)],
        default=128)
    body            = TextAreaField('body', validators=
        [DataRequired()])
    submit          = SubmitField('Submit')

class SubmitForm(FlaskForm):
    language        = QuerySelectField(
        query_factory=lambda: Language.query.all(),
        get_label='name',
        validators=[DataRequired()])
    code            = TextAreaField('code', validators=[Length(min=1, max=65535)])
    submit          = SubmitField('Submit')

