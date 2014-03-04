# -*- coding: utf-8 -*-
"""
User State Module for the Recommendation System.

@author: ymiche
@version: 0.1
"""

import numpy as np
from geopy.distance import vincenty

import discogs_client as discogs
discogs.user_agent = 'MyRecommendationSystem/0.1'

from datetime import datetime

from song import Song


class UserState(object):
    # TODO : Finish this class.
    """
    Parameters
    ----------

    song            : (str, int)
                    The couple used to identify a song, the string is the
                    query_string for that song, and the integer is the release
                    id of the master release associated to it.

    """

    def __init__(self, imei, activity, location, timestamp, song):
        # Verify some things about the arguments
        # The IMEI should be a 15 digit number
        if not isinstance(imei, int):
            raise Exception('Given IMEI is not an integer.')
        if np.floor(np.log10(imei)) != 14:
            raise Exception('Given IMEI has not the proper length \
                                                        (15 digits).')
        # The activity should belong to the list of possible activities
        if activity not in ACTIVITIES.keys():
            raise Exception('Given activity is not recognized.')
        # The location needs to be a couple of floats
        if not isinstance(location, tuple):
            raise Exception('Given location is not a tuple.')
        if len(location) != 2:
            raise Exception('Given location does not have the correct number \
                of coordinates.')
        # The timestamp should be a datetime.datetime object
        if not isinstance(timestamp, datetime):
            raise Exception('Given timestamp is not a datetime object.')
        # The song should be of class Song
        if not isinstance(song, Song):
            raise Exception('Given song is not a Song object.')
        # Initialize the object
        self.imei = imei
        self.activity = activity
        self.location = location
        self.timestamp = timestamp
        self.song = song

    def distance(self, userstate2):
        """
        Proxy for the distance function between two user states.
        """
        return distance_user_states(self, userstate2)



def distance_user_states(userstate1, userstate2):
    """
    Returns the distance set between the two user_states.

    Parameters
    ----------
    userstate1          : user_state
                        The first user state
    userstate2          : same as for userstate1

    Returns
    -------
    Returns the distance set between userstate1 and userstate2.

    """
    if not isinstance(userstate1, UserState):
        raise Exception('Given first user state is not a valid one.')
    if not isinstance(userstate2, UserState):
        raise Exception('Given second user state is not a valid one.')

    distance = {'location': distance_locations(userstate1.location, \
                                                userstate2.location),
                'activity': distance_activities(userstate1.activity, \
                                                userstate2.activity),
                'song': userstate1.song.distance(userstate2.song),
                'time': distance_timestamps(userstate1.timestamp, \
                                                userstate2.timestamp),
               }

    return distance

def distance_locations(location1, location2):
    """
    Calculates the distance between two GPS locations.
    Uses the geopy module for Vincenty's formula.
    Returns a distance in meters.

    Parameters
    ----------
    location1           : (float, float)
                        A couple of GPS coordinates (WGS84 format)
    location2:          : same as for location1

    Returns
    -------
    A distance in meters between the two locations, using the Vincenty
    Formula.

    """
    if not isinstance(location1, tuple):
        raise Exception('Given first location is not a tuple.')
    if len(location1) != 2:
        raise Exception('Given first location does not have the correct \
            number of coordinates.')
    if not isinstance(location2, tuple):
        raise Exception('Given second location is not a tuple.')
    if len(location2) != 2:
        raise Exception('Given second location does not have the correct \
            number of coordinates.')
    return vincenty(location1, location2).m

def distance_activities(activity1, activity2):
    """
    Calculates the distance between two activities.

    Parameters
    ----------
    activity1           : str
                        One of the activities in activities.
    activity2           : same as for activity1

    Returns
    -------
    Returns a signed integer: If the integer is positive, the user has
    'accelerated', if negative, decelerated.
    """
    if activity1 not in ACTIVITIES.keys():
        raise Exception('Given first activity is not recognized.')
    if activity2 not in ACTIVITIES.keys():
        raise Exception('Given second activity is not recognized.')
    return ACTIVITIES[activity2] - ACTIVITIES[activity1]

def distance_timestamps(timestamp1, timestamp2):
    """
    Calculates the distance between two timestamps. Expects the timestamps to
    be datetime.datetime objects.

    Parameters
    ----------
    timestamp1          : datetime.datetime object
                        The initial datetime object
    timestamp2          : same as for timestamp1

    Returns
    -------
    Returns a datetime.timedelta instance between the two timestamps.
    """
    if not isinstance(timestamp1, datetime):
        raise Exception('Given first timestamp is not a datetime object.')
    if not isinstance(timestamp2, datetime):
        raise Exception('Given second timestamp is not a datetime object.')
    return timestamp2-timestamp1



# Global definitions
# Activities of a user
ACTIVITIES = {'STILL':      0,
              'ON_FOOT':    1,
              'ON_BICYCLE': 2,
              'IN_VEHICLE': 3}

