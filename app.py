### Climate App
### author: Inna Baloyan
### date:   July 28,2018

import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, desc
# Maintain the same connection per thread
###from sqlalchemy.pool import SingletonThreadPool

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
### engine = create_engine("sqlite:///Resources/hawaii.sqlite")
###engine = create_engine('sqlite:///Resources/hawaii.sqlite', poolclass=SingletonThreadPool, pool_size=50)  
engine = create_engine('sqlite:///Resources/hawaii.sqlite', connect_args={'check_same_thread': False})

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
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date/<start_date><br/>"
        f"/api/v1.0/start_date/end_date/<start_date>/<end_date>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return a dictionary of all percipitation scores for the previous year"""
    # Query all percipitation scores for the year
    prcp_data_results = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date < '2017-08-24').filter(Measurement.date > '2016-08-23').\
    group_by(Measurement.date).order_by(desc(Measurement.date)).all()

    # Create a dictionary from the row data and append to a list of all percipitation scores
    all_prcp_data = []
    for prcp_score in prcp_data_results:
        prcp_dict = {}

        # Use `date` as a key and `prcp` as a value
        prcp_dict[prcp_score.date] = prcp_score.prcp
        
        all_prcp_data.append(prcp_dict)

    # Return a JSON representation of the dictionary
    return jsonify(all_prcp_data)
    
@app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations from the dataset"""
    # Query all stations
    station_results = session.query(Station.name).all()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(station_results))

    # Return a JSON representation of the list
    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return a dictionary of all temperature observataions for the previous year"""
    # Query all temperatures for the last year
    tobs_data_results = session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.date < '2017-08-24').filter(Measurement.date > '2016-08-23').\
    group_by(Measurement.date).order_by(desc(Measurement.date)).all()

    # Create a dictionary from the row data and append to a list of all temperatures
    all_tobs_data = []
    for tobs_record in tobs_data_results:
        tobs_dict = {}

        # Use `date` as a key and `tobs` as a value
        tobs_dict[tobs_record.date] = tobs_record.tobs
        
        all_tobs_data.append(tobs_dict)

    # Return a JSON representation of the dictionary
    return jsonify(all_tobs_data)

@app.route("/api/v1.0/start_date/<start_date>")
def daily_normals(start_date):
    """Return TMIN, TAVG, and TMAX for all dates greater than and equal to the start date"""
    # Will accept start date in the format '%m-%d' 
    # Create a query that will calculate and return the daily normals, 
    # i.e. the averages for tmin, tmax, and tavg for all historic data which is later or equal to a specific month and day        
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    daily_normals_data = session.query(*sel).filter(func.strftime("%m-%d", Measurement.date) >= start_date).all()
    number_of_elements = print(str(len(daily_normals_data)))

    # Create a dictionary from the row data and append to a list of all daily normals
    all_daily_normals = []
    for tstats_record in daily_normals_data:
        (min_tobs, max_tobs, avg_tobs) = tstats_record
        daily_normals_dict = {}
        daily_normals_dict["avg"] = avg_tobs 
        daily_normals_dict["max"] = max_tobs 
        daily_normals_dict["min"] = min_tobs 
        all_daily_normals.append(daily_normals_dict)

    # Return a JSON representation of the dictionary
    return jsonify(all_daily_normals)

# print(daily_normals('07-15'))

@app.route("/api/v1.0/start_date/end_date/<start_date>/<end_date>")
def calc_temps(start_date, end_date):
    """Return the list: TMIN, TAVG, and TMAX for the dates between the start and date inclusively"""    
    # Will accept start date and end date in the format '%Y-%m-%d' 
    # and return the minimum, average, and maximum temperatures for that range of dates   
    vacation_daily_normals = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

    # Convert list of tuples into normal list
    ###vacation_stats = list(np.ravel(vacation_daily_normals))

    # Create a dictionary from the row data and append to a list of all daily normals
    all_vac_daily_normals = []
    for vac_stats in vacation_daily_normals:
        (min_tmp, max_tmp, avg_tmp) = vac_stats
        daily_vac_dict = {}
        daily_vac_dict["avg"] = avg_tmp 
        daily_vac_dict["max"] = max_tmp 
        daily_vac_dict["min"] = min_tmp 
        all_vac_daily_normals.append(daily_vac_dict)

    # Return a JSON representation of the list
    return jsonify(all_vac_daily_normals)

#print(calc_temps('2017-07-15', '2017-07-22'))

if __name__ == '__main__':
    app.run(debug=True)

################### The End ######################################  