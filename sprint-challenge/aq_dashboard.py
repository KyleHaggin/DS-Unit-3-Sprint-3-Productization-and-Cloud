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


def filter():
    output = Record.query.filter(Record.value >= 10).all()
    return output


@APP.route('/')
def root():
    output = filter()
    return str(output)


# basedir = os.path.abspath(os.path.dirname(__file__))
# APP.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(
#     basedir, 'data.sqlite')
APP.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
DB = SQLAlchemy(APP)


class Record(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    datetime = DB.Column(DB.String(25))
    value = DB.Column(DB.Float, nullable=False)

    def __repr__(self):
        return (
            'Time {} --- Value {}'.format(self.datetime, self.value)
            )


@APP.route('/refresh')
def refresh():
    """Pull fresh data from Open AQ and replace existing data."""
    DB.drop_all()
    DB.create_all()
    data = datetime_val_data()
    hldr = []
    for x in range(len(data)):
        hldr_datetime, hldr_value = data[x]
        hldr_datetime = str(hldr_datetime)
        inserted = Record(datetime=hldr_datetime, value=hldr_value)
        DB.session.add(inserted)
    DB.session.commit()
    return 'Data refreshed!'
