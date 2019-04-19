#!/usr/bin/env python3
from flask import Flask, render_template, url_for, request, redirect, flash
from flask import make_response, jsonify
from flask import session as login_session
from flask_sqlalchemy import SQLAlchemy

from database_setup import Base, City, Site, User

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

import httplib2
import json
import requests
import random
import string


app = Flask(__name__)

# flask_sqlalchemy warns against the use of this. It is true by default.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Create a DB session
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///historicalsites.db'
db = SQLAlchemy(app)
session = db.session()

# Load json secrets for google oauth2
CLIENT_ID = json.loads(
            open('client_secrets.json', 'r').read())['web']['client_id']


# Three helper functions all include a session.close(). Without closing
# sessions, logging in or out of the website usually resulted in sqlalchemy
# thread errors although flask_sqlalchemy should be thread safe. Logging out
# still causes thread errors sometimes. I could not figure out the reason.

# Add a new user to database and return the users id
def create_user(login_session):
    new_user = User(name=login_session['username'],
                    email=login_session['email'],
                    picture=login_session['picture'])
    session.add(new_user)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    session.close()
    return user.id


# Returns a user given the user id
def get_user_info(id):
    user = session.query(User).filter_by(id=id).one()
    session.close()
    return user


def get_user_id(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        session.close()
        return user.id
    except BaseException:
        return None


def get_session_user(login_session):
    try:
        return login_session['user_id']
    except BaseException:
        return None


# Create and store a state token to prevent cross site request forgery attacks.
def generate_state_token():
    characters = string.ascii_uppercase + string.digits
    state = ''.join(random.choice(characters) for i in range(32))
    return state


# Show login page, sends a state token to the user to prevent cross site
# forgery attacks.
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
        response = make_response(json.dumps(
                                 'Current user is already connected.'),
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

    # Check if the user is already registered
    result = get_user_id(login_session['email'])
    print(result)
    # Register if the user does not exit
    if result is None:
        user_id = create_user(login_session)
        login_session['user_id'] = user_id
    else:
        login_session['user_id'] = result

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += (' " style = "width: 300px; height: 300px;' +
               'border-radius: 150px;-webkit-border-radius: 150px;' +
               '-moz-border-radius: 150px;"> ')
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
        response = make_response(json.dumps('Current user not connected.'),
                                 401)
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
        del login_session['user_id']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        # If token could not be revoked, inform the user
        response = make_response(json.dumps(
                                 'Failed to revoke token for given user.',
                                 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# Show all cities
@app.route('/')
def show_cities():
    # Get cities from the database
    cities = session.query(City).order_by(City.name)
    username = login_session.get('username', '')
    # Pass id to hide links from unauthorized or unauthenticated users
    user_id = get_session_user(login_session)
    return render_template('cities.html', cities=cities,
                           username=username, user_id=user_id)


# Show historical sites within a city
@app.route('/<int:city_id>')
def show_sites(city_id):
    city = session.query(City).filter_by(id=city_id).one()
    sites = session.query(Site).filter_by(city_id=city_id)
    # Pass id to hide links from unauthorized or unauthenticated users
    user_id = get_session_user(login_session)
    return render_template('sites.html', city=city,
                           sites=sites, user_id=user_id)


# Show a historical site
@app.route('/<int:city_id>/<int:site_id>')
def show_historical_site(city_id, site_id):
    site = session.query(Site).filter_by(id=site_id, city_id=city_id).one()
    return render_template('singlesite.html', site=site)


# Add a new city
@app.route('/new', methods=['GET', 'POST'])
def new_city():
    # Redirect to login page if the user is not logged in.
    if 'username' not in login_session:
        flash('You need to login to add a city.')
        return redirect('/login')

    user_id = get_user_id(login_session['email'])

    if request.method == 'POST':
        city = validate_new_city(request.form, user_id)
        if city is None:
            flash('Name field is required!')
            return redirect(url_for('show_cities'))
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

    # Redirect to login page if user is not logged in.
    if 'username' not in login_session:
        flash('You need to login to edit a city.')
        return redirect('/login')

    # Redirect to main page if the user is unauthorized.
    if login_session['user_id'] != city.user_id:
        flash('You do not have authorization to edit {}'.format(city.name))
        return redirect(url_for('show_cities'))

    if request.method == 'POST':
        city = validate_edit_city(city, request.form)

        if city is None:
            flash('Name field is required!')
            return redirect(url_for('show_cities'))

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

    # Redirect to login page if user is not logged in.
    if 'username' not in login_session:
        flash('You need to login to delete a city.')
        return redirect('/login')

    # Redirect to main page if the user is unauthorized.
    if login_session['user_id'] != city.user_id:
        flash('You do not have authorization to delete {}'.format(city.name))
        return redirect(url_for('show_cities'))

    if request.method == 'POST':
        # A city may not have any site entries. Those cases need to be
        # handled to prevent errors.
        try:
            session.query(Site).filter_by(city_id=city_id).delete()
        except BaseException:
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

    # Redirect to login page if the user is not logged in.
    if 'username' not in login_session:
        flash('You need to login to add a site.')
        return redirect('/login')

    user_id = get_user_id(login_session['email'])

    if request.method == 'POST':
        site = validate_new_site(request.form, user_id, city_id)

        if site is None:
            flash('Name field is required!')
            return redirect(url_for('show_sites', city_id=city_id))

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

    # Redirect to main page if the user is not logged in.
    if 'username' not in login_session:
        flash('You need to login to edit a site.')
        return redirect('/login')

    # Redirect to sites page if the user is not authorized
    if login_session['user_id'] != site.user_id:
        flash('You do not have authorization to edit {}'.format(site.name))
        return redirect(url_for('show_sites', city_id=city_id))

    if request.method == 'POST':
        site = validate_edit_site(site, request.form)
        if site is None:
            flash('Name field is required!')
            return redirect(url_for('show_sites', city_id=city_id))

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

    # Redirect to main page if the user is not logged in.
    if 'username' not in login_session:
        flash('You need to login to delete a site.')
        return redirect('/login')

    # Redirect to sites page if the user is not authorized
    if login_session['user_id'] != site.user_id:
        flash('You do not have authorization to delete {}'.format(site.name))
        return redirect(url_for('show_sites', city_id=city_id))

    if request.method == 'POST':
        session.delete(site)
        session.commit()
        flash('Historical site {} deleted!'.format(site.name))
        return redirect(url_for('show_sites', city_id=city_id))
    else:
        return render_template('deletesite.html', site=site)


def validate_new_city(city_form, user_id):
    '''Validates a city form, returns none if the form has no name field.
    Returns a City object otherwise. If no image link is included, default
    image is added.

    Arguments:
    city_form: An immutable dictionary with fields name and picture
    user_id: ID of the user making the request.
    '''
    city_form = city_form.to_dict()
    if not city_form['name']:
        return None
    if not city_form['image_uri']:
        city_form['image_uri'] = url_for('static', filename='no_image.png')
    city = City(name=city_form['name'], image=city_form['image_uri'],
                user_id=user_id)
    return city


def validate_edit_city(city, city_form):
    '''Validates an edit city form returns, none if the form has no name field.
    Returns a City object otherwise. If no image link is included, default
    image is added.

    Arguments:
    city: The City object to be updated
    city_form: An immutable dictionary with fields name and picture
    '''
    # Since only authorized users can make a request to edit, no need to check
    # for user ID here.
    city_form = city_form.to_dict()
    if not city_form['name']:
        return None
    if not city_form['image_uri']:
        city_form['image_uri'] = url_for('static', filename='no_image.png')
    city.name = city_form['name']
    city.image = city_form['image_uri']
    return city


def validate_new_site(site_form, user_id, city_id):
    '''Validates a site form, returns none if the form has no name field.
    Returns a Site object otherwise. Other unprovided fields are filled by
    default values.

    Arguments:
    site_form: An immutable dictionary with fields name and picture
    user_id: ID of the user making the request.
    city_id: ID of the city where the site is located.
    '''
    site_form = site_form.to_dict()

    if not site_form['name']:
        return None

    site_form = site_form_defaults(site_form)

    site = Site(name=site_form['name'], civilization=site_form['civilization'],
                description=site_form['description'],
                image=site_form['image_uri'], city_id=city_id, user_id=user_id)
    return site


def validate_edit_site(site, site_form):
    '''Validates a site form, returns none if the form has no name field.
    Returns a Site object otherwise. Other unprovided fields are filled by
    default values.

    Arguments:
    site: The Site object to be updated
    site_form: An immutable dictionary with fields name and picture
    '''
    site_form = site_form.to_dict()

    if not site_form['name']:
        return None

    site_form = site_form_defaults(site_form)

    site.name = site_form['name']
    site.civilization = site_form['civilization']
    site.description = site_form['description']
    site.image = site_form['image_uri']
    return site


def site_form_defaults(site_form):
    '''
    This helper function fills site form fields with default values if they
    are not provided.

    Arguments:
    site_form: A dictionary object obtained from site forms.
    '''
    if not site_form['civilization']:
        site_form['civilization'] = 'Civilization was not provided by the user'
    if not site_form['description']:
        site_form['description'] = 'Description was not provided by the user'
    if not site_form['image_uri']:
        site_form['image_uri'] = url_for('static', filename='no_image.png')
    return site_form


# JSON api to get all cities
@app.route('/JSON')
@app.route('/cities/JSON')
def cities_json():
    cities = session.query(City).all()
    return jsonify(cities=[city.serialize for city in cities])


# JSON api to get all sites within a city
@app.route('/<int:city_id>/JSON')
def city_sites_json(city_id):
    sites = session.query(Site).filter_by(city_id=city_id).all()
    return jsonify(sites=[site.serialize for site in sites])


# JSON api to get all sites
@app.route('/sites/JSON')
def sites_json():
    sites = session.query(Site).all()
    return jsonify(sites=[site.serialize for site in sites])


# JSON api to get a single site
@app.route('/<int:city_id>/<int:site_id>/JSON')
def single_site(city_id, site_id):
    site = session.query(Site).filter_by(id=site_id, city_id=city_id).one()
    return jsonify(site=site.serialize)


if __name__ == '__main__':
    # Read the secret key from file and close the file
    f = open("secret_key.txt", "r")
    app.secret_key = f.read()
    f.close()
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
