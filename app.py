#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from asyncio.base_subprocess import WriteSubprocessPipeProto
import json
import weakref
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import sys
from model import Venue, Show, Artist, app, db



# db.create_all()
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

today = datetime.now()
now = today.strftime("%Y-%m-%d %H:%M:%S")

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
  # list all the available venues
 
  data = []
  data = Venue.query.order_by('id').all() 
  for d in data:
      d.venues = Venue.query.filter_by(city=d.city).all()
  return render_template('pages/venues.html', areas=data);


@app.route('/venues/search', methods=['POST'])
def search_venues():
  # search on artists with partial string search. it is case-insensitive.
  
  search_term = request.form.get('search_term', '')
  data = Venue.query.filter(Venue.name.ilike("%" + search_term + "%")).all()
  response = {
        "count": len(data),
        "data": data
    }
  return render_template('pages/search_venues.html', results=response, search_term=search_term)


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  venue = {}
  up_shows = []
  past_show = []
  try:
    venue = Venue.query.get(venue_id)
    for show in venue.shows:
      sh = Show.query.get(show.id)
      show.artist_name = sh.artist.name
      show.artist_image_link = sh.artist.image_link
      if show.time > today:
        show.time = str(show.time)
        up_shows.append(show)
      else:
        show.time = str(show.time)
        past_show.append(show)
    setattr(venue, 'past_shows', past_show)
    setattr(venue, 'upcoming_shows', up_shows)
    setattr(venue, 'past_shows_count', len(past_show))
    setattr(venue, 'upcoming_shows_count', len(up_shows))
  except:
    print(sys.exc_info())
  return render_template('pages/show_venue.html', venue=venue)


  # data = Venue.query.filter_by(id=venue_id).first()




#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # modify data to be the data object returned from db insertion
  error = False
  try:
    new_venue = Venue(
        name = request.form.get('name'),
        city = request.form.get('city'),
        state = request.form.get('state'),
        address = request.form.get('address'),
        phone = request.form.get('phone'),
        genres = request.form.getlist('genres'),
        facebook_link = request.form.get('facebook_link'),
        image_link = request.form.get('image_link'),
        website_link = request.form.get('website_link'),
        seeking_talent=request.form.get('seeking_talent'),
        seeking_description = request.form.get('seeking_description')
        )
    db.session.add(new_venue)
    db.session.commit()
    flash('Venue ' + request.form.get('name') + ' was successfully listed!')
  except:
    db.session.rollback()
    error = True
    print(sys.exc_info())
    flash('An error occurred. Venue ' + request.form.get('name')+ ' could not be listed.')
  finally:
    db.session.close()
  return render_template('pages/home.html')
  

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # delete a record. Handle cases where the session commit could fail.
  error = False
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
    flash('Venue ' + venue.name + ' was successfully deleted!')
  except:
    db.session.rollback()
    error = True
    flash('An error occurred trying to delete ' + venue.name)
  finally:
    db.session.close()
  return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # returns available artists

  data = Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # search on artists with partial string search. Ensure it is case-insensitive.
  
  search_term = request.form.get('search_term', '')
  data = Artist.query.filter(Artist.name.ilike("%" + search_term + "%")).all()
  response = {
        "count": len(data),
        "data": data
    }
  return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  artist = {}
  up_shows = []
  past_show = []
  try:
    artist = Artist.query.get(artist_id)
    for show in artist.shows:
      sh = Show.query.get(show.id)
      show.venue_name = sh.venue.name
      show.venue_image_link = sh.venue.image_link
      if show.time > today :
        show.time = str(show.time)
        up_shows.append(show)
      else:
        show.time = str(show.time)
        past_show.append(show)
    setattr(artist, 'past_shows', past_show)
    setattr(artist, 'upcoming_shows', up_shows)
    setattr(artist, 'past_shows_count', len(past_show))
    setattr(artist, 'upcoming_shows_count', len(up_shows))
  except:
    print(sys.exc_info())
  return render_template('pages/show_artist.html', artist=artist)
  # data = Artist.query.filter_by(id=artist_id).first()

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  form = ArtistForm(request.form)
  try:
        artist = Artist.query.get(artist_id)
        artist.name = form.name.data
        artist.city = form.city.data
        artist.state = form.state.data
        artist.phone = form.phone.data
        artist.genres = form.genres.data
        artist.image_link = form.image_link.data
        artist.facebook_link = form.facebook_link.data
        artist.website_link = form.website_link.data
        artist.seeking_venue = form.seeking_venue.data
        artist.seeking_description = form.seeking_description.data
        db.session.commit()
        flash('Artist ' + form.name.data + 'was successfully edited!')
  except:
    db.session.rollback()
    flash('Artist '  + form.name.data + 'could not be edited.')
  finally:
        db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
   # populate form with values from venue with ID <venue_id>
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  form = VenueForm(request.form)
  try:
        venue = Venue.query.get(venue_id)
        venue.name = form.name.data
        venue.city = form.city.data
        venue.state = form.state.data
        venue.phone = form.phone.data
        venue.address = form.address.data
        venue.image_link = form.image_link.data
        venue.facebook_link = form.facebook_link.data
        venue.website_link = form.website_link.data
        venue.genres = form.genres.data
        venue.seeking_talent = form.seeking_talent.data
        venue.seeking_description = form.seeking_description.data
        db.session.commit()
        flash('Venue ' + form.name.data + 'was successfully edited!')
  except:
    db.session.rollback()
    flash('Venue '  + form.name.data + 'could not be edited.')
  finally:
        db.session.close()
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
  error = False
  try:
    new_artist = Artist(
        name = request.form.get('name'),
        city = request.form.get('city'),
        state = request.form.get('state'),
        phone = request.form.get('phone'),
        genres = request.form.getlist('genres'),
        facebook_link = request.form.get('facebook_link'),
        image_link = request.form.get('image_link'),
        website_link = request.form.get('website_link'),
        seeking_venue=request.form.get('seeking_venue'),
        seeking_description = request.form.get('seeking_description')
        )
    db.session.add(new_artist)
    db.session.commit()
    flash('Artist ' + request.form.get('name') + ' was successfully listed!')
  except:
    db.session.rollback()
    error = True
    print(sys.exc_info())
    flash('An error occurred. Artist ' + request.form.get('name')+ ' could not be listed.')
  finally:
    db.session.close()
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows

  data = Show.query.all()
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  error = False
  try:
    new_show = Artist(
        start_time = request.form.get('start_time'),
        artist_id = request.form.get('artist_id'),
        venue_id = request.form.get('venue_id')
        )
    db.session.add(new_show)
    db.session.commit()
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    error = True
    print(sys.exc_info())
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()
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
