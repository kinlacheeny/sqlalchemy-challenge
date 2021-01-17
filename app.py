#################################################
# Step 2 - Climate App 
# JB Kinlacheeny, Homework: sqlalchemy-challenge
# January 16, 2021 
#################################################
import sqlalchemy
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
import datetime as dt
import numpy as np

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect an existing database into a new model
Base = automap_base()

# Reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# find the last date in the db
session = Session(engine)
last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]

# Calculate the date 1 year ago from the last data point in the database
year1 = dt.datetime.strptime(last_date, "%Y-%m-%d")
last_year = year1 - dt.timedelta(days=365)

#################################################
# Flask Setup
#################################################

# Create an app
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def Home():
    """List all available API routes."""
    return (
        f"Welcome to SQL-Alchemy - Hawaii Climate"
        f"Available Routes: <br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start date format: YYYY-MM-DD]<start><br/>"
        f"/api/v1.0/start date format: YYYY-MM-DD<start>/end date format: YYYY-MM-DD<end>"
    )

#################################################
# Create precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    year1 = dt.datetime.strptime(last_date, "%Y-%m-%d")
    last_year = year1 - dt.timedelta(days=365)
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= last_year).all()
    session.close()

    # Create a dictionary using date as key and prcp as value
    precip = []
    for date,prcp in results:
        p = {}
        p["date"] = date
        p["prcp"] = prcp
        precip.append(p)
    
    return jsonify(precip)

#################################################
# Create stations route
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(Measurement.station).distinct().all()
    session.close()

    # Active stations
    active_stations = list(np.ravel(results))
    
    # jsonify
    return jsonify(active_stations)

#################################################
# Create tobs route
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    # Query the dates and tobs of the most active station for the last year of data
    year1 = dt.datetime.strptime(last_date, "%Y-%m-%d")
    last_year = dt.date(2017,8,23) - dt.timedelta(days=365)
    
    active_stations = session.query(Measurement.station, func.count(Measurement.station)).\
        filter(Measurement.date >= last_year).\
            group_by(Measurement.station).\
                order_by(func.count(Measurement.station).desc()).first()
    temps = session.query(Measurement.tobs).\
            filter(Measurement.station == active_stations [0]).\
                filter(Measurement.date >= last_year).all()

    session.close()

    # Return a JSON list of tobs for the previous year
    return_temp = [result[0] for result in temps]
    
    return jsonify(return_temp)

#################################################
@app.route("/api/v1.0/<start>")
def start(start):
    if len(start) == 10:
        session=Session(engine)
        results = session.query(func.min(Measurement.tobs),\
            func.avg(Measurement.tobs),\
                func.max(Measurement.tobs)).\
                    filter(Measurement.date >= start).all()
        session.close()
        return jsonify(results)
    
    return jsonify({"error": f"{start} is an invalid date! Use format (YYYY-MM-DD)."}), 404

# #################################################
# # Run the application
# #################################################
if __name__ == "__main__":
    app.run(debug=True)