from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, IntegerField
from wtforms.validators import DataRequired, ValidationError
import sqlalchemy as sa
from app import db
from app.models import Splits

class NewBettingPageForm(FlaskForm):
    date = DateField('Date', validators=[DataRequired()])
    betting_submit = SubmitField('Create New Betting Page')

class NewScoringPageForm(FlaskForm):
    date = DateField('Date', validators=[DataRequired()])
    scoring_submit = SubmitField('Create New Scoring Page')

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