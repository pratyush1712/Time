from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from . import db
import json
import sys
from website import model
#sys.path.append('D:\flask\Flask-Web-App-Tutorial\website\model.py') #folder which contains model, snn etc.,

views = Blueprint('views', __name__)

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
import httplib2   # used in oauth2 flow
from apiclient import discovery




# This variable specifies the name of a file that contains the OAuth 2.0
# information for this application, including its client_id and client_secret.
#CLIENT_SECRETS_FILE = "client_secret.json"
CLIENT_SECRET_FILE = 'client_id.json'  ## You'll need this

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
SCOPES = ['https://www.googleapis.com/auth/calendar']
API_SERVICE_NAME = 'calendar'
API_VERSION = 'v3'


# Note: A secret key is included in the sample so that it works.
# If you use this code in your application, replace this with a truly secret
# key. See https://flask.palletsprojects.com/quickstart/#sessions.

def dateit(date, plus):
    # from 2022-01-17 09:59:00 to 2015-05-28T09:00:00-07:00
    sign = ''
    for char in (plus.split(":")[2])[2:]:
        sign+=char
    return date.split(' ')[0] + 'T' + date.split(' ')[1]+str(sign)

def timebreak(startTime, endTime, user):
    # the response of the query
    resp = []
    # calculate the number of blocks required
    secDiff = (endTime-startTime).total_seconds()
    minuteDiff = secDiff/60
    numBlocks = int(minuteDiff//(user.maxFocusTime*60))
    # create Timeslot objects
    index = 0
    for block in range(numBlocks):
        a=startTime + block*timedelta(minutes=user.maxFocusTime*60*6/5)
        index+=1
        if index!=5:
            # create a Timeslot object
            slot = Timeslot(startTime=a, endTime=a+timedelta(minutes=(user.maxFocusTime*60)), assignment = None, user=user.id)
            db.session.add(slot)
            db.session.commit()
            # add the new timeslot to response
            resp.append(slot.jserialize())
        else:
            slot = Timeslot(startTime=a+timedelta(minutes=user.maxFocusTime*1/3*60), endTime=a+timedelta(minutes=user.maxFocusTime*60*2/3), assignment = None, user=user.id)
            db.session.add(slot)
            db.session.commit()
            index = 0
    return resp

@views.route("/")
@login_required
def init():
    return render_template("home.html",email=current_user.email, name=current_user.name)

@views.route("/<email>", methods=['GET','POST'])
@login_required
def profile(email):
    user = User.query.filter_by(email=email).first()
    if request.method == 'POST':
        maxFocusTime = request.form.get("maxFocusTime")
        preferedWorkTime = request.form.get("preferedWorkTime")
        user.preferedWorkTime=preferedWorkTime
        user.maxFocusTime = maxFocusTime
        db.session.commit()
        return render_template('home.html', data=user.serialize())
    return render_template('user-info.html', data=user.serialize())

def credentials_to_dict(credentials):
    return {'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes}

@views.route("/<email>/timeslots/", methods=['GET','POST'])
def timeslots(email):
    user = User.query.filter_by(email=email).first()
    if request.method == 'POST':
        startTime = request.form.get("startTime")
        endTime = request.form.get("endTime")
        resp = timebreak((datetime(
                month=int(startTime.split('-')[1]),
                day=int((startTime.split('-')[2]).split("T")[0]),
                year=int((startTime.split('-')[0])),
                hour=int((startTime.split('T')[1]).split(':')[0]),
                minute=int((startTime.split('T')[1]).split(':')[1])
            )), (datetime(
                month=int(endTime.split('-')[1]),
                day=int((endTime.split('-')[2]).split("T")[0]),
                year=int((endTime.split('-')[0])),
                hour=int((endTime.split('T')[1]).split(':')[0]),
                minute=int((endTime.split('T')[1]).split(':')[1])
            )), user)
        if Timeslot.query.filter_by(user=user.id).first() is not None:
            return render_template("timeslots.html",data = [t.jserialize() for t in Timeslot.query.filter_by(user=user.id)], asn = [a.JsonizableSerialize() for a in Assignment.query.filter_by(user=user.id)], email=email)
    return render_template("timeslots.html", data = [t.jserialize() for t in Timeslot.query.filter_by(user=user.id)], email=email)

@views.route("/<email>/assignments/", methods=['GET','POST', 'DELETE'])
def assignment(email):
    user = User.query.filter_by(email=email).first()
    if request.method == 'POST':
        #body = json.loads(request.data)
        duedate = request.form.get("duedate")
        amtofTime = request.form.get("amount of time")
        hours = int(amtofTime.split(":")[0])
        minutes = int(amtofTime.split(":")[1])
        priority = request.form.get("priority")
        new_assignment = Assignment(
            name=request.form.get("name"),
            duedate=(datetime(
                month=int(duedate.split('-')[1]),
                day=int((duedate.split('-')[2]).split("T")[0]),
                year=int((duedate.split('-')[0])),
                hour=int((duedate.split('T')[1]).split(':')[0]),
                minute=int((duedate.split('T')[1]).split(':')[1])
            )),
            amtOfTime = timedelta(hours=hours, minutes=minutes),
            user=user.id,
            priority=priority
        )
        db.session.add(new_assignment)
        db.session.commit()
        return render_template("assignment.html", data = [a.JsonizableSerialize() for a in Assignment.query.filter_by(user=user.id)], email=email)
    return render_template("assignment.html", data = [a.JsonizableSerialize() for a in Assignment.query.filter_by(user=user.id)], email=email)


def valid_credentials(email):
    """
    Returns OAuth2 credentials if we have valid
    credentials in the session.  This is a 'truthy' value.
    Return None if we don't have credentials, or if they
    have expired or are otherwise invalid.  This is a 'falsy' value.
    """
    if f'{email} credentials' not in flask.session:
        return None

    credentials = client.OAuth2Credentials.from_json(
        flask.session[f'{email} credentials'])

    if (credentials.invalid or
        credentials.access_token_expired):
        return None
    return credentials

@views.route('/oauth2callback')
@login_required
def oauth2callback():
    """
    The 'flow' has this one place to call back to.  We'll enter here
    more than once as steps in the flow are completed, and need to keep
    track of how far we've gotten. The first time we'll do the first
    step, the second time we'll skip the first step and do the second,
    and so on.
    """
    flow =  client.flow_from_clientsecrets(
        CLIENT_SECRET_FILE,
        scope= SCOPES,
        redirect_uri=flask.url_for('views.oauth2callback', _external=True,_scheme="https"))
    if 'code' not in flask.request.args:
        auth_uri = flow.step1_get_authorize_url()
        return flask.redirect(auth_uri)
    else:
        auth_code = flask.request.args.get('code')
        credentials = flow.step2_exchange(auth_code)
        flask.session[f'{current_user.email} credentials'] = credentials.to_json()
        return flask.redirect(flask.url_for('views.run_algo', email=current_user.email))

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
    service = discovery.build('calendar', 'v3', http=http_auth)
    return service

# route to run the algo
@views.route("/<email>/run", methods=['GET'])
def run_algo(email):
    user = User.query.filter_by(email=email).first()
    credentials = valid_credentials(email)
    if not credentials:
        return flask.redirect(flask.url_for('views.oauth2callback',_external=True,_scheme="https"))
    service = get_gcal_service(credentials)
    assignments = [a.serialize() for a in Assignment.query.filter_by(user=user.id)]
    timeslots = [t.serialize() for t in Timeslot.query.filter_by(user=user.id)]
    model.runAssign(assignments, timeslots,user)
    finalizedSlots = [t.jserialize() for t in Timeslot.query.filter_by(user=user.id)]
    settings = service.settings().list().execute()
    timezone='Asia/Kolkata'
    for settinfs in settings['items']:
        if settinfs['id'] == 'timezone':
            timezone=settinfs["value"]  
    plus = pytz.timezone(timezone)
    assignments = [a.JsonizableSerialize() for a in Assignment.query.filter_by(user=user.id)]
    plus = datetime.now(plus)
    plus=str(plus)
    print(assignments)
    for slots in finalizedSlots:
        print(slots["assignment"])
        if slots["assignment"] is not None:
            assignmentId = slots['assignment']
            event = {
                'summary': assignments[assignmentId-2].get("name"),
                'start': {
                    'dateTime': dateit(slots.get("startTime"),plus),
                    'timezone': timezone
                },
                'end': {
                    'dateTime': dateit(slots["endTime"],plus),
                    'timezone': timezone
                }
            }
            print(event)
            event = service.events().insert(calendarId='primary', body=event).execute()
    rep = (credentials.to_json())
    rep=json.loads(rep)
    token = (rep.get("access_token"))
    #requests.post('https://oauth2.googleapis.com/revoke',
    #params={'token': token},
    #headers = {'content-type': 'application/x-www-form-urlencoded'})
    #flask.session.clear()
    return render_template('results.html', data=[a.JsonizableSerialize() for a in Assignment.query.filter_by(user=user.id)])

@views.route('/googleb9f9364d29bffe94.html')
def verify():
    return render_template('googleb9f9364d29bffe94.html')


if __name__ == "__main__":
    #port = int(os.environ.get("PORT", 5000))
    #app.run(host='0.0.0.0', port=port)
    app.run(host='localhost',port=8080)
