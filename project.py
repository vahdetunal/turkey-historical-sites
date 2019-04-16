#!/usr/bin/env python3
from flask import Flask, render_template, url_for, request, redirect, flash

from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, City, Site

app = Flask(__name__)

# Create the engine for DB connection
engine = create_engine('sqlite:///historicalsites.db')

# Create a DB session
Session = sessionmaker(bind=engine)
session = Session()


# Show all cities
@app.route('/')
def show_cities():
    # Get cities from the database
    cities = session.query(City).order_by(asc(City.name))
    return render_template('cities.html', cities=cities)


# Show historical sites within a city
@app.route('/<int:city_id>')
def show_sites(city_id):
    return "Historical sites in {}".format(city_id)


# Show a historical site
@app.route('/<int:city_id>/<int:site_id>')
def show_historical_site(city_id, site_id):
    return "Historical site {} in city {}".format(site_id, city_id)


# Add a new city
@app.route('/new', methods=['GET', 'POST'])
def new_city():
    return "Add a new city"


# Edit a city
@app.route('/<int:city_id>/edit', methods=['GET', 'POST'])
def edit_city(city_id):
    return "Edit the city {}.".format(city_id)


# Delete a city
@app.route('/<int:city_id>/delete', methods=['GET', 'POST'])
def delete_city(city_id):
    return "Delete the city {}.".format(city_id)


# Add a historical site
@app.route('/<int:city_id>/new', methods=['GET', 'POST'])
def new_historical_site(city_id):
    return "Add a new historlcal site in city {}.".format(city_id)


# Edit a historical site
@app.route('/<int:city_id>/<int:site_id>/edit', methods=['GET', 'POST'])
def edit_historical_site(city_id, site_id):
    return "Edit the historical site {} in city {}.".format(site_id, city_id)


# Edit a historical site
@app.route('/<int:city_id>/<int:site_id>/delete', methods=['GET', 'POST'])
def delete_historical_site(city_id, site_id):
    return "Delete the historical site {} in city {}.".format(site_id, city_id)


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
