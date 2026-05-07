from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, IntegerField
from wtforms.validators import DataRequired, ValidationError
import sqlalchemy as sa
from app import db
from app.models import Splits, Game, Series

class NewSeriesForm(FlaskForm):

    date = DateField(
        'Date',
        validators=[DataRequired()]
    )

    submit = SubmitField('Create Bowling Night')

    def validate_date(self, date):

        series = db.session.scalar(
            sa.select(Series).where(
                Series.date == date.data
            )
        )

        if series is not None:
            raise ValidationError(
                'That bowling night already exists!'
            )

class NewGameForm(FlaskForm):
    date = DateField('Date', validators=[DataRequired()])
    submit = SubmitField('Create New Game')

    def validate_date(self, date):
        game = db.session.scalar(sa.select(Game).where(
            Game.date == date.data))
        if game is not None:
            raise ValidationError('Date already exists!')

class NewSplitForm(FlaskForm):
    layout = StringField('Split Layout', validators=[DataRequired()])
    value = IntegerField('Split Value', validators=[DataRequired()])
    submit = SubmitField('Create New Split')

    def validate_layout(self, layout):
        split = db.session.scalar(sa.select(Splits).where(
            Splits.layout == layout.data))
        if split is not None:
            raise ValidationError('Split already exists!')
        
class DeleteForm(FlaskForm):
    submit = SubmitField('Delete')