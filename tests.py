# -*- coding: utf-8 -*-
"""
Tests for the Recom system

@author: ymiche
@version: 0.1
"""

from datetime import datetime
from song import Song
from user_state import UserState


def main():
    """
    Main test function for now.
    """
    imei1 = 123456789012345
    activity1 = 'STILL'
    location1 = (41.512107999999998, -81.607044999999999)
    timestamp1 = datetime.now()
    song1 = Song('Barbie Girl')

    song1.details()

    imei2 = 234567890123456
    activity2 = 'STANDING'
    location2 = (41.512107999999998, -81.607044999999999)
    timestamp2 = datetime.now()
    song2 = Song('Turn Back Time')

    song2.details()

    print song1.distance(song2)

    userstate1 = UserState(imei1, activity1, location1, timestamp1, song1)
    userstate2 = UserState(imei2, activity2, location2, timestamp2, song2)

    print userstate1.distance(userstate2)


if __name__ == '__main__':
    main()
