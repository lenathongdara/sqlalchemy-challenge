# Import the dependencies.
import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///SurfsUp/Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
measurements = Base.classes.measurement
stations = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def home():
    """Lists all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start/2014-01-26<br/>"
        f"/api/v1.0/start/2014-01-26/end/2017-02-18"
    )

@app.route("/api/v1.0/precipitation")
def precipations():
    """Returns precipitation data for the last year in the database."""
    
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Query precipitation data for the last year of data. 
    precipitation = session.query(measurements.date, measurements.prcp).\
        filter(measurements.date >= '2016-08-23').\
        order_by(measurements.date).all()
    
    session.close()

    # Save the query results as a list of dictionaries with the date as the key and value as the precipitation and return the jsonified data. 
    prcp_dicts = [{date: prcp} for date, prcp in precipitation]
    return jsonify(prcp_dicts)
    

@app.route("/api/v1.0/stations")
def stations_list():
   """Returns all of the stations in the database."""
  
   session = Session(engine)

   # Query all of the stations in the database.  
   stations_list = session.query(stations.station).all()

   session.close()
   
   # Save the query results as a one-dimensional list and return the jsonified data. 
   stations_list_1 = list(np.ravel(stations_list))
   return jsonify(stations_list_1)


@app.route("/api/v1.0/tobs")
def tobs_list():
    """Returns temperature data for the most active station for the last year in the database."""

    session = Session(engine)

    # Query temperature data for the most active station. 
    most_active_temps = session.query(measurements.tobs).\
        filter(measurements.date >= '2016-08-23').\
        filter(measurements.station == 'USC00519281').all()
    
    session.close()

    # Save the query results as a one-dimensional list and return the jsonified data. 
    temeperature_list = list(np.ravel(most_active_temps))
    return jsonify(temeperature_list)


@app.route("/api/v1.0/start/<start>")
def start_date(start):
    """Returns minimum, average, and maximum temperatures calculated from the given start date to the end of the dataset."""
    
    session = Session(engine)

    # Save the given start date as a parameter for the URL.
    date_format = dt.datetime.strptime(start, '%Y-%m-%d').date()
   
    # Query the minimum, average, and maximum temperatures from the given start date to the end of the dataset. 
    sel = [func.min(measurements.tobs), func.avg(measurements.tobs), func.max(measurements.tobs)]
    start_query = session.query(*sel).\
        filter(measurements.date >= date_format).all()
    
    session.close()
    
    # Save the query results as a one-dimensional list, then dictionary and return the jsonified data. 
    start_list = list(np.ravel(start_query))
    start_dict = {'Minimum Temperature': start_list[0],
                  'Average Temperature': start_list[1],
                  'Maximum Temperature': start_list[2]}
    return jsonify(start_dict)


@app.route("/api/v1.0/start/<start>/end/<end>")
def startend_date(start, end):
    """Returns minimum, average, and maximum temperatures calculated from the given start date to the given end date."""

    session = Session(engine)

    # Save the given start date and end date as parameters for the URL.
    start_date_format = dt.datetime.strptime(start, '%Y-%m-%d').date()
    end_date_format = dt.datetime.strptime(end, '%Y-%m-%d').date()
   
    # Query the minimum, average, and maximum temperatures from the given start date to the given date.
    sel = [func.min(measurements.tobs), func.avg(measurements.tobs), func.max(measurements.tobs)]
    startend_query = session.query(*sel).\
        filter(measurements.date >= start_date_format).\
        filter(measurements.date <= end_date_format).all()
    
    session.close()
    
    # Save the query results as a one-dimensional list, then dictionary and return the jsonified data. 
    startend_list = list(np.ravel(startend_query))
    startend_dict = {'Minimum Temperature': startend_list[0],
                  'Average Temperature': startend_list[1],
                  'Maximum Temperature': startend_list[2]}
    return jsonify(startend_dict)

if __name__ == '__main__':
    app.run(debug=True)
    