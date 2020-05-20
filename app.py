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
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Station = Base.classes.station
Measurement = Base.classes.measurement

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
        f"Available Routes</br>"
        f"/api/v1.0/station</br>"
        f"/api/v1.0/precipitation</br>"
        f"/api/v1.0/stations</br>"
        f"/api/v1.0/tobs"
    )


@app.route("/api/v1.0/station")
def station():
    # Create our session (link) from Python to the DB
    session = Session(engine)

   
    # Query all stations
    results = session.query(Station.station).all()

    session.close()

    # Convert list of tuples into normal list
    all_names = list(np.ravel(results))

    return jsonify(all_names)




@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    maxdate = session.query(func.max(func.strftime("%Y-%m-%d", Measurement.date))).all()
    tmpdate = list(np.ravel(maxdate))[0]
    tmpdate = dt.datetime.strptime(tmpdate, '%Y-%m-%d')
    year = dt.timedelta(days=365)
    begdate = tmpdate - year
   # enddate = tmpdate
    
   
    # Query all measurements
    results = session.query(Measurement.date, Measurement.prcp)\
                .filter(Measurement.date >begdate)\
                .group_by(Measurement.date)\
                .order_by(Measurement.date).all()

    session.close()
    rainDict = {}
    for result in results:
        rainDict.update({result.date:result.prcp})



    return jsonify(rainDict)




@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

   
    # Query all stations
    results = session.query(Station.station).all()

    session.close()

    # Convert list of tuples into normal list
    all_names = list(np.ravel(results))

    return jsonify(all_names)
    
    
    
@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Query all temperature
    qry_active_station = session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()

    session.close()
    
    most_active = qry_active_station[0][0]

    session = Session(engine)

    maxdate = session.query(func.max(func.strftime("%Y-%m-%d", Measurement.date))).all()
    tmpdate = list(np.ravel(maxdate))[0]
    tmpdate = dt.datetime.strptime(tmpdate, '%Y-%m-%d')
    year = dt.timedelta(days=365)
    begdate = tmpdate - year

    

    session.close()

    session = Session(engine)

    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= begdate).\
            filter(Measurement.station == most_active).all()

    session.close()

    qry_results = list(np.ravel(results))

    return jsonify(qry_results)



   


if __name__ == '__main__':
    app.run(debug=True)