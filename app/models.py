from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db

class Betting(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)

    date: so.Mapped[str] = so.mapped_column(sa.String(64),
                                            index=True, unique=True)
    
    def __repr__(self):
        return '<Date {}>'.format(self.date)
    
class Splits(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)

    layout: so.Mapped[str] = so.mapped_column(sa.String(64), 
                                              index=True, unique=True)
    
    value: so.Mapped[int] = so.mapped_column(sa.Integer,
                                              index=True)
    
    def __repr__(self):
        return '<Split Layout: {}>, <Split Worth: {}>'.format(self.layout, self.value)
    
