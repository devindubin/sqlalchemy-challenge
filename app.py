import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session, Query
from sqlalchemy import create_engine, func
import datetime as dt

from flask import Flask, jsonify
##########################################################3
#Database Setup
#########################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
conn = engine.connect()

Base = automap_base()
Base.prepare(engine,reflect=True)

measurement = Base.classes.measurement
station = Base.classes.station

##########################################################33
# Flask Setup
##########################################################
app = Flask(__name__)

@app.route("/")
def home():
    print('server going home')
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )

@app.route("/about")
def about():
    return "HI SHERIDAN"


@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)

    results = session.query(measurement.date,measurement.prcp).all()

    session.close()

    precip = dict(results)
    return jsonify(precip)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)

    results = session.query(station.station,station.name).all()

    return jsonify(results)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    first_date = dt.datetime.strptime((Query(measurement).with_session(session).order_by(measurement.date.desc()).first().date),"%Y-%m-%d")

    year_before = first_date - dt.timedelta(days= 365)

    most_active_list = session.query(measurement.station,func.count(measurement.station)).group_by(measurement.station).order_by(func.count(measurement.station).desc()).all()
    most_active = most_active_list[0][0]

    results = session.query(measurement.date,measurement.tobs).filter(measurement.station == most_active,measurement.date > year_before).all()

    session.close()

    results = list(results)

    return (jsonify(results))

@app.route("/api/v1.0/<start>")
def start_year(start):
    session = Session(engine)

    results = session.query(func.min(measurement.tobs),func.avg(measurement.tobs),func.max(measurement.tobs)).filter(measurement.date >= start).all()

    session.close()

    return jsonify(results)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start,end):
    session = Session(engine)

    results = session.query(func.min(measurement.tobs),func.avg(measurement.tobs),func.max(measurement.tobs)).filter(measurement.date >= start, measurement.date <= end).all()

    session.close()

    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)