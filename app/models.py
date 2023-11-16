# https://docs.sqlalchemy.org/en/20/orm/basic_relationships.html#association-object

from typing import List

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app import db


class Participation(db.Model):
    __tablename__ = "participation_table"
    participant_id: Mapped[int] = mapped_column(
        ForeignKey("participant_table.id"), primary_key=True
    )
    event_id: Mapped[int] = mapped_column(
        ForeignKey("event_table.id"), primary_key=True
    )
    certificate: Mapped[str] = mapped_column(db.String(32), unique=True, nullable=False)
    participant: Mapped["Participant"] = relationship(back_populates="events")
    event: Mapped["Event"] = relationship(back_populates="participants")

    def __repr__(self) -> str:
        return "<Participation of %r in %r>" % (self.participant.email, self.event.name)


class Participant(db.Model):
    __tablename__ = "participant_table"
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    name: Mapped[str] = mapped_column(db.String(100), nullable=False)
    email: Mapped[str] = mapped_column(db.String(320), unique=True, nullable=False)
    events: Mapped[List["Participation"]] = relationship(back_populates="participant", cascade='save-update, merge, delete')

    def __repr__(self):
        return "<Participant %r>" % self.email


class Event(db.Model):
    __tablename__ = "event_table"
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    name: Mapped[str] = mapped_column(db.String(20), nullable=False)
    participants: Mapped[List["Participation"]] = relationship(back_populates="event", cascade='save-update, merge, delete')

    def __repr__(self) -> str:
        return "<Event %r>" % self.name
