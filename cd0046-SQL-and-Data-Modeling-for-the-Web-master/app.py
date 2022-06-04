# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import json
import sys
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from model import *

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migration = Migrate(app, db)


# TODO: connect to a local postgresql database

# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#




# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime


# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#

@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    data = []
    city_states = Venue.query.with_entities(Venue.city, Venue.state).distinct().all()
    for city_state in city_states:
        city = city_state[0]
        state = city_state[1]
        venues = Venue.query.filter_by(city=city, state=state).all()
        data.append({
            "city": city,
            "state": state,
            "venues": venues
        })

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    search_term = request.form.get('search_term', '')
    venues = db.session.query(Venue).filter(Venue.name.ilike(r"%{}%".format(search_term))).all()  # code from stack overflow

    data = []
    count = len(venues)
    for venue in venues:
        data.append({
            "id": venue.id,
            "name": venue.name,

        })

        response = {'count': count, 'data': data}

    um_upcoming_shows": 0,
    
    return render_template('pages/search_venues.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    venues = Venue.query.get(venue_id)
    pass_shows_count = 0
    datas = []
    past_shows = []
    upcoming_shows = []
    past_shows_query = db.session.query(Show).join(Artist).filter(Show.venue_id == venue_id).filter(
        Show.start_time < datetime.now()).all()
    upcoming_shows_query = db.session.query(Show).join(Artist).filter(Show.venue_id == venue_id).filter(
        Show.start_time > datetime.now()).all()
    if len(past_shows_query) > 0:
        for shows in past_shows_query:
            past_shows.append({
                "artist_id": shows.artist_id,
                "artist_name": shows.artist.name,
                "artist_image_link": shows.artist.image_link,
                "start_time": shows.start_time.strftime('%Y-%m-%d %H:%M:%S')
            })
    else:
        past_shows = []

    if len(upcoming_shows_query) > 0:
        for shows in upcoming_shows_query:
            upcoming_shows.append({
                "artist_id": shows.artist_id,
                "artist_name": shows.artist.name,
                "artist_image_link": shows.artist.image_link,
                "start_time": shows.start_time.strftime("%Y-%m-%d %H:%M:%S")
            })
    else:
        upcoming_shows = []

    datas.append({
        "id": venues.id,
        "name": venues.name,
        "genres": venues.genres,
        "address": venues.address,
        "city": venues.city,
        "state": venues.state,
        "phone": venues.phone,
        "website": venues.website_link,
        "facebook_link": venues.facebook_link,
        "seeking_talent": venues.seeking_talent,
        "seeking_description": venues.seeking_description,
        "image_link": venues.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
    })

    
    data = list(filter(lambda d: d['id'] == venue_id, datas))[0]
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
    error = False
    try:
        venue = Venue(
            name=form.name.data,
            city=form.city.data,
            phone=form.phone.data,
            state=form.state.data,
            address=form.address.data,
            genres=request.form.getlist('genre'),
            facebook_link=form.facebook_link.data,
            image_link=form.image_link.data,
            website_link=form.website_link.data,
            seeking_talent=form.seeking_talent.data,
            seeking_description=form.seeking_description.data
        )
        db.session.add(venue)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
        if error:
            flash('An error occured. Venue ' +
                  request.form['name'] + ' Could not be listed!')
        else:
            flash('Venue ' + request.form['name'] +
                  ' was successfully listed!')

    return render_template('pages/home.html')



@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    error = False
    try:
        venue = Venue.query.get(venue_id)
        db.session.delete(venue)
        db.session.commit()
    except():
        db.session.rollback()
        error = True
    finally:
        db.session.close()
    if error:

        flash(f'An error occurred. Venue {venue_id} could not be deleted.')
        abort(500)
    else:
        flash(f'Venue {venue_id} was successfully deleted.')

    return render_template('pages/home.html')

    


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    artists = Artist.query.all()
    data = []
    for artist in artists:
        data.append({
            "id": artist.id,
            "name": artist.name,

        })
    
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    search_term = request.form.get('search_term', '')
    artists = db.session.query(Artist).filter(Artist.name.ilike(r"%{}%".format(search_term))).all() # code from stackoverflow

    data = []
    count = len(artists)
    for artist in artists:
        data.append({
            "id": artist.id,
            "name": artist.name,

        })

        response = {'count': count, 'data': data}
        
    return render_template('pages/search_artists.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artist table, using artist_id
    artists = Artist.query.get(artist_id)
    pass_shows_count = 0
    datas = []
    past_shows = []
    upcoming_shows = []
    past_shows_query = db.session.query(Show).join(Artist).filter(Show.artist_id == artist_id).filter(
        Show.start_time < datetime.now()).all()
    upcoming_shows_query = db.session.query(Show).join(Artist).filter(Show.artist_id == artist_id).filter(
        Show.start_time > datetime.now()).all()
    if len(past_shows_query) > 0:
        for shows in past_shows_query:
            past_shows.append({
                "artist_id": shows.artist_id,
                "artist_name": shows.artist.name,
                "artist_image_link": shows.artist.image_link,
                "start_time": shows.start_time.strftime('%Y-%m-%d %H:%M:%S')
            })
    else:
        past_shows = []

    if len(upcoming_shows_query) > 0:
        for shows in upcoming_shows_query:
            upcoming_shows.append({
                "artist_id": shows.artist_id,
                "artist_name": shows.artist.name,
                "artist_image_link": shows.artist.image_link,
                "start_time": shows.start_time.strftime("%Y-%m-%d %H:%M:%S")
            })
    else:
        upcoming_shows = []

    datas.append({
        "id": artists.id,
        "name": artists.name,
        "city": artists.city,
        "state": artists.state,
        "phone": artists.phone,
        "website": artists.website_link,
        "facebook_link": artists.facebook_link,
        "seeking_venue": artists.seeking_venue,
        "genres": artists.genres,
        "seeking_description": artists.seeking_description,
        "image_link": artists.image_link,
        "upcoming_shows": upcoming_shows,
        "past_shows": past_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
    })
   
    data = list(filter(lambda d: d['id'] == artist_id, datas))[0]
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
        form.facebook_link.data = artist.facebook_link
        form.image_link.data = artist.image_link
        form.website_link.data = artist.website_link
        form.seeking_description.data = artist.seeking_description
        form.genres.data = artist.genres
        form.seeking_venue.data = artist.seeking_venue

   
    #   # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    form = ArtistForm()
    artists = Artist.query.get(artist_id)
    try:
        artists.name = form.name.data
        artists.genres = request.form.getlist('genres')
        artists.city = form.city.data
        artists.state = form.state.data
        artists.phone = form.phone.data
        artists.website_link = form.website_link.data
        artists.facebook_link = form.facebook_link.data
        artists.looking_for_venues = form.seeking_venue.data
        artists.seeking_description = form.seeking_description.data
        artists.image_link = form.image_link.data

        # db.session.add(artists)
        db.session.commit()
        flash("Edited successful!")

    except Exception as error:
        print(error)
        db.session.rollback()
        flash("OPP! unsuccessful!")
    return redirect(url_for('show_artist', artist_id=artist_id))

    # TODO: take values from the form submitted, and update existing

    # artist record with ID <artist_id> using the new attributes


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.get(venue_id)
    if venue:
        form.name.data = venue.name
        form.city.data = venue.city
        form.state.data = venue.state
        form.address.data = venue.address
        form.phone.data = venue.phone
        form.facebook_link.data = venue.facebook_link
        form.image_link.data = venue.image_link
        form.website_link.data = venue.website_link
        form.seeking_description.data = venue.seeking_description
        form.genres.data = venue.genres
        form.seeking_talent.data = venue.seeking_talent

    return render_template('forms/edit_venue.html', form=form, venue=venue)


venue = {
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


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    form = VenueFormForm()
    venues = Venue.query.get(venue_id)
    try:
        venues.name = form.name.data
        venues.genres = request.form.getlist('genres')
        venues.city = form.city.data
        venues.state = form.state.data
        venues.address = form.address.data
        venues.phone = form.phone.data
        venues.website_link = form.website_link.data
        venues.facebook_link = form.facebook_link.data
        venues.seeking_talent = form.seeking_talent.data
        venues.seeking_description = form.seeking_description.data
        venues.image_link = form.image_link.data

        # db.session.add(artists)
        db.session.commit()
        flash(" Venue edited successful!")

    except Exception as error:
        print(error)
        db.session.rollback()
        flash("OPP! unsuccessful!")
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
    error = False
    try:
        artist = Artist(
            name=form.name.data,
            city=form.city.data,
            phone=form.phone.data,
            state=form.state.data,
            genres=form.genres.data,
            facebook_link=form.facebook_link.data,
            image_link=form.image_link.data,
            website_link=form.website_link.data,
            seeking_venue=form.seeking_venue.data,
            seeking_description=form.seeking_description.data
        )
        db.session.add(artist)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
        if error:
            flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
        else:
            flash('Artist ' + request.form['name'] + ' was successfully listed!')

    return render_template('pages/home.html')

    
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
            "venue_name": show.venue.name,
            "artist_id": show.artist_id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": format_datetime(str(show.start_time))
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
    form = ShowForm(request.form)
    error = False
    try:
        show = Show(
            artist_id=form.artist_id.data,
            venue_id=form.venue_id.data,
            start_time=str(form.start_time.data),
        )
        db.session.add(show)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
        if error:
            flash('An error occurred. Show could not be listed.')
        else:
            flash('Show was successfully listed!')

    # on successful db insert, flash success

    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g.,
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

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
