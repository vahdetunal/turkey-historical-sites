#!/usr/bin/env python3
from flask import Flask, render_template, url_for, request, redirect, flash
from flask import session as login_session

from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, City, Site

import random, string

app = Flask(__name__)


# Create and store a state token to prevent cross site request forgery attacks.
def generate_state_token():
    characters = string.ascii_uppercase + string.digits
    state = ''.join(random.choice(characters) for i in range(32))
    return state

@app.route('/login')
def show_login():
    state = generate_state_token()
    login_session['state'] = state
    return render_template('login.html', STATE=state)

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
    city = session.query(City).filter_by(id=city_id).one()
    sites = session.query(Site).filter_by(city_id=city_id)
    return render_template('sites.html', city=city, sites=sites)


# Show a historical site
@app.route('/<int:city_id>/<int:site_id>')
def show_historical_site(city_id, site_id):
    site = session.query(Site).filter_by(id=site_id, city_id=city_id).one()
    return render_template('singlesite.html', site=site)


# Add a new city
@app.route('/new', methods=['GET', 'POST'])
def new_city():
    if request.method == 'POST':
        city = City(name=request.form['name'],
                    image=request.form['image_uri'],
                    user_id=1)
        session.add(city)
        session.commit()
        flash('New city {} successfully added!'.format(city.name))
        return redirect(url_for('show_cities'))
    else:
        return render_template('newcity.html')


# Edit a city
@app.route('/<int:city_id>/edit', methods=['GET', 'POST'])
def edit_city(city_id):
    city = session.query(City).filter_by(id=city_id).one()
    if request.method == 'POST':
        if request.form['name']:
            city.name = request.form['name']
        if request.form['image_uri']:
            city.image = request.form['image_uri']
        city.user_id = 1
        session.add(city)
        session.commit()
        flash('City {} edited!'.format(city.name))
        return redirect(url_for('show_cities'))
    else:
        return render_template('editcity.html', city=city)


# Delete a city
@app.route('/<int:city_id>/delete', methods=['GET', 'POST'])
def delete_city(city_id):
    '''
    Deletes a city and all site entries related.
    '''
    city = session.query(City).filter_by(id=city_id).one()
    if request.method == 'POST':
        # A city may not have any site entries. Those cases need to be
        # handled to prevent errors.
        try:
            session.query(Site).filter_by(city_id=city_id).delete()
        except:
            session.rollback()
        session.delete(city)
        session.commit()
        flash('City {} deleted!'.format(city.name))
        return redirect(url_for('show_cities'))
    else:
        return render_template('deletecity.html', city=city)


# Add a historical site
@app.route('/<int:city_id>/new', methods=['GET', 'POST'])
def new_historical_site(city_id):
    city = session.query(City).filter_by(id=city_id).one()
    if request.method == 'POST':
        site = Site(name=request.form['name'],
                    description=request.form['description'],
                    civilization=request.form['civilization'],
                    image=request.form['image_uri'],
                    city_id=city_id,
                    user_id=1)
        session.add(site)
        session.commit()
        flash('New historical site {} added!'.format(site.name))
        return redirect(url_for('show_sites', city_id=city_id))
    else:
        return render_template('newsite.html', city=city)


# Edit a historical site
@app.route('/<int:city_id>/<int:site_id>/edit', methods=['GET', 'POST'])
def edit_historical_site(city_id, site_id):
    site = session.query(Site).filter_by(id=site_id, city_id=city_id).one()
    if request.method == 'POST':
        if request.form['name']:
            site.name = request.form['name']
        if request.form['description']:
            site.description = request.form['description']
        if request.form['civilization']:
            site.civilization = request.form['civilization']
        if request.form['image_uri']:
            site.image = request.form['image_uri']
        session.add(site)
        session.commit()
        flash('Historical site {} edited!'.format(site.name))
        return redirect(url_for('show_historical_site',
                                city_id=city_id, site_id=site_id))
    else:
        return render_template('editsite.html', site=site)


# Delete a historical site
@app.route('/<int:city_id>/<int:site_id>/delete', methods=['GET', 'POST'])
def delete_historical_site(city_id, site_id):
    site = session.query(Site).filter_by(id=site_id, city_id=city_id).one()
    if request.method == 'POST':
        session.delete(site)
        session.commit()
        flash('Historical site {} deleted!'.format(site.name))
        return redirect(url_for('show_sites', city_id=city_id))
    else:
        return render_template('deletesite.html', site=site)


if __name__ == '__main__':
    app.secret_key = 'some_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
