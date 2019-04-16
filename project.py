#!/usr/bin/env python3
from flask import Flask, render_template, url_for, request, redirect, flash


app = Flask(__name__)


# Show all cities
@app.route('/')
def show_cities():
    return 'Cities'


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
