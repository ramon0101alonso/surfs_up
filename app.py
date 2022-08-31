
import datetime as dt
import numpy as np
import pandas as pd

# dependencies we need for SQLAlchemy
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

#dependencies we need for flask
from flask import Flask, jsonify

#access the SQLite database
engine = create_engine("sqlite:///hawaii.sqlite")

#reflect the database into our classes
Base = automap_base()
Base.prepare(engine, reflect=True)

#save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

#create session link from Python to our database
session = Session(engine)

#set up flask
app = Flask(__name__)

#create the welcome route the google page and then images, videos
@app.route("/")

#add routing info for each route

def welcome():
    return(
    '''
    Welcome to the Climate Analysis API!
    Available Routes:
    /api/v1.0/precipitation
    /api/v1.0/stations
    /api/v1.0/tobs
    /api/v1.0/temp/start/end
    ''')

#new route that will return the precipitation data for the last year.
@app.route("/api/v1.0/precipitation")

#prepcipatation function that calculates the date one year ago from the most recent date in database with query
#./ gives you a new line
def precipitation():
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    precipitation = session.query(Measurement.date, Measurement.prcp).\
      filter(Measurement.date >= prev_year).all()
      #this line creates a dictionary with the date as key and preicipitation as the value
    precip = {date: prcp for date, prcp in precipitation}
    return jsonify(precip)

#station route
@app.route("/api/v1.0/stations")
#function with query to get all of the stations in database
def stations():
    results = session.query(Station.station).all()
    #see notes in word notes module 9 this is a one dimensional array result converted into a list, then converted into json
    stations = list(np.ravel(results))
    return jsonify(stations=stations)

#route to return the temperature observations for the previous year
@app.route("/api/v1.0/tobs")
#function to calculate the date one year ago from the last date in the database with query to primary station for all
def temp_monthly():
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    results = session.query(Measurement.tobs).\
      filter(Measurement.station == 'USC00519281').\
      filter(Measurement.date >= prev_year).all()
    #unravel just like in stations route convert into one dimensional array and the jsonify
    temps = list(np.ravel(results))
    return jsonify(temps=temps)

#to see the output, flask run, and then add the app.route to the end of the website

#route to report the in avg and max temp with both a starting and ending date
@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")

#function with start and end parameter.  
def stats(start=None, end=None):
    #query to get min, avg, max temp from sqlite db
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    #query sel then unravel into one dimensional array and convert to list
    # the * indicates there will be multiple results for our query, min, avg and max temp
    if not end:
        results = session.query(*sel).\
            filter(Measurement.date >= start).all()
        temps = list(np.ravel(results))
        #return jsonify(temps=temps) converting one-dimensioal array and convert them to a list
        return jsonify(temps)

    #takes the results from one dimensional sel and gets the start and end date data
    results = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    temps = list(np.ravel(results))
    return jsonify(temps)

    #/api/v1.0/temp/start/end route gives you null values so you have to insert the start date and end date to get results
    #/api/v1.0/temp/2017-06-01/2017-06-30 this has start and end dates