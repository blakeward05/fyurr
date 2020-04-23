#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import sys
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    genres = db.Column(db.String())
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean())
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref='venues')

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

    def get_venue_snapshot(self):
      now = datetime.utcnow()
      shows = Show.query.filter_by(venue_id=self.id).filter(Show.start_time>now).count()
      snapshot = {'id':self.id, 'name':self.name, 'upcoming_shows': shows}
      return snapshot

    def get_venue_shows(self):
      shows = Show.query.filter(Show.venue_id == self.id).order_by(Show.start_time.desc()).all()
      return(shows)



      

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String())
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean())
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref='artists')

    def get_artist_shows(self):
      shows = Show.query.filter(Show.artist_id == self.id).order_by(Show.start_time.desc()).all()
      return(shows)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate


# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    start_time = db.Column(db.DateTime(), nullable=True)
    past_ind = db.Column(db.Boolean(), nullable=True)

    def get_artist_snap(self):
      artist = Artist.query.get(self.artist_id)
      show_snap = {'artist_id': artist.id, 'artist_name': artist.name, 'artist_image_link': artist.image_link, 'start_time': self.start_time.strftime('%m/%d/%Y, %H:%M')}
      return(show_snap)

    def get_venue_snap(self):
      venue = Venue.query.get(self.venue_id)
      show_snap = {'venue_id': venue.id, 'venue_name': venue.name, 'venue_image_link': venue.image_link, 'start_time': self.start_time.strftime('%m/%d/%Y, %H:%M')}
      return(show_snap)




#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  cities = Venue.query.distinct('city', 'state').all()
  data = []
  for city in cities:
    print(city.city)
    venues = Venue.query.filter(Venue.city == city.city, Venue.state == city.state).all()
    record = {
        'city': city.city,
        'state': city.state,
        'venues': [venue.get_venue_snapshot() for venue in venues],
    }
    data.append(record)
  print(data)

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  term = request.form['search_term']
  print(term)
  venues = Venue.query.filter(Venue.name.ilike('%'+ term + '%')).all()
  response = {}
  data = []
  for venue in venues:
    shows = venue.get_venue_shows()
    num = 0
    for show in shows:
      if show.start_time > datetime.now():
        num += 1
    data.append({'id': venue.id, 'name': venue.name, 'num_upcoming_shows': num})

  response['count'] = len(venues)
  response['data'] = data

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.get(venue_id)
  shows = venue.get_venue_shows()
  past_shows = []
  upcoming_shows = []
  for show in shows:
    artist_snap = show.get_artist_snap()
    print(artist_snap)
    if show.start_time > datetime.now():
      upcoming_shows.append(artist_snap)
    else: 
      past_shows.append(artist_snap)

  data = venue.__dict__
  data['genres'] = [venue.genres]
  data['past_shows'] = past_shows
  data['past_shows_count'] = len(past_shows)
  data['upcoming_shows'] = upcoming_shows
  data['upcoming_shows_count']= len(upcoming_shows)
  

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = VenueForm(request.form)
  try:
    new_venue = Venue(name = request.form['name'],
                      genres = ",".join(form.genres.data),
                      address = request.form['address'],
                      city = request.form['city'],
                      state = request.form['state'],
                      phone = request.form['phone'],
                      facebook_link = request.form['facebook_link'],
                      website = form.website.data,
                      image_link = form.image_link.data,
                      seeking_talent = form.seeking_talent.data,
                      seeking_description = form.seeking_description.data
                      )
    db.session.add(new_venue)
    db.session.commit()
  # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data = Artist.query.order_by('id').all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  term = request.form['search_term']
  print(term)
  artists = Artist.query.filter(Artist.name.ilike('%'+ term + '%')).all()
  response = {}
  data = []
  for artist in artists:
    shows = artist.get_artist_shows()
    num = 0
    for show in shows:
      if show.start_time > datetime.now():
        num += 1
    data.append({'id': artist.id, 'name': artist.name, 'num_upcoming_shows': num})

  response['count'] = len(artists)
  response['data'] = data

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  
  artist = Artist.query.get(artist_id)
  shows = artist.get_artist_shows()
  past_shows = []
  upcoming_shows = []
  for show in shows:
    venue_snap = show.get_venue_snap()
    if show.start_time > datetime.now():
      upcoming_shows.append(venue_snap)
    else: 
      past_shows.append(venue_snap)

  data = artist.__dict__
  data['genres'] = [artist.genres]
  data['past_shows'] = past_shows
  data['past_shows_count'] = len(past_shows)
  data['upcoming_shows'] = upcoming_shows
  data['upcoming_shows_count']= len(upcoming_shows)

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = ArtistForm(request.form)
  try:
    new_artist = Artist(name = request.form['name'],
                      genres = ",".join(form.genres.data),
                      phone = request.form['phone'],
                      city = request.form['city'],
                      state = request.form['state'],
                      facebook_link = request.form['facebook_link'],
                      website = form.website.data,
                      image_link = form.image_link.data,
                      seeking_venue = form.seeking_venue.data,
                      seeking_description = form.seeking_description.data
                      )
    db.session.add(new_artist)
    db.session.commit()
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  # on successful db insert, flash success'
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  
  data = []
  shows = Show.query.all()
  for show in shows:
    venue = show.get_venue_snap()
    artist = show.get_artist_snap()
    venue.update(artist)
    data.append(venue)
   
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  try:
    new_show = Show(artist_id = request.form['artist_id'], venue_id = request.form['venue_id'], start_time = request.form['start_time'])
    db.session.add(new_show)
    db.session.commit()
  # on successful db insert, flash success
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Show could not be listed.')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
