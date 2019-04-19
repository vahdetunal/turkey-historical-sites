# turkey-historical-sites

turkey-historical-sites is a website project that lists historical sites in
Turkey based on the city they are located.

## Getting Started

Following instructions will help you run the project on your local machine.

### Prerequisites

- Python 3: Instructions for installing python 3 can be found [here](
  https://realpython.com/installing-python/)
- psycopg2: Installation instructions can be found [here](
  http://initd.org/psycopg/docs/install.html)
- Flask: Instructions to install Flask can be found [here](
  http://flask.pocoo.org/docs/1.0/installation/)
- SQL Alchemy: Instuctions for installation can be found [here](
  https://docs.sqlalchemy.org/en/13/intro.html#installation)
- flask_sqlalchemy: Can be installed from the command line using
  `pip install flask-sqlalchemy`
- oauth2client: Install from the command line using
  `pip install --upgrade oauth2client`

### Installing

If you have git installed, you can fork the project from terminal using:
  `git clone https://github.com/vahdetunal/turkey-historical-sites.git`

Alternatively, it can be downloaded directly from [github](
  https://github.com/vahdetunal/turkey-historical-sites.git).

## Using the Application

- Open the terminal and navigate into the project folder.
- Run database_setup.py using `python3 database_setup.py`
- Populate the database with some initial entries by using
  `python3 populate_db.py`
- Run the application using `python3 project.py`
- Visit http://localhost:5000 on your browser.
- Contents of the website is accessable without login.
- The website uses google oAuth2 login. Registered users can add new cities
  and historical sites. They can also edit or delete the entries they have
  created.

## JSON Endpoints

- http://localhost:5000/cities/JSON and http://localhost:5000/JSON for cities.
- http://localhost:5000/city_id/JSON to get all historical sites within a city.
- http://localhost:5000/sites/JSON to access all historical sites.
- http://localhost:5000/city_id/site_id/JSON to get information about a single
  historical site.
- Adding /JSON to home page, a city historical sites page or a historical sites
  own page will return the corresponding JSON API.