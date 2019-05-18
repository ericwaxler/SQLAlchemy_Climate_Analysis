import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

import datetime as dt
from dateutil.relativedelta import relativedelta

from flask import Flask, jsonify


engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)


app = Flask(__name__)

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Returns precipitation data over the last year"""

    maxdate = session.query(func.max(Measurement.date)).scalar()
    startdate = (dt.datetime.strptime(maxdate, '%Y-%m-%d') - relativedelta(years=1)).date()
    results = session.query(Measurement.date,Measurement.prcp).filter(Measurement.date >= startdate).all()
    all_prcp = []
    prcp_dict = {}

    for date, prcp in results:
        prcp_dict.update({date:prcp})
        
    all_prcp.append(prcp_dict)
    return jsonify(all_prcp)


@app.route("/api/v1.0/stations")
def station():
    """Returns all stations"""
    results = session.query(Station.station,Station.name,Station.latitude,Station.longitude,Station.elevation).all()
    all_stations = []
    for station, name, latitude, longitude, elevation in results:
        sta_dict = {}
        sta_dict['elevation'] = elevation
        sta_dict['longitude'] = longitude
        sta_dict['latitude'] = latitude
        sta_dict['name'] = name
        sta_dict['station'] = station
        
        all_stations.append(sta_dict)
        
    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def tobs():
    """Return temperature measurements from the last year of data"""
    maxdate = session.query(func.max(Measurement.date)).scalar()
    startdate = (dt.datetime.strptime(maxdate, '%Y-%m-%d') - relativedelta(years=1)).date()

    results = session.query(Measurement.date,Measurement.tobs).filter(Measurement.date >= startdate).all()
    all_tobs = []
    for date, tobs in results:
        tobs_dict = {}
        tobs_dict['date'] = date
        tobs_dict['temp'] = tobs
        all_tobs.append(tobs_dict)

    return jsonify(all_tobs)

@app.route("/api/v1.0/<start>")
def desc_start(start):
    """TMIN, TAVG, and TMAX for a list of dates."""
    
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    stats = []
    sd = {}
    sd.update({'Minimum':results[0][0]})
    sd.update({'Average':results[0][1]})
    sd.update({'Maximum':results[0][2]})
    stats.append(sd)

    return jsonify(stats)

@app.route("/api/v1.0/<start>/<end>")
def desc_start_end(start, end):
    """TMIN, TAVG, and TMAX for a list of dates."""
    
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    stats = []
    sd = {}
    sd.update({'Minimum':results[0][0]})
    sd.update({'Average':results[0][1]})
    sd.update({'Maximum':results[0][2]})
    stats.append(sd)

    return jsonify(stats)

if __name__ == '__main__':
    app.run(debug=True)
