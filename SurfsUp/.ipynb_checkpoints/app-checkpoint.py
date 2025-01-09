# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt

from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session

#################################################
# Database Setup
#################################################
# Connect to the SQLite database
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    return (
        f"Welcome to the Hawaii Climate API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the last 12 months of precipitation data."""
    # Find the most recent date in the dataset
    recent_date = session.query(func.max(Measurement.date)).scalar()
    recent_date = dt.datetime.strptime(recent_date, '%Y-%m-%d')
    one_year_ago = recent_date - dt.timedelta(days=365)

    # Query for the last 12 months of precipitation data
    prcp_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_ago).\
        order_by(Measurement.date).all()

    # Convert to dictionary
    precipitation_dict = {date: prcp for date, prcp in prcp_data}

    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations():
    """Return a list of all weather stations."""
    results = session.query(Station.station).all()

    # Unpack results into a list
    station_list = [r[0] for r in results]

    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return the last 12 months of temperature observations for the most active station."""
    # Find the most active station
    most_active_station = session.query(Measurement.station, func.count(Measurement.id)).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.id).desc()).\
        first()[0]

    # Find the most recent date and calculate one year ago
    recent_date = session.query(func.max(Measurement.date)).scalar()
    recent_date = dt.datetime.strptime(recent_date, '%Y-%m-%d')
    one_year_ago = recent_date - dt.timedelta(days=365)

    # Query the last 12 months of TOBS data for the most active station
    tobs_data = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station).\
        filter(Measurement.date >= one_year_ago).\
        order_by(Measurement.date).all()

    # Convert to list of dictionaries
    tobs_list = [{"date": date, "tobs": tobs} for date, tobs in tobs_data]

    return jsonify(tobs_list)

# Close session when Flask app shuts down
@app.teardown_appcontext
def cleanup(exception=None):
    session.close()

if __name__ == "__main__":
    app.run(debug=True)
