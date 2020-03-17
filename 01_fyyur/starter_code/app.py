#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
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
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database
migrate = Migrate(app, db)


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String,nullable=True)
    city = db.Column(db.String(120),nullable=True)
    state = db.Column(db.String(120),nullable=True)
    address = db.Column(db.String(120),nullable=True)
    phone = db.Column(db.String(120),nullable=True)
    image_link = db.Column(db.String(500),nullable=True)
    facebook_link = db.Column(db.String(120),nullable=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    genres = db.Column(db.String(), nullable=True)
    website = db.Column(db.String(500), nullable=True)
    seeking_talent = db.Column(db.Boolean, nullable=True)
    seeking_description = db.Column(db.String(120), nullable=True)

    shows = db.relationship('Show', backref='venue', lazy=True)


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String,nullable=True)
    city = db.Column(db.String(120),nullable=True)
    state = db.Column(db.String(120),nullable=True)
    phone = db.Column(db.String(120),nullable=True)
    genres = db.Column(db.String(120),nullable=True)
    image_link = db.Column(db.String(500),nullable=True)
    facebook_link = db.Column(db.String(120),nullable=True)


    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    website = db.Column(db.String(500),nullable=True)
    seeking_venue = db.Column(db.Boolean, nullable=True)
    seeking_description = db.Column(db.String(120),nullable=True)

    shows = db.relationship('Show', backref='artist', lazy=True)

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'),nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

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
  #       num_shows should be aggregated based on number of upcoming shows per venue.

     # list for storing venue data
     #list of dictionaries
    data = []

    # selecting all venues from table
    venues = Venue.query.all()
    venue_location = set()
    for venue in venues:
        # add unique city/state tuples
        venue_location.add((venue.city, venue.state))

    # for each unique city/state, add venues
    for location in venue_location:
        data.append({
            "city": location[0],
            "state": location[1],
            "venues": []
        })

    # get number of upcoming shows for each venue
    for venue in venues:
        num_upcoming_shows = 0
        shows = Show.query.filter_by(venue_id=venue.id).all()
        # if the show start time is after now, add to upcoming
        for show in shows:
            if show.start_time > datetime.now():
                num_upcoming_shows += 1
        # for each entry, add venues to matching city/state
        for entry in data:
            if venue.city == entry['city'] and venue.state == entry['state']:
                entry['venues'].append({
                    "id": venue.id,
                    "name": venue.name,
                    "num_upcoming_shows": num_upcoming_shows
                })

    return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
      # get the user search term
    search_term = request.form.get('search_term', '')

    # find all venues matching search term
    # including partial match and case-insensitive
    venues = Venue.query.filter(Venue.name.ilike('%{}%'.format(search_term))).all()

    response = {
        "count": len(venues),
        "data": []
    }

    for venue in venues:
        num_upcoming_shows = 0

        shows = Show.query.filter_by(venue_id=venue.id).all()

        # calculuate num of upcoming shows for each venue
        for show in shows:
            if show.start_time > datetime.now():
                num_upcoming_shows += 1

        # add venue data to response
        response['data'].append({
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": num_upcoming_shows,
        })


    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
    # get all venues
    venue = Venue.query.filter_by(id=venue_id).first()
    # get all shows for given venue
    shows = Show.query.filter_by(venue_id=venue_id).all()
    # returns upcoming shows
    def upcoming_shows():
        upcoming = []
        # if show is in future, add show details to upcoming
        for show in shows:
            if show.start_time > datetime.now():
                upcoming.append({
                    "artist_id": show.artist_id,
                    "artist_name": Artist.query.filter_by(id=show.artist_id).first().name,
                    "artist_image_link": Artist.query.filter_by(id=show.artist_id).first().image_link,
                    "start_time": format_datetime(str(show.start_time))
                })
        return upcoming

    # returns past shows
    def past_shows():
        past = []
        # if show is in past, add show details to past
        for show in shows:
            if show.start_time < datetime.now():
                past.append({
                    "artist_id": show.artist_id,
                    "artist_name": Artist.query.filter_by(id=show.artist_id).first().name,
                    "artist_image_link": Artist.query.filter_by(id=show.artist_id).first().image_link,
                    "start_time": format_datetime(str(show.start_time))
                })
        return past

    # data for given venue
    data = {
        "id": venue.id,
        "name": venue.name,
        "genres": [venue.genres],
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link,
        "past_shows": past_shows(),
        "upcoming_shows": upcoming_shows(),
        "past_shows_count": len(past_shows()),
        "upcoming_shows_count": len(upcoming_shows())
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
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  name = request.form.get('name')
  city = request.form.get('city')
  state = request.form.get('state')
  address = request.form.get('address')
  phone = request.form.get('phone')
  genres = request.form.get('genres')
  facebook_link = request.form.get('facebook_link')
  try:
    venue = Venue(name=name, city=city, state=state, phone=phone,address=address, genres=genres, facebook_link=facebook_link)
    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + request.form.get('name') + ' was successfully listed!')
  except:
    flash('An error occurred. Venue ' + request.form.get('name') + ' could not be listed.')
    db.session.rollback()
  finally:
    db.session.close()

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    venue = Venue.query.filter_by(id=venue_id).first()
    db.session.delete(venue)
    db.session.commit()
    flash('Venue ID ' + venue_id + ' was successfully deleted!')
  except:
    flash('An error occurred. Venue ID '+venue_id+' could not be deleted.')
    db.session.rollback()
  finally:
    db.session.close()

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database

    data = []

    artists = Artist.query.all()

    for artist in artists:
        data.append({
            "id": artist.id,
            "name": artist.name
        })


    return render_template('pages/artists.html', artists=data)



@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

    # get the user search term
    search_term = request.form.get('search_term', '')

  # find all venues matching search term
  # including partial match and case-insensitive
    artists = Artist.query.filter(Artist.name.ilike('%{}%'.format(search_term))).all()
    response = {
      "count": len(artists),
      "data": []
        }
    for artist in artists:
        num_upcoming_shows = 0

        shows = Show.query.filter_by(venue_id=artist.id).all()

      # calculuate num of upcoming shows for each venue
        for show in shows:
            if show.start_time > datetime.now():
                num_upcoming_shows += 1
    # add venue data to response
        response['data'].append({
          "id": artist.id,
          "name": artist.name,
          "num_upcoming_shows": num_upcoming_shows,
          })
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

# get artist by id
    artist = Artist.query.filter_by(id=artist_id).first()

    # get all shows matching artist id
    shows = Show.query.filter_by(artist_id=artist_id).all()

    # returns upcoming shows
    def upcoming_shows():
        upcoming = []

        # if the show is upcoming, add to upcoming
        for show in shows:
            if show.start_time > datetime.now():
                upcoming.append({
                    "venue_id": show.venue_id,
                    "venue_name": Venue.query.filter_by(id=show.venue_id).first().name,
                    "venue_image_link": Venue.query.filter_by(id=show.venue_id).first().image_link,
                    "start_time": format_datetime(str(show.start_time))
                })
        return upcoming

    # returns past shows
    def past_shows():
        past = []

        # if show is in past, add to past
        for show in shows:
            if show.start_time < datetime.now():
                past.append({
                    "venue_id": show.venue_id,
                    "venue_name": Venue.query.filter_by(id=show.venue_id).first().name,
                    "venue_image_link": Venue.query.filter_by(id=show.venue_id).first().image_link,
                    "start_time": format_datetime(str(show.start_time))
                })
        return past

    # data for given artist
    data = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link,
        "past_shows": past_shows(),
        "upcoming_shows": upcoming_shows(),
        "past_shows_count": len(past_shows()),
        "upcoming_shows_count": len(upcoming_shows()),
    }

    # return artist page with data
    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
# get the matching artist by id
    artist = Artist.query.filter_by(id=artist_id).first()

    # artist data
    artist = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link
    }

    # set placeholders in form SelectField dropdown menus to current data
    form.state.process_data(artist['state'])
    form.genres.process_data(artist['genres'])
    form.seeking_venue.process_data(artist['seeking_venue'])

    # return edit template with artist data
    return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

     # catch exceptions with try-except block
    try:
        form = ArtistForm()

        # get the current artist by id
        artist = Artist.query.filter_by(id=artist_id).first()

        # load data from user input on form submit
        artist.name = form.name.data
        artist.genres = form.genres.data
        artist.city = form.city.data
        artist.state = form.state.data
        artist.phone = form.phone.data
        # validate phone
#        phone_validator(artist.phone)
        artist.facebook_link = form.facebook_link.data
        artist.image_link = form.image_link.data
        artist.website = form.website.data
        artist.seeking_venue = True if form.seeking_venue.data == 'Yes' else False
        artist.seeking_description = form.seeking_description.data

        # commit the changes
        db.session.commit()

        flash('Artist ' + request.form['name'] + ' was successfully updated!')
    except ValidationError as e:
        # catch validation errors from phone number

        # rollback session in the event of an exception
        db.session.rollback()
        flash('An error occurred. Artist ' +
              request.form['name'] + ' could not be listed. ' + str(e))
    except:
        # catch all other exceptions

        db.session.rollback()
        flash('An error occurred. Artist ' +
              request.form['name'] + ' could not be updated.')
    finally:
        # always close the session
        db.session.close()

    # return redirect to artist page

    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.filter_by(id=venue_id).first()

  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes

     # catch exceptions with try-except block
    try:
        form = VenueForm()

        # get venue by id
        venue = Venue.query.filter_by(id=venue_id).first()

        # load form data from user input
        venue.name = form.name.data
        venue.genres = form.genres.data
        venue.city = form.city.data
        venue.state = form.state.data
        venue.address = form.address.data
        venue.phone = form.phone.data
        # validate phone num
        #phone_validator(venue.phone)
        venue.facebook_link = form.facebook_link.data
        venue.website = form.website.data
        venue.image_link = form.image_link.data
        venue.seeking_talent = True if form.seeking_talent.data == 'Yes' else False
        venue.seeking_description = form.seeking_description.data

        # commit changes, flash message if successful
        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully updated!')
    except ValidationError as e:
        # catch errors from phone validation

        # rollback session if error
        db.session.rollback()
        flash('An error occurred. Venue ' +
              request.form['name'] + ' could not be listed. ' + str(e))
    except:
        # catch all other errors
        db.session.rollback()
        flash('An error occurred. Venue ' +
              request.form['name'] + ' could not be updated.')
    finally:
        # always close the session
        db.session.close()

    # return redirect to venue page
    return redirect(url_for('show_venue', venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # catch exceptions with try-except block
    try:
        name = request.form.get('name')
        city = request.form.get('city')
        state = request.form.get('state')
        phone = request.form.get('phone')
        genres = request.form.get('genres')
        facebook_link = request.form.get('facebook_link')
        website = request.form.get('website')
        image_link = request.form.get('image_link')
        seeking_venue = True if request.form.get('seeking_venue')== 'Yes' else False
        seeking_description = request.form.get('seeking_description')

        # create new artist from form data
        artist = Artist(name=name, city=city, state=state, phone=phone,
                        genres=genres, facebook_link=facebook_link,
                        website=website, image_link=image_link,
                        seeking_venue=seeking_venue,
                        seeking_description=seeking_description)

        # # # add new artist and commit session
        db.session.add(artist)
        db.session.commit()

        # flash message if successful
        flash('Artist ' + request.form['name'] + ' was successfully listed!')

    except:
        # catch all other exceptions
        db.session.rollback()
        flash('An error occurred. Artist ' +
              request.form['name'] + ' could not be listed.')
    finally:
        # always close the session
        db.session.close()

    # return template for home page
    return render_template('pages/home.html')



#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  # num_shows should be aggregated based on number of upcoming shows per venue.
    # get all the shows
    shows = Show.query.all()
    data = []
    # get venue and artist information for each show
    for show in shows:
        data.append({
            "venue_id": show.venue_id,
            "venue_name": Venue.query.filter_by(id=show.venue_id).first().name,
            "artist_id": show.artist_id,
            "artist_name": Artist.query.filter_by(id=show.artist_id).first().name,
            "artist_image_link": Artist.query.filter_by(id=show.artist_id).first().image_link,
            "start_time": format_datetime(str(show.start_time))
        })
    # return shows page with show data
    return render_template('pages/shows.html', shows=data)

  # data=[{
  #   "venue_id": 1,
  #   "venue_name": "The Musical Hop",
  #   "artist_id": 4,
  #   "artist_name": "Guns N Petals",
  #   "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "start_time": "2019-05-21T21:30:00.000Z"
  # }, {}....]


@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # catch exceptions with     try-except block
    try:
        # get user input data from form
        artist_id = request.form['artist_id']
        venue_id = request.form['venue_id']
        start_time = request.form['start_time']

        # create new show with user data
        show = Show(artist_id=artist_id, venue_id=venue_id,
                    start_time=start_time)

        # add show and commit session
        db.session.add(show)
        db.session.commit()

        # on successful db insert, flash success
        flash('Show was successfully listed!')
    except:
        # rollback if exception
        db.session.rollback()

        flash('An error occurred. Show could not be listed.')
    finally:
        db.session.close()

    # return homepage template
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
    app.run(debug=True)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
