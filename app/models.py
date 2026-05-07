from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
import datetime
from app import db

class Series(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)

    date: so.Mapped[datetime.date] = so.mapped_column(
        sa.Date(),
        unique=True,
        index=True
    )

    games: so.Mapped[list['Game']] = so.relationship(
        back_populates='series',
        cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f'<Series {self.date}>'

    @property
    def display_date(self):
        return self.date.strftime("%b %d, %Y")

class Game(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)

    series_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey('series.id'),
        index=True
    )

    game_number: so.Mapped[int] = so.mapped_column(sa.Integer())

    form_state: so.Mapped[str] = so.mapped_column(
        sa.Text(),
        nullable=True
    )

    series: so.Mapped['Series'] = so.relationship(
        back_populates='games'
    )

    __table_args__ = (
        sa.UniqueConstraint('series_id', 'game_number'),
    )

    def __repr__(self):
        return f'<Game {self.game_number}>'

# class Game(db.Model):
#     id: so.Mapped[int] = so.mapped_column(primary_key=True)

#     date: so.Mapped[datetime.date] = so.mapped_column(sa.Date(),
#                                             index=True, unique=True)
    
#     form_state: so.Mapped[str] = so.mapped_column(sa.Text(), nullable=True)
    
#     def __repr__(self):
#         return '<Date {}>'.format(self.date)
    
#     @property
#     def display_date(self):
#         return self.date.strftime("%b %d, %Y")
    
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
    
