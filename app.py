#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import sys
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from os import abort
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app,db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
  __tablename__ = 'venue'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String)
  city = db.Column(db.String(120))
  state = db.Column(db.String(120))
  address = db.Column(db.String(120))
  phone = db.Column(db.String(120))
  genres = db.Column(db.ARRAY(db.String))
  facebook_link = db.Column(db.String(120))
  image_link = db.Column(db.String(500))
  website_link = db.Column(db.String(200))
  seeking_talent = db.Column(db.Boolean,default = False)
  seeking_description = db.Column(db.String(1000))
  shows = db.relationship('Show',backref = 'venue')

  def __repr__(self):
    return f'<Venue {self.id} {self.name} {self.city}>'

  # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):

  __tablename__ = 'artist'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String)
  city = db.Column(db.String(120))
  state = db.Column(db.String(120))
  phone = db.Column(db.String(120))
  genres = db.Column(db.ARRAY(db.String))
  facebook_link = db.Column(db.String(120))
  image_link = db.Column(db.String(500))
  website_link = db.Column(db.String(200))
  seeking_venue = db.Column(db.Boolean, default = False)
  seeking_description = db.Column(db.String(1000))
  shows = db.relationship('Show',backref = 'artist')

  def __repr__(self):
    return f'<Artist {self.id} {self.name} {self.city}>'


class Show(db.Model):
  __tablename__  = 'show'

  id = db.Column(db.Integer,primary_key = True)
  artist_id = db.Column(db.Integer,db.ForeignKey('artist.id'),nullable = False)
  venue_id = db.Column(db.Integer,db.ForeignKey('venue.id'),nullable = False)
  start_time = db.Column(db.DateTime,nullable = False)


# TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

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
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  venues = Venue.query.all()
  data=[]
  
  venue_places = set()
  for place in venues:
    venue_places.add((place.city,place.state))

  for venue in venue_places:
    data.append({
      "city":venue[0],
      "state":venue[1],
      "venues":[]
    })

  for show_place in venues:
    num_upcoming_shows = 0

    shows = Show.query.filter_by(venue_id = show_place.id).all()

    for show in shows:
      if show.start_time > datetime.now():
        num_upcoming_shows += 1

    for input in data:
      if show_place.city == input['city'] and show_place.state == input['state']:
        input['venues'].append({
          "id":show_place.id,
          "name":show_place.name,
          "num_upcoming_shows": num_upcoming_shows
        })

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

  search = request.form.get('search_term','')
  venues = Venue.query.filter(Venue.name.ilike(f'%{search}%')).all()


  data = []

  for venue in venues:
    data.append({
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows": len(db.session.query(Show).filter(Show.venue_id == 1).filter(Show.start_time>datetime.now()).all())
    })

  response={
    "count": len(venues),
    "data": data
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):

  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  venue = Venue.query.filter_by(id=venue_id).first()

  upcoming_shows = db.session.query(Show).join(Artist).filter(Show.venue_id == venue_id).filter(Show.start_time>datetime.now()).all()
  upcoming_shows_data = []

  past_shows = db.session.query(Show).join(Artist).filter(Show.venue_id == venue_id).filter(Show.start_time<datetime.now()).all()
  past_shows_data = []

  for show in past_shows:
    past_shows_data.append({
      "artist_id": show.artist_id,
      "artist_name": Artist.query.filter_by(id=show.artist_id).first().name,
      "image_link":show.artist.image_link,
      "start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S")
    })

  for show in upcoming_shows:
    upcoming_shows_data.append({
      "artist_id": show.artist_id,
      "artist_name": Artist.query.filter_by(id=show.artist_id).first().name,
      "image_link":show.artist.image_link,
      "start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S")
    })

  data = {
    "id":venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows":past_shows_data,
    "upcoming_shows":upcoming_shows_data,
    "past_shows_count": len(past_shows_data),
    "upcoming_shows_count":len(upcoming_shows_data)
  }

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm(request.form)

  try:
    new_venue = Venue(
    name=form.name.data,
    city=form.city.data,
    state=form.state.data,
    address=form.address.data,
    phone=form.phone.data,
    genres=form.genres.data,
    facebook_link=form.facebook_link.data,
    image_link=form.image_link.data,
    website_link=form.website_link.data,
    seeking_talent=form.seeking_talent.data,
    seeking_description=form.seeking_description.data
    )

    db.session.add(new_venue)
    db.session.commit()

    flash('Venue ' + request.form['name'] + ' was successfully listed!')

  except ValueError: 

    flash('Error occurred. Venue ' + form.name + ' could not be listed.')

  finally:
    db.session.close()

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  error = False
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()

    flash(f'Your venue {venue_id} has been deleted successfully')
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())

    flash(f'Sorry, An error has occured. Venue {venue_id} could not be deleted.')
  finally:
    db.session.close() #FIXME
    

  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data = db.session.query(Artist).all()
  
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

  search = request.form.get('search_term','')
  artists = Artist.query.filter(Artist.name.ilike(f'%{search}')).all()

  data = []

  for artist in artists:
    data.append({
      "id":artist.id,
      "name":artist.name,
      "num_upcoming_shows": len(db.session.query(Show).filter(Show.artist_id == 1).filter(Show.start_time>datetime.now()).all())
    })

  response={
    "count":len(artists),
    "data":data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  artist = Artist.query.filter_by(id=artist_id).first()

  upcoming_shows = db.session.query(Show).join(Venue).filter(Show.artist_id == artist_id).filter(Show.start_time>datetime.now()).all()
  upcoming_shows_data = []

  past_shows = db.session.query(Show).join(Venue).filter(Show.artist_id == artist_id).filter(Show.start_time<datetime.now()).all()
  past_shows_data = []

  for show in past_shows:
    past_shows_data.append({
      "venue_id": show.venue_id,
      "venue_name": Venue.query.filter_by(id=show.venue_id).first().name,
      "image_link":show.venue.image_link,
      "start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S")
    })

  for show in upcoming_shows:
    upcoming_shows_data.append({
      "venue_id": show.venue_id,
      "venue_name": Venue.query.filter_by(id=show.venue_id).first().name,
      "image_link":show.venue.image_link,
      "start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S")
    })

  data = {
    "id":artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website_link,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows":past_shows_data,
    "upcoming_shows":upcoming_shows_data,
    "past_shows_count": len(past_shows_data),
    "upcoming_shows_count":len(upcoming_shows_data)
  }
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)

  if artist:
    form.name.data = artist.name
    form.city.data = artist.city
    form.state.data = artist.state
    form.phone.data = artist.phone
    form.genres.data = artist.genres
    form.facebook_link.data = artist.facebook_link
    form.image_link.data = artist.image_link
    form.website_link.data = artist.website_link
    form.seeking_venue.data = artist.seeking_venue
    form.seeking_description.data = artist.seeking_description
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
  venue = Venue.query.get(venue_id)

  if venue:
    form.name.data = venue.name
    form.city.data = venue.city
    form.state.data = venue.state
    form.phone.data = venue.phone
    form.address.data = venue.address
    form.genres.data = venue.genres
    form.facebook_link.data = venue.facebook_link
    form.image_link.data = venue.image_link
    form.website_link.data = venue.website_link
    form.seeking_talent.data = venue.seeking_talent
    form.seeking_description.data = venue.seeking_description

  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  venue = Venue.query.get(venue_id)

  try:
    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.address = request.form['address']
    venue.phone = request.form['phone']
    venue.genres = request.form.getlist('genres')
    venue.image_link = request.form['image_link']
    venue.facebook_link = request.form['facebook_link']
    venue.website_link = request.form['website_link']
    venue.seeking_talent = True if 'seeking_talent' in request.form else False
    venue.seeking_description = request.form['seeking_description']

    db.session.commit()

    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  
  except ValueError:
    db.session.rollback()
    print(sys.exc_info())

    flash('Error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  
  finally:
    db.session.close()
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
  form = ArtistForm(request.form)
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  try:
    new_artist = Artist(
    name=form.name.data,
    city=form.city.data,
    state=form.state.data,
    phone=form.phone.data,
    genres=form.genres.data,
    facebook_link=form.facebook_link.data,
    image_link=form.image_link.data,
    website_link=form.website_link.data,
    seeking_venue=form.seeking_venue.data,
    seeking_description=form.seeking_description.data
    )

    db.session.add(new_artist)
    db.session.commit()

    flash('Artist ' + request.form['name'] + ' was successfully listed!')

  except ValueError: 

    flash('Error occurred. Venue ' + form.name + ' could not be listed.')

  finally:
    db.session.close()
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.

  shows = Show.query.all()

  data = []

  for show in shows:
    data.append({
      "venue_id": show.venue_id,
      "venue_name": Venue.query.filter_by(id=show.venue_id).first().name,
      "artist_id":show.artist_id,
      "artist_name":Artist.query.filter_by(id=show.artist_id).first().image,
      "artist_image_link": Artist.query.filter_by(id =show.artist_id).first().image_link,
      "start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S")
    })
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
  error = False
  try:
    artist_id = request.form['artist_id']
    venue_id = request.form['venue_id']
    start_time = request.form['start_time']

    new_show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)

    db.session.add(new_show)
    db.session.commit()
    # on successful db insert, flash success
    flash('Show at' + request.form['venue_id']+ ' by' + request.form['artist_id']+ 'was successfully listed.')
  except ValueError:
    db.session.rollback()
    print(sys.exc_info())

    flash('An error occurred. Show  at' + request.form['venue_id']+ ' could not be listed.')

  finally:
    db.session.close()
  
  if error:
    flash('An error occurred. Show  at' + request.form['venue_id']+ ' could not be listed.')
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
