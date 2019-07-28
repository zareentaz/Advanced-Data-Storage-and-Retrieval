# 1. import Flask
from flask import Flask, jsonify
import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func




#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")


# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

keys = Base.classes.keys()

global Measurement
if "measurement" not in keys:
    print("measurement does not exist in keys. Exiting the program")
    exit(0)
else:    
    print("measurement exists in keys. Proceeding...")
    # Save reference to the table
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

# 3. Define what to do when a user hits the index route
@app.route("/")
def home():
    print("Server received request for 'Home' page...")
    return (
            f"Available Routes:<br/>"
            f"/api/v1.0/precipitation<br/>"
            f"/api/v1.0/stations<br/>"
            f"/api/v1.0/tobs<br/>"
            f"/api/v1.0/<start><br/>"
            f"/api/v1.0/<start>/<end>"
    ) 

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    latest_date=session.query(Measurement.date).order_by(Measurement.date.desc()).first().date
    year_ago = dt.datetime.strptime(latest_date,'%Y-%m-%d') - dt.timedelta(days=365)
    date_prcp_measure=session.query(Measurement.date,Measurement.prcp).\
                       filter(Measurement.date >= year_ago).\
                        order_by(Measurement.date).all()
    
   # Create a dictionary from the row data   
    date_prcp = []
    for date, prcp in date_prcp_measure:
        Measurement_dict = {}
        Measurement_dict["date"] = date
        Measurement_dict["prcp"] = prcp
        date_prcp.append(Measurement_dict)

    return jsonify(date_prcp)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    station=session.query(Station.station).all()
    
    # Convert list of tuples into normal list
    all_stations = list(np.ravel(station))
    return jsonify(station)


@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    latest_date=session.query(Measurement.date).order_by(Measurement.date.desc()).first().date
    year_ago = dt.datetime.strptime(latest_date,'%Y-%m-%d') - dt.timedelta(days=365)
    date_tobs=session.query(Measurement.date,Measurement.tobs).\
              filter(Measurement.date >= year_ago).\
              order_by(Measurement.date).all()
    
    tobs_date = []
    for date, tobs in date_tobs:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        tobs_date.append(tobs_dict)
  
    #tobs=list(np.ravel(date_tobs))
    return jsonify(tobs_date)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")    
def temp(start=None,end=None):
                
    session = Session(engine)
    if end!= None:
        temp_start_end = session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).\
                          filter(Measurement.date >= start).filter(Measurement.date <= end).all()


#When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
    else:
        temp_start_end = session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).\
                         filter (Measurement.date >= start).all()
   #convert list of tuple into normal list
    temp_start_end_rav = list(np.ravel(temp_start_end))
    return jsonify(temp_start_end_rav)
           
           
           
if __name__ == "__main__":
    app.run(debug=True)