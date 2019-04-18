#!/usr/bin/env python3
from flask import Flask, render_template, url_for, request, redirect, flash
from flask import session as login_session
from flask import make_response

from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, City, Site

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

import httplib2
import json
import requests
import random, string


app = Flask(__name__)


CLIENT_ID = json.loads(
            open('client_secrets.json', 'r').read())['web']['client_id']

# Create the engine for DB connection
engine = create_engine('sqlite:///historicalsites.db')

# Create a DB session
Session = sessionmaker(bind=engine)
session = Session()

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


# Connect the user using Google oAuth
@app.route('/gconnect', methods=['POST', 'GET'])
def gconnect():
    # State token validation against cross site forgery attacks.
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Get the one time access token
    code = request.data
    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={}'
           .format(access_token))
    h = httplib2.Http()
    # This request returns a bytes object and needs to be decoded.
    result = json.loads(h.request(url, 'GET')[1].decode('utf-8'))
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    google_id = credentials.id_token['sub']
    if result['user_id'] != google_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check if the user is already logged in.
    stored_access_token = login_session.get('access_token')
    stored_google_id = login_session.get('google_id')
    if stored_access_token is not None and google_id == stored_google_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['google_id'] = google_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print("done!")
    return output


# Disconnect from users Google account.
@app.route('/gdisconnect')
def gdisconnect():
    # Check if the user is logged in
    access_token = login_session.get('access_token')
    if access_token is None:
        print('Access Token is None')
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print('In gdisconnect access token is {}'.format(access_token))
    print('User name is: ')
    print(login_session['username'])
    # Revoke users access token.
    url = ('https://accounts.google.com/o/oauth2/revoke?token={}'
           .format(login_session['access_token']))
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print('result is ')
    print(result)
    # If token is successfuly revoked, delete users session
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['google_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        # If token could not be revoked, inform the user
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# Show all cities
@app.route('/')
def show_cities():
    # Get cities from the database
    cities = session.query(City).order_by(asc(City.name))
    username = login_session.get('username', '')
    return render_template('cities.html',
                            cities=cities,
                            username=username)


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
