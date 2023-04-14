from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

from datetime import datetime, timedelta
from enum import unique
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import backref
import hashlib
import os

from flask_login import UserMixin

class User(db.Model, UserMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)

    # user information
    email = db.Column(db.String, nullable=False, unique=True)
    password_digest = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)

    # user profile
    maxFocusTime = db.Column(db.Float, nullable=False)
    preferedWorkTime = db.Column(
        db.Integer, nullable=False
    )  # it can be either 1 (night time) or 0 (day time)
    assignments = db.relationship("Assignment")
    timeslots = db.relationship("Timeslot")

    def __init__(self, **kwargs):
        self.name = kwargs.get("name")
        self.email = kwargs.get("email")
        self.password_digest = kwargs.get("password")
        self.maxFocusTime = kwargs.get("maxFocusTime")
        self.preferedWorkTime = kwargs.get("preferedWorkTime")
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "maxFocusTime": (self.maxFocusTime),
            "preferedWorkTime": (self.preferedWorkTime),
            "assignments": [a.sub_serialize() for a in self.assignments],
            "timeslots": [t.sub_serialize() for t in self.timeslots],
        }

class Assignment(db.Model):
    __tablename__ = "assignment"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    duedate = db.Column(db.DateTime, nullable=False)
    amtOfTime = db.Column(db.Interval, nullable=False)
    user = db.Column(db.Integer, db.ForeignKey("user.id"))
    timeslots = db.relationship(
        "Timeslot"
    )  # db.Integer, uselist=False, backref="timeslot")
    priority = db.Column(db.Integer, nullable=False)

    def __init__(self, **kwargs):
        self.name = kwargs.get("name")
        self.duedate = kwargs.get("duedate")
        self.amtOfTime = kwargs.get("amtOfTime")
        self.user = kwargs.get("user")
        self.priority = kwargs.get("priority")
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "priority": self.priority,
            "duedate": (self.duedate),
            "amtOfTime": (self.amtOfTime),
            "user": self.user,
            "timeslots": [t.sub_serialize() for t in self.timeslots],
        }
    def JsonizableSerialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "priority": self.priority,
            "duedate": str(self.duedate),
            "amtOfTime": str(self.amtOfTime),
            "user": self.user,
            "timeslots": [t.jserialize() for t in self.timeslots],
        }
    def sub_serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "priority": self.priority,
            "duedate": str(self.duedate),
            "amtOfTime": str(self.amtOfTime),
        }

class Timeslot(db.Model):
    __tablename__ = "timeslots"
    id = db.Column(db.Integer, primary_key=True)
    assignment = db.Column(db.Integer, db.ForeignKey("assignment.id"))
    startTime = db.Column(db.DateTime, nullable=False)
    endTime = db.Column(db.DateTime, nullable=False)
    user = db.Column(db.Integer, db.ForeignKey("user.id"))

    def __init__(self, **kwargs):
        self.assignment = kwargs.get("assignment")
        self.startTime = kwargs.get("startTime")
        self.endTime = kwargs.get("endTime")
        self.user = kwargs.get("user")
    def serialize(self):
        return {
            "id": self.id,
            "assignment": self.assignment,
            "startTime": (self.startTime),
            "endTime": (self.endTime),
            "user": self.user,
        }
    def sub_serialize(self):
        return {
            "id": self.id,
            "startTime": str(self.startTime),
            "endTime": str(self.endTime),
        }
    def jserialize(self):
        return {
            "id": self.id,
            "assignment": self.assignment,
            "startTime": str(self.startTime),
            "endTime": str(self.endTime),
            "user": self.user,
        }
