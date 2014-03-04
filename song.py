# -*- coding: utf-8 -*-
"""
Song Module for the Recommendation System.

@author: ymiche
@version: 0.1
"""

import numpy as np
from geopy.distance import vincenty
from geopy import geocoders

import discogs_client as discogs
discogs.user_agent = 'MyRecommendationSystem/0.1'


class Song(object):
    # FIXME : The querystring is insufficient to find the sensMe values
    # for the song. Need to have either a DB of values available for all the
    # songs, or a method that can extract it from the song file directly.
    """
    The class that implements how a song is represented in the system:

    Parameters
    ----------


    Attributes
    ----------
    query_string        : str
                        The query string used to identify the song.
    release_id          : int
                        The ID of the master release associated to the
                        song.
    genre               : str
                        The genre of the master release associated.
    style               : str
                        The style of the master release associated.
    tempo               : int
                        The tempo of the master release associated (seldom
                        available...)
    year                : int
                        The release year of the master release associated.
    country             : str
                        The country in which the master release was released \
                        first.
    sens_me             : (float, float)
                        A couple with the coordinates for that song in the \
                        sensMe system.
    """

    def __init__(self, query_string):
        if not isinstance(query_string, str):
            raise Exception('Given query string for song init is not a \
                                                                string.')
        if query_string == '':
            raise Exception('Given query string for song is empty.')
        self.query_string = query_string
        self.release_id = self.look_up_release_id()
        self.genre, self.style, self.tempo, self.year, self.country = \
            self.look_up_details_by_master_id()
        self.sens_me_values = self.sens_me()

    def look_up_release_id(self):
        """
        Find the release_id from the Discogs database.
        So far, this simply queries the Discogs API for the queryString,
        looks at the very first entry found, searches for the master release
        associated to it, and returns that master release's ID.

        As such, there is NO ID for a single song, but only for the whole
        album.

        Parameters
        ----------
        query_string         : str
                            The string with which to query the Discogs
                            database.

        Returns
        -------
        Returns the master_id associated with the query.
        """
        my_search = discogs.Search(self.query_string)
        release = my_search.results()[0]
        return release.data['id']

    def look_up_details_by_master_id(self):
        # FIXME : The current strategy is to use only one style and genre
        # for the distance calculations.
        """
        Look up all the available details of the given master_id and affect
        to the current song object.

        Parameters
        ----------
        master_id           : int
                            The internal Discogs ID for identifying the
                            release.

        Returns
        -------
        Returns the genre, style, tempo, year and country of the associated
        master release.
        Several attributes might be set to 'None' if nothing is available for
        that song in the database.

        """
        release = discogs.MasterRelease(self.release_id)
        release_data = release.data
        genre = 'None'
        style = 'None'
        tempo = 0
        year = 'None'
        country = 'None'
        if 'genres' in release_data.keys():
            genre = release_data['genres'][0]
        if 'styles' in release_data.keys():
            style = release_data['styles'][0]
        if 'tempo' in release_data.keys():
            tempo = release_data['tempo']
        if 'year' in release_data.keys():
            year = release_data['year']
        if 'country' in release_data.keys():
            country = release_data['country']

        return genre, style, tempo, year, country

    def sens_me(self):
        """
        Calculates the sensMe couple of values for the song.
        """
        # FIXME : So far, this returns a constant. Needs implementation of the
        # SensMe system and song handling.
        sens_me_values = (1.0, 1.0)
        return sens_me_values

    def distance(self, song2):
        """
        Proxy for the distance between songs functions.
        See distance_songs for help.
        """
        return distance_songs(self, song2)

    def details(self):
        """
        Prints the details of the current song object.
        """
        print 'Query String %s' % self.query_string
        print 'Genre %s' % self.genre
        print 'Style %s' % self.style
        print 'Release id %s' % self.release_id
        print 'Tempo %s' % self.tempo
        print 'Year %s' % self.year
        print 'Country %s' % self.country
        print 'SensMe {}'.format(self.sens_me_values)



def distance_genres(genre1, genre2):
    """
    Calculates the distance between two musical genres according to their
    'sensMe' 2D representation.

    Parameters
    ----------
    genre1              : str
                        One of the genres in GENRES
    genre2              : same as for genre1

    Returns
    -------
    Returns a float with the Euclidean distance between the two genres'
    representation in the sensMe 2D system.
    If one of the genres is 'None', the returned distance is -1.0
    """
    if genre1 not in GENRES.keys():
        raise Exception('Given first genre is not recognized.')
    if genre2 not in GENRES.keys():
        raise Exception('Given second genre is not recognized.')
    if genre1 == 'None' or genre2 == 'None':
        return -1.0
    return np.linalg.norm(np.array(GENRES[genre1]) - np.array(GENRES[genre2]))

def distance_styles(style1, style2):
    """
    Calculates the distance between two musical styles according to their
    'sensMe' 2D representation.

    Parameters
    ----------
    style1              : str
                        One of the styles in STYLES
    style2              : same as for style1

    Returns
    -------
    Returns a float with the Euclidean distance between the two styles'
    representation in the sensMe 2D system.
    If one of the styles is 'None', the returned distance is -1.0
    """
    if style1 not in STYLES.keys():
        raise Exception('Given first style is not recognized.')
    if style2 not in STYLES.keys():
        raise Exception('Given second style is not recognized.')
    if style1 == 'None' or style2 == 'None':
        return -1.0
    return np.linalg.norm(np.array(STYLES[style1]) - np.array(STYLES[style2]))

def distance_countries(country1, country2):
    """
    Calculates the distance between the two countries, in meters.
    Uses Google Engine to return GPS coordinates for the country,
    and Vincenty's formula for the distance calculation again.

    Parameters
    ----------
    country1            : str
                        The name of the country (as recognizable by Google)
    country2            : same as for country1

    Returns
    -------
    A distance in meters between the two countries, using the Vincenty
    Formula.
    If one of the countries is 'None', the returned distance is -1.0

    """
    if not isinstance(country1, str):
        raise Exception('Given first country is not a string.')
    if not isinstance(country2, str):
        raise Exception('Given second country is not a string.')
    if country1 == 'None' or country2 == 'None':
        return -1.0
    my_geocoder = geocoders.GoogleV3()
    try:
        _, coordinates1 = my_geocoder.geocode(country1)
        _, coordinates2 = my_geocoder.geocode(country2)
    except TypeError:
        raise Exception('Could not geocode the country name.')
    return vincenty(coordinates1, coordinates2).m

def distance_years(year1, year2):
    """
    Calculates the distance between two years, expressed in years.

    Parameters
    ----------
    year1           : int
                    A year in int format
    year2           : same as for year1

    Returns
    -------
    The number of years between the two years.
    The value wille be negative if year1 is smaller than year2.
    """
    if not isinstance(year1, int):
        raise Exception('Given first year is not an integer.')
    if not isinstance(year2, int):
        raise Exception('Given second year is not an integer.')
    return year1 - year2

def distance_tempos(tempo1, tempo2):
    """
    Calculates the distance between two tempos.

    Parameters
    ----------
    tempo1          : int
                    A tempo in int format
    tempo2          : same as for tempo1

    Returns
    -------
    The difference in tempo between the two values.
    If tempo1 is smaller than tempo2, the value will be negative.
    """
    if not isinstance(tempo1, int):
        raise Exception('Given first tempo is not an integer.')
    if not isinstance(tempo2, int):
        raise Exception('Given second tempo is not an integer.')
    return tempo1 - tempo2

def distance_sens_me(sens_me1, sens_me2):
    """
    Calculates the distance between two sensMe couples of float.
    Returns a float for the distance.

    Parameters
    ----------
    sens_me1        : (float, float)
                    A couple of values in the sensMe plane
    sens_me2        : same as for sens_me1

    Returns
    -------
    Returns the Euclidean distance between the two sens_me points.
    """
    if not isinstance(sens_me1, tuple):
        raise Exception('Given first sensMe is not a tuple.')
    if len(sens_me1) != 2:
        raise Exception('Given first sensMe does not have the correct \
            number of coordinates.')
    if not isinstance(sens_me2, tuple):
        raise Exception('Given second sensMe is not a tuple.')
    if len(sens_me2) != 2:
        raise Exception('Given second sensMe does not have the correct \
            number of coordinates.')
    return np.linalg.norm(np.array(sens_me1)-np.array(sens_me2))

def distance_songs(song1, song2):
    """
    Calculates the distance between the given songs.
    Returns a set of distances for all the songs attributes.

    Parameters
    ----------
    song1           : song object
                    A song object
    song2           : same as for song1

    Returns
    -------
    Returns a dictionary of all the distances between the different
    attributes of the two songs, if available.
    """
    if not isinstance(song1, Song):
        raise Exception('Given first song is not a song object.')
    if not isinstance(song2, Song):
        raise Exception('Given second song is not a song object.')
    distance_set = {'distance_genre': distance_genres(song1.genre, \
                                                        song2.genre),
                    'distance_style': distance_styles(song1.style, \
                                                        song2.style),
                    'distance_country': distance_countries(song1.country, \
                                                        song2.country),
                    'distance_year': distance_years(song1.year, \
                                                        song2.year),
                    'distance_tempo': distance_tempos(song1.tempo, \
                                                        song2.tempo),
                    'distance_sens_me': distance_sens_me(song1.sens_me_values, \
                                                        song2.sens_me_values),
                    }
    return distance_set




# Musical Genres
# The genres are coded using a SensMe couple to be able to calculate a
# distance between them
GENRES = {'Rock': (0.0, 0.0),
          'Pop': (0.0, 0.0),
          'Electronic': (0.0, 0.0),
          'Hip Hop': (0.0, 0.0),
          'Funk/Soul': (0.0, 0.0),
          'Jazz': (0.0, 0.0),
          'Folk/World/Country': (0.0, 0.0),
          'Non-Music': (0.0, 0.0),
          'Stage & Screen': (0.0, 0.0),
          'Reggae': (0.0, 0.0),
          'Latin': (0.0, 0.0),
          'Classical': (0.0, 0.0),
          'Blues': (0.0, 0.0),
          'Children\'s': (0.0, 0.0),
          'Brass & Military': (0.0, 0.0),
        }


# Musical Styles
# The styles are coded using a SensMe couple to be able to calculate a
# distance between them
STYLES = {'Soundtrack': (0.0, 0.0),
          'Score': (0.0, 0.0),
          'Modern Classical': (0.0, 0.0),
          'Synth-pop': (0.0, 0.0),
          'Ambient': (0.0, 0.0),
          'Experimental': (0.0, 0.0),
          'Disco': (0.0, 0.0),
          'Pop Rock': (0.0, 0.0),
          'Theme': (0.0, 0.0),
          'Downtempo': (0.0, 0.0),
          'Abstract': (0.0, 0.0),
          'Electro': (0.0, 0.0),
          'Alternative Rock': (0.0, 0.0),
          'House': (0.0, 0.0),
          'Industrial': (0.0, 0.0),
          'Easy Listening': (0.0, 0.0),
          'Techno': (0.0, 0.0),
          'Contemporary': (0.0, 0.0),
          'Ballad': (0.0, 0.0),
          'Dark Ambient': (0.0, 0.0),
          'Funk': (0.0, 0.0),
          'Minimal': (0.0, 0.0),
          'New Wave': (0.0, 0.0),
          'Indie Rock': (0.0, 0.0),
          'Breakbeat': (0.0, 0.0),
          'Soft Rock': (0.0, 0.0),
          'Leftfield': (0.0, 0.0),
          'Prog Rock': (0.0, 0.0),
          'New Age': (0.0, 0.0),
          'Soul': (0.0, 0.0),
          'Hip Hop': (0.0, 0.0),
          'Vocal': (0.0, 0.0),
          'Breaks': (0.0, 0.0),
          'Psychedelic Rock': (0.0, 0.0),
          'Trip Hop': (0.0, 0.0),
          'Musique Concrète': (0.0, 0.0),
          'Avantgarde': (0.0, 0.0),
          'Musical': (0.0, 0.0),
          'Rock & Roll': (0.0, 0.0),
          'Classic Rock': (0.0, 0.0),
          'Noise': (0.0, 0.0),
          'RnB/Swing': (0.0, 0.0),
          'Heavy Metal': (0.0, 0.0),
          'Classical': (0.0, 0.0),
          'Contemporary Jazz': (0.0, 0.0),
          'Hard Rock': (0.0, 0.0),
          'Drum n Bass': (0.0, 0.0),
          'Trance': (0.0, 0.0),
          'Jazz-Funk': (0.0, 0.0),
          'Drone': (0.0, 0.0),
          'Italo-Disco': (0.0, 0.0),
          'Europop': (0.0, 0.0),
          'Art Rock': (0.0, 0.0),
          'Euro House': (0.0, 0.0),
          'Pop Rap': (0.0, 0.0),
          'Folk Rock': (0.0, 0.0),
          'Punk': (0.0, 0.0),
          'Big Beat': (0.0, 0.0),
          'Spoken Word': (0.0, 0.0),
          'Chanson': (0.0, 0.0),
          'Folk': (0.0, 0.0),
          'Acoustic': (0.0, 0.0),
          'Tribal': (0.0, 0.0),
          'Chiptune': (0.0, 0.0),
          'IDM': (0.0, 0.0),
          'Lounge': (0.0, 0.0),
          'Bollywood': (0.0, 0.0),
          'Country Rock': (0.0, 0.0),
          'Future Jazz': (0.0, 0.0),
          'Rhythm & Blues': (0.0, 0.0),
          'Hindustani': (0.0, 0.0),
          'Krautrock': (0.0, 0.0),
          'Smooth Jazz': (0.0, 0.0),
          'Hi NRG': (0.0, 0.0),
          'Latin': (0.0, 0.0),
          'Blues Rock': (0.0, 0.0),
          'Dub': (0.0, 0.0),
          'Nu Metal': (0.0, 0.0),
          'Modern': (0.0, 0.0),
          'Neo-Classical': (0.0, 0.0),
          'Post Rock': (0.0, 0.0),
          'Big Band': (0.0, 0.0),
          'Reggae-Pop': (0.0, 0.0),
          'J-pop': (0.0, 0.0),
          'Fusion': (0.0, 0.0),
          'Dialogue': (0.0, 0.0),
          'Arena Rock': (0.0, 0.0),
          'Symphonic Rock': (0.0, 0.0),
          'Progressive House': (0.0, 0.0),
          'Field Recording': (0.0, 0.0),
          'Goth Rock': (0.0, 0.0),
          'Illbient': (0.0, 0.0),
          'Brit Pop': (0.0, 0.0),
          'Space-Age': (0.0, 0.0),
          'Jazz-Rock': (0.0, 0.0),
          'Romantic': (0.0, 0.0),
          'Country': (0.0, 0.0),
          'Soul-Jazz': (0.0, 0.0),
          'Special Effects': (0.0, 0.0),
          'Instrumental': (0.0, 0.0),
          'Psychedelic': (0.0, 0.0),
          'Novelty': (0.0, 0.0),
          'Movie Effects': (0.0, 0.0),
          'Lo-Fi': (0.0, 0.0),
          'Comedy': (0.0, 0.0),
          'Swing': (0.0, 0.0),
          'Darkwave': (0.0, 0.0),
          'Space Rock': (0.0, 0.0),
          'Tech House': (0.0, 0.0),
          'Free Improvisation': (0.0, 0.0),
          'Rhythmic Noise': (0.0, 0.0),
          'Schlager': (0.0, 0.0),
          'Acid Jazz': (0.0, 0.0),
          'Parody': (0.0, 0.0),
          'Post-Modern': (0.0, 0.0),
          'Acid': (0.0, 0.0),
          'Surf': (0.0, 0.0),
          'Gangsta': (0.0, 0.0),
          'Reggae': (0.0, 0.0),
          'Dubstep': (0.0, 0.0),
          'Ethereal': (0.0, 0.0),
          'Hardcore': (0.0, 0.0),
          'Neofolk': (0.0, 0.0),
          'Power Electronics': (0.0, 0.0),
          'Free Jazz': (0.0, 0.0),
          'Deep House': (0.0, 0.0),
          'Glitch': (0.0, 0.0),
          'Progressive Trance': (0.0, 0.0),
          'Interview': (0.0, 0.0),
          'Bossa Nova': (0.0, 0.0),
          'EBM': (0.0, 0.0),
          'Freestyle': (0.0, 0.0),
          'Latin Jazz': (0.0, 0.0),
          'Rockabilly': (0.0, 0.0),
          'Cool Jazz': (0.0, 0.0),
          'Ska': (0.0, 0.0),
          'Acid House': (0.0, 0.0),
          'Jazzdance': (0.0, 0.0),
          'Medieval': (0.0, 0.0),
          'Avant-garde Jazz': (0.0, 0.0),
          'Poetry': (0.0, 0.0),
          'Power Pop': (0.0, 0.0),
          'Glam': (0.0, 0.0),
          'Opera': (0.0, 0.0),
          'Baroque': (0.0, 0.0),
          'Ragga HipHop': (0.0, 0.0),
          'Garage Rock': (0.0, 0.0),
          'Hip-House': (0.0, 0.0),
          'Neo-Romantic': (0.0, 0.0),
          'Monolog': (0.0, 0.0),
          'Radioplay': (0.0, 0.0),
          'Broken Beat': (0.0, 0.0),
          'Happy Hardcore': (0.0, 0.0),
          'Italodance': (0.0, 0.0),
          'Jungle': (0.0, 0.0),
          'Shoegaze': (0.0, 0.0),
          'Shoegazer': (0.0, 0.0),
          'Thug Rap': (0.0, 0.0),
          'Garage House': (0.0, 0.0),
          'African': (0.0, 0.0),
          'Cut-up/DJ': (0.0, 0.0),
          'Afrobeat': (0.0, 0.0),
          'Conscious': (0.0, 0.0),
          'Goa Trance': (0.0, 0.0),
          'Post-Punk': (0.0, 0.0),
          'Speech': (0.0, 0.0),
          'Hard House': (0.0, 0.0),
          'Black Metal': (0.0, 0.0),
          'Gospel': (0.0, 0.0),
          'Grunge': (0.0, 0.0),
          'Salsa': (0.0, 0.0),
          'Samba': (0.0, 0.0),
          'Story': (0.0, 0.0),
          'Thrash': (0.0, 0.0),
          'Berlin-School': (0.0, 0.0),
          'Electric Blues': (0.0, 0.0),
          'Louisiana Blues': (0.0, 0.0),
          'Promotional': (0.0, 0.0),
          'Psy-Trance': (0.0, 0.0),
          'Audiobook': (0.0, 0.0),
          'Bossanova': (0.0, 0.0),
          'Dub Techno': (0.0, 0.0),
          'Nursery Rhymes': (0.0, 0.0),
          'Post Bop': (0.0, 0.0),
          'Stoner Rock': (0.0, 0.0),
          'Dancehall': (0.0, 0.0),
          'Emo': (0.0, 0.0),
          'Flamenco': (0.0, 0.0),
          'Celtic': (0.0, 0.0),
          'Cha-Cha': (0.0, 0.0),
          'Death Metal': (0.0, 0.0),
          'Mambo': (0.0, 0.0),
          'Political': (0.0, 0.0),
          'Breakcore': (0.0, 0.0),
          'Delta Blues': (0.0, 0.0),
          'Doo Wop': (0.0, 0.0),
          'Doom Metal': (0.0, 0.0),
          'Marches': (0.0, 0.0),
          'Music Hall': (0.0, 0.0),
          'Religious': (0.0, 0.0),
          'Afro-Cuban Jazz': (0.0, 0.0),
          'Jazzy Hip-Hop': (0.0, 0.0),
          'Mod': (0.0, 0.0),
          'Neo Soul': (0.0, 0.0),
          'UK Garage': (0.0, 0.0),
          'Bluegrass': (0.0, 0.0),
          'Psychobilly': (0.0, 0.0),
          'Tribal House': (0.0, 0.0),
          'Ghetto': (0.0, 0.0),
          'Grindcore': (0.0, 0.0),
          'Math Rock': (0.0, 0.0),
          'Modal': (0.0, 0.0),
          'Therapy': (0.0, 0.0),
          'Aboriginal': (0.0, 0.0),
          'Bass Music': (0.0, 0.0),
          'Country Blues': (0.0, 0.0),
          'Eurodance': (0.0, 0.0),
          'Funk Metal': (0.0, 0.0),
          'Karaoke': (0.0, 0.0),
          'Bop': (0.0, 0.0),
          'Calypso': (0.0, 0.0),
          'Dixieland': (0.0, 0.0),
          'Electro House': (0.0, 0.0),
          'Hard Trance': (0.0, 0.0),
          'New Jack Swing': (0.0, 0.0),
          'Swingbeat': (0.0, 0.0),
          'Technical': (0.0, 0.0),
          'Beat': (0.0, 0.0),
          'Bhangra': (0.0, 0.0),
          'Education': (0.0, 0.0),
          'Hardstyle': (0.0, 0.0),
          'Indie Pop': (0.0, 0.0),
          'Ragtime': (0.0, 0.0),
          'Southern Rock': (0.0, 0.0),
          'Tango': (0.0, 0.0),
          'Free Funk': (0.0, 0.0),
          'Gabber': (0.0, 0.0),
          'Harmonica Blues': (0.0, 0.0),
          'Impressionist': (0.0, 0.0),
          'Military': (0.0, 0.0),
          'New Beat': (0.0, 0.0),
          'Oi': (0.0, 0.0),
          'Zydeco': (0.0, 0.0),
          'Acid Rock': (0.0, 0.0),
          'Afro-Cuban': (0.0, 0.0),
          'Cumbia': (0.0, 0.0),
          'Electroclash': (0.0, 0.0),
          'MPB': (0.0, 0.0),
          'No Wave': (0.0, 0.0),
          'Ranchera': (0.0, 0.0),
          'Rumba': (0.0, 0.0),
          'Cajun': (0.0, 0.0),
          'Chinese Classical': (0.0, 0.0),
          'Educational': (0.0, 0.0),
          'Grime': (0.0, 0.0),
          'Hardcore Hip-Hop': (0.0, 0.0),
          'Indian Classical': (0.0, 0.0),
          'Ragga': (0.0, 0.0),
          'Renaissance': (0.0, 0.0),
          'Soca': (0.0, 0.0),
          'Speedcore': (0.0, 0.0),
          'Batucada': (0.0, 0.0),
          'Bounce': (0.0, 0.0),
          'Cubano': (0.0, 0.0),
          'Euro-Disco': (0.0, 0.0),
          'Gamelan': (0.0, 0.0),
          'Gypsy Jazz': (0.0, 0.0),
          'Hard Bop': (0.0, 0.0),
          'Jumpstyle': (0.0, 0.0),
          'Minimal Techno': (0.0, 0.0),
          'Modern Electric Blues': (0.0, 0.0),
          'Nordic': (0.0, 0.0),
          'Norteño': (0.0, 0.0),
          'Persian Classical': (0.0, 0.0),
          'Polka': (0.0, 0.0),
          'Reggae Gospel': (0.0, 0.0),
          'Skweee': (0.0, 0.0),
          'Speed Metal': (0.0, 0.0),
          'Steel Band': (0.0, 0.0),
          'Tejano': (0.0, 0.0),
          'Bayou Funk': (0.0, 0.0),
          'Brass Band': (0.0, 0.0),
          'Canzone Napoletana': (0.0, 0.0),
          'Crunk': (0.0, 0.0),
          'DJ Battle Tool': (0.0, 0.0),
          'Enka': (0.0, 0.0),
          'Gagaku': (0.0, 0.0),
          'Hard Techno': (0.0, 0.0),
          'Hyphy': (0.0, 0.0),
          'Laïkó': (0.0, 0.0),
          'Makina': (0.0, 0.0),
          'Overtone Singing': (0.0, 0.0),
          'P.Funk': (0.0, 0.0),
          'Piano Blues': (0.0, 0.0),
          'Public Service Announcement': (0.0, 0.0),
          'Rocksteady': (0.0, 0.0),
          'Roots Reggae': (0.0, 0.0),
          'Sermon': (0.0, 0.0),
          'Speed Garage': (0.0, 0.0),
          'Bachata': (0.0, 0.0),
          'Britcore': (0.0, 0.0),
          'Chicago Blues': (0.0, 0.0),
          'Corrido': (0.0, 0.0),
          'Deathrock': (0.0, 0.0),
          'Dub Poetry': (0.0, 0.0),
          'Early': (0.0, 0.0),
          'Favela Funk': (0.0, 0.0),
          'Gogo': (0.0, 0.0),
          'Horrorcore': (0.0, 0.0),
          'Klezmer': (0.0, 0.0),
          'Korean Court Music': (0.0, 0.0),
          'Lovers Rock': (0.0, 0.0),
          'Metalcore': (0.0, 0.0),
          'Nueva Cancion': (0.0, 0.0),
          'Ottoman Classical': (0.0, 0.0),
          'Pachanga': (0.0, 0.0),
          'Pacific': (0.0, 0.0),
          'Philippine Classical': (0.0, 0.0),
          'Pop Punk': (0.0, 0.0),
          'Quechua': (0.0, 0.0),
          'Romani': (0.0, 0.0),
          'Schranz': (0.0, 0.0),
          'Screw': (0.0, 0.0),
          'Sámi Music': (0.0, 0.0),
          'Trova': (0.0, 0.0),
          'Viking Metal': (0.0, 0.0),
          'Zouk': (0.0, 0.0),
          'Éntekhno': (0.0, 0.0),
}
