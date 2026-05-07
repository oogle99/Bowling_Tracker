from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
import datetime
from app import db

class Game(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)

    date: so.Mapped[datetime.date] = so.mapped_column(sa.Date(),
                                            index=True, unique=True)
    
    form_state: so.Mapped[str] = so.mapped_column(sa.Text(), nullable=True)
    
    def __repr__(self):
        return '<Date {}>'.format(self.date)
    
    @property
    def display_date(self):
        return self.date.strftime("%b %d, %Y")
    
class Score(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)

    game_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('game.id'))

    bowler_name: so.Mapped[str] = so.mapped_column(sa.String(64))

    frames: so.Mapped[str] = so.mapped_column(sa.Text)
        
class Splits(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)

    layout: so.Mapped[str] = so.mapped_column(sa.String(64), 
                                              index=True, unique=True)
    
    value: so.Mapped[int] = so.mapped_column(sa.Integer,
                                              index=True)
    
    def __repr__(self):
        return '<Split Layout: {}>, <Split Worth: {}>'.format(self.layout, self.value)
    
