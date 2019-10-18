"""OpenAQ Air Quality Dashboard with Flask."""
from flask import Flask, request
import openaq
import os
from flask_sqlalchemy import SQLAlchemy

APP = Flask(__name__)

api = openaq.OpenAQ()


def datetime_val_data():
    data = []
    status, body = api.measurements(city='Los Angeles', parameter='pm25')
    results = body['results']
    for x in range(len(results)):
        results_time = results[x]['date']
        hldr = results_time['utc'], results[x]['value']
        data.append(hldr)
    return data


@APP.route('/')
def root():
    output = datetime_val_data()
    return str(output)


basedir = os.path.abspath(os.path.dirname(__file__))
APP.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(
    basedir, 'data.sqlite')
DB = SQLAlchemy(APP)


class Record(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    datetime = DB.Column(DB.String(25))
    value = DB.Column(DB.Float, nullable=False)

    def __repr__(self):
        return '<Time {}>'.format()


@APP.route('/refresh')
def refresh():
    """Pull fresh data from Open AQ and replace existing data."""
    DB.drop_all()
    DB.create_all()
    # TODO Get data from OpenAQ, make Record objects with it, and add to db
    DB.session.commit()
    return 'Data refreshed!'
