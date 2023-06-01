from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from . import db
import json
import sys
from website import model

views = Blueprint("views", __name__)

# -*- coding: utf-8 -*-

from distutils.log import debug
import pytz
from .models import Assignment, Timeslot, User
import flask
from flask import Flask, redirect, session
from flask import request, render_template, url_for
import requests
import json
from datetime import datetime, timedelta
import os
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
from googleapiclient.discovery import build
import uuid
import json
import logging
from dateutil import tz  # For interpreting local times
from oauth2client import client
import httplib2  # used in oauth2 flow
from apiclient import discovery

CLIENT_SECRET_FILE = "client_id.json"  ## You'll need this

SCOPES = ["https://www.googleapis.com/auth/calendar"]
API_SERVICE_NAME = "calendar"
API_VERSION = "v3"


def dateit(date, plus):
    """
    :param date: The date and time you want to convert
    :param plus: The number of days to add to the date
    :return: a string that is the date and time in the format of the Azure SQL Data Warehouse.
    """
    # from 2022-01-17 09:59:00 to 2015-05-28T09:00:00-07:00
    sign = ""
    for char in (plus.split(":")[2])[2:]:
        sign += char
    return date.split(" ")[0] + "T" + date.split(" ")[1] + str(sign)


def timebreak(startTime, endTime, user):
    """
    The function takes in the start time and end time of a user's session and creates a number of blocks
    of time equal to the number of blocks of time the user has specified.

    :param startTime: the start time of the day
    :param endTime: the end time of the day
    :param user: the user object
    :return: The response is a list of dictionaries, each dictionary representing a timeslot.
    """
    # the response of the query
    resp = []
    # calculate the number of blocks required
    secDiff = (endTime - startTime).total_seconds()
    minuteDiff = secDiff / 60
    numBlocks = int(minuteDiff // (user.maxFocusTime * 60))
    # create Timeslot objects
    index = 0
    for block in range(numBlocks):
        a = startTime + block * timedelta(minutes=user.maxFocusTime * 60 * 6 / 5)
        index += 1
        if index != 5:
            # create a Timeslot object
            slot = Timeslot(
                startTime=a,
                endTime=a + timedelta(minutes=(user.maxFocusTime * 60)),
                assignment=None,
                user=user.id,
            )
            db.session.add(slot)
            db.session.commit()
            # add the new timeslot to response
            resp.append(slot.jserialize())
        else:
            slot = Timeslot(
                startTime=a + timedelta(minutes=user.maxFocusTime * 1 / 3 * 60),
                endTime=a + timedelta(minutes=user.maxFocusTime * 60 * 2 / 3),
                assignment=None,
                user=user.id,
            )
            db.session.add(slot)
            db.session.commit()
            index = 0
    return resp


@views.route("/")
@login_required
def init():
    return render_template("home.html", name=current_user.name)


@views.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    """
    This function is used to update the user profile
    :return: The profile page is being returned.
    """
    user = User.query.filter_by(email=current_user.email).first()
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        maxFocusTime = request.form.get("maxFocusTime")
        preferedWorkTime = 1 if request.form.get("preferedWorkTime") == "night" else 0
        user.preferedWorkTime = preferedWorkTime
        user.maxFocusTime = maxFocusTime
        user.name = name
        user.email = email
        db.session.commit()
        return render_template("profile.html", data=user.serialize())
    return render_template("profile.html", data=user.serialize())


def credentials_to_dict(credentials):
    """
    Converts a Credentials object to a Python dictionary

    :param credentials: The credentials obtained from the client_secret_json_path and the
    client_secret_json_path
    :return: a dictionary of the credentials.
    """
    return {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": credentials.scopes,
    }


@views.route("/timeslots/", methods=["GET", "POST"])
@login_required
def timeslots():
    """
    This function is used to create a timeslot for a user.
    :return: A JSON object with the timeslots and assignments.
    """
    user = User.query.filter_by(email=current_user.email).first()
    if request.method == "POST":
        startTime = request.form.get("startTime")
        endTime = request.form.get("endTime")
        resp = timebreak(
            (
                datetime(
                    month=int(startTime.split("-")[1]),
                    day=int((startTime.split("-")[2]).split("T")[0]),
                    year=int((startTime.split("-")[0])),
                    hour=int((startTime.split("T")[1]).split(":")[0]),
                    minute=int((startTime.split("T")[1]).split(":")[1]),
                )
            ),
            (
                datetime(
                    month=int(endTime.split("-")[1]),
                    day=int((endTime.split("-")[2]).split("T")[0]),
                    year=int((endTime.split("-")[0])),
                    hour=int((endTime.split("T")[1]).split(":")[0]),
                    minute=int((endTime.split("T")[1]).split(":")[1]),
                )
            ),
            user,
        )
        if Timeslot.query.filter_by(user=user.id).first() is not None:
            return render_template(
                "timeslots.html",
                data=[t.jserialize() for t in Timeslot.query.filter_by(user=user.id)],
                asn=[
                    a.JsonizableSerialize()
                    for a in Assignment.query.filter_by(user=user.id)
                ],
            )
    return render_template(
        "timeslots.html",
        data=[t.jserialize() for t in Timeslot.query.filter_by(user=user.id)],
    )


@views.route("/assignments/", methods=["GET", "POST", "DELETE"])
@login_required
def assignment():
    """
    This function is used to create a new assignment.
    :return: A list of all the assignments that are associated with the user.
    """
    user = User.query.filter_by(email=current_user.email).first()
    if request.method == "POST":
        # body = json.loads(request.data)
        duedate = request.form.get("duedate")
        amtofTime = request.form.get("amount of time")
        hours = int(amtofTime.split(":")[0])
        minutes = int(amtofTime.split(":")[1])
        priority = request.form.get("priority")
        new_assignment = Assignment(
            name=request.form.get("name"),
            duedate=(
                datetime(
                    month=int(duedate.split("-")[1]),
                    day=int((duedate.split("-")[2]).split("T")[0]),
                    year=int((duedate.split("-")[0])),
                    hour=int((duedate.split("T")[1]).split(":")[0]),
                    minute=int((duedate.split("T")[1]).split(":")[1]),
                )
            ),
            amtOfTime=timedelta(hours=hours, minutes=minutes),
            user=user.id,
            priority=priority,
        )
        db.session.add(new_assignment)
        db.session.commit()
        return render_template(
            "assignment.html",
            data=[
                a.JsonizableSerialize()
                for a in Assignment.query.filter_by(user=user.id)
            ],
        )
    return render_template(
        "assignment.html",
        data=[
            a.JsonizableSerialize() for a in Assignment.query.filter_by(user=user.id)
        ],
    )


def valid_credentials(email):
    """
    Returns OAuth2 credentials if we have valid
    credentials in the session.  This is a 'truthy' value.
    Return None if we don't have credentials, or if they
    have expired or are otherwise invalid.  This is a 'falsy' value.
    """
    if f"{email} credentials" not in flask.session:
        return None

    credentials = client.OAuth2Credentials.from_json(
        flask.session[f"{email} credentials"]
    )

    if credentials.invalid or credentials.access_token_expired:
        return None
    return credentials


@views.route("/oauth2callback")
@login_required
def oauth2callback():
    """
    The 'flow' has this one place to call back to.  We'll enter here
    more than once as steps in the flow are completed, and need to keep
    track of how far we've gotten. The first time we'll do the first
    step, the second time we'll skip the first step and do the second,
    and so on.
    """
    flow = client.flow_from_clientsecrets(
        CLIENT_SECRET_FILE,
        scope=SCOPES,
        redirect_uri=flask.url_for(
            "views.oauth2callback", _external=True, _scheme="http"
        ),
    )
    if "code" not in flask.request.args:
        auth_uri = flow.step1_get_authorize_url()
        return flask.redirect(auth_uri)
    else:
        auth_code = flask.request.args.get("code")
        credentials = flow.step2_exchange(auth_code)
        flask.session[f"{current_user.email} credentials"] = credentials.to_json()
        return flask.redirect(flask.url_for("views.export", email=current_user.email))


def get_gcal_service(credentials):
    """
    We need a Google calendar 'service' object to obtain
    list of calendars, busy times, etc.  This requires
    authorization. If authorization is already in effect,
    we'll just return with the authorization. Otherwise,
    control flow will be interrupted by authorization, and we'll
    end up redirected back to /index *without a service object*.
    Then the second call will succeed without additional authorization.
    """
    http_auth = credentials.authorize(httplib2.Http())
    service = discovery.build("calendar", "v3", http=http_auth)
    return service


# route to run the algo
@views.route("/run", methods=["GET"])
@login_required
def run_algo():
    """
    This function is called when the user clicks the run algorithm button.
    It calls the runAssign function from the model.py file.
    The runAssign function takes in the assignments and timeslots and runs the algorithm.
    The finalized slots are then stored in the database.
    :return: The final assignments are being returned.
    """
    user = User.query.filter_by(email=current_user.email).first()
    # credentials = valid_credentials(current_user.email)
    # if not credentials:
    #     return flask.redirect(flask.url_for('views.oauth2callback',_external=True,_scheme="http"))
    # service = get_gcal_service(credentials)
    assignments = [a.serialize() for a in Assignment.query.filter_by(user=user.id)]
    timeslots = [t.serialize() for t in Timeslot.query.filter_by(user=user.id)]
    model.runAssign(assignments, timeslots, user)
    print(
        [a.JsonizableSerialize() for a in Assignment.query.filter_by(user=user.id)]
    )  # settings = service.settings().list().execute()
    # timezone='Asia/Kolkata'
    # for settinfs in settings['items']:
    #     if settinfs['id'] == 'timezone':
    #         timezone=settinfs["value"]
    # plus = pytz.timezone(timezone)
    # assignments = [a.JsonizableSerialize() for a in Assignment.query.filter_by(user=user.id)]
    # plus = datetime.now(plus)
    # plus=str(plus)
    # for slots in finalizedSlots:
    #     if slots["assignment"] is not None:
    #         assignmentId = slots['assignment']
    #         event = {
    #             'summary': assignments[assignmentId-1].get("name"),
    #             'start': {
    #                 'dateTime': dateit(slots.get("startTime"),plus),
    #                 'timezone': timezone
    #             },
    #             'end': {
    #                 'dateTime': dateit(slots["endTime"],plus),
    #                 'timezone': timezone
    #             }
    #         }
    #         event = service.events().insert(calendarId='primary', body=event).execute()
    # rep = (credentials.to_json())
    # rep=json.loads(rep)
    # token = (rep.get("access_token"))
    # requests.post('https://oauth2.googleapis.com/revoke',
    # params={'token': token},
    # headers = {'content-type': 'application/x-www-form-urlencoded'})
    # flask.session.clear()
    return render_template(
        "results.html",
        data=[
            a.JsonizableSerialize() for a in Assignment.query.filter_by(user=user.id)
        ],
    )


@views.route("/googleb9f9364d29bffe94.html")
def verify():
    return render_template("googleb9f9364d29bffe94.html")


@views.route("/export")
@login_required
def export():
    """
    This function is used to export the data from the database to the google calendar
    :return: The user is being redirected to the calendar.
    """
    user = User.query.filter_by(email=current_user.email).first()
    credentials = valid_credentials(current_user.email)
    if not credentials:
        return flask.redirect(
            flask.url_for("views.oauth2callback", _external=True, _scheme="http")
        )
    service = get_gcal_service(credentials)
    finalizedSlots = [t.jserialize() for t in Timeslot.query.filter_by(user=user.id)]
    settings = service.settings().list().execute()
    timezone = "Asia/Kolkata"
    for settinfs in settings["items"]:
        if settinfs["id"] == "timezone":
            timezone = settinfs["value"]
    plus = pytz.timezone(timezone)
    assignments = [
        a.JsonizableSerialize() for a in Assignment.query.filter_by(user=user.id)
    ]
    plus = datetime.now(plus)
    plus = str(plus)
    for slots in finalizedSlots:
        print(slots)
        if slots["assignment"] is not None:
            assignmentId = slots["assignment"]
            event = {
                "summary": assignments[assignmentId - 4].get("name"),
                "start": {
                    "dateTime": dateit(slots.get("startTime"), plus),
                    "timezone": timezone,
                },
                "end": {
                    "dateTime": dateit(slots["endTime"], plus),
                    "timezone": timezone,
                },
            }
            event = service.events().insert(calendarId="primary", body=event).execute()
    rep = credentials.to_json()
    rep = json.loads(rep)
    return flask.redirect("https://calendar.google.com/calendar/")
    # return render_template('exported.html', data=user.serialize())
