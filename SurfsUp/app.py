from flask import Flask, jsonify

import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

app = Flask(__name__)

# connect to the database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# home route
@app.route("/")
def home():
    return (
        f"<center><h2>Welcome to the Hawaii Climate Analysis Local API</h2></center>"
        f"<center><h3>Select from one of the available routes:</h3></center>"
        f"<center>/api/v1.0/precipitation</center>"
        f"<center>/api/v1.0/stations</center>"
        f"<center>/api/v1.0/tobs</center>"
        f"<center>/api/v1.0/start</center>"
    )

# /api/v1.0/precipitation route
@app.route("/api/v1.0/precipitation")
def precip():
    """Return the previous year's precipitation as a JSON."""
    with Session(engine) as session:
        recent_date = session.query(func.max(Measurement.date)).scalar()
        recent_date_dt = dt.datetime.strptime(recent_date, '%Y-%m-%d')
        one_year_ago = recent_date_dt - dt.timedelta(days=365)

        prcp_data = session.query(Measurement.date, Measurement.prcp).\
            filter(Measurement.date >= one_year_ago).\
            order_by(Measurement.date).all()

        Precipitation = {date: prcp for date, prcp in prcp_data}

    return jsonify(Precipitation)

# /api/v1.0/stations route
@app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations as a JSON."""
    with Session(engine) as session:
        stations_data = session.query(Station.station).all()
        station_list = list(np.ravel(stations_data))
    return jsonify(station_list)

# /api/v1.0/tobs route
@app.route("/api/v1.0/tobs")
def temperatures():
    """Return the previous year's temperature observations as a JSON."""
    with Session(engine) as session:
        recent_date = session.query(func.max(Measurement.date)).scalar()
        recent_date_dt = dt.datetime.strptime(recent_date, '%Y-%m-%d')
        one_year_ago = recent_date_dt - dt.timedelta(days=365)

        most_active_station = session.query(Measurement.station).\
            group_by(Measurement.station).\
            order_by(func.count(Measurement.id).desc()).\
            first()[0]

        tobs_data = session.query(Measurement.tobs).\
            filter(Measurement.station == most_active_station).\
            filter(Measurement.date >= one_year_ago).all()

        temperatureList = list(np.ravel(tobs_data))

    return jsonify(temperatureList)

# /api/v1.0/<start> route
@app.route("/api/v1.0/<start>")
def temp_start(start):
    """Return TMIN, TAVG, and TMAX for dates greater than or equal to the start date."""
    with Session(engine) as session:
        # Query to calculate TMIN, TAVG, and TMAX
        results = session.query(
            func.min(Measurement.tobs),
            func.avg(Measurement.tobs),
            func.max(Measurement.tobs)
        ).filter(Measurement.date >= start).all()

        # Unpack the results into a dictionary
        temp_data = {
            "start_date": start,
            "min_temp": results[0][0],
            "avg_temp": results[0][1],
            "max_temp": results[0][2]
        }

    return jsonify(temp_data)

# /api/v1.0/<start>/<end> route
@app.route("/api/v1.0/<start>/<end>")
def temp_start_end(start, end):
    """Return TMIN, TAVG, and TMAX for dates between the start and end dates, inclusive."""
    with Session(engine) as session:
        # Query to calculate TMIN, TAVG, and TMAX for the date range
        results = session.query(
            func.min(Measurement.tobs),
            func.avg(Measurement.tobs),
            func.max(Measurement.tobs)
        ).filter(Measurement.date >= start).filter(Measurement.date <= end).all()

        # Unpack the results into a dictionary
        temp_data = {
            "start_date": start,
            "end_date": end,
            "min_temp": results[0][0],
            "avg_temp": results[0][1],
            "max_temp": results[0][2]
        }

    return jsonify(temp_data)


# app launcher
if __name__ == '__main__':
    app.run(debug=True)
