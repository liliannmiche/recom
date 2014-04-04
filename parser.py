# -*- coding: utf-8 -*-
"""
Parser Module for the Recommendation System.

@author: ymiche
@version: 0.1
"""

from song import Song
from user_state import UserState

from datetime import datetime
import csv
import cPickle as pkl
import sys
import discogs_client as discogs


def parse_csv(file_path):
    """
    Parse the data from the CSV file to a dict of user states.

    Parameters
    ----------

    Returns
    -------
    A dict of user states, imei as keys, values are list of user states
    in the order they occurred.
    """
    user_states_dict = {}
    with open(file_path, 'rb') as csvfile:
        if __debug__:
            print 'CSV file has header, skipping first line.'
        if csv.Sniffer().has_header(csvfile.read(1024)):
            csvfile.seek(0)
            csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
            csvreader.next()
        else:
            csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in csvreader:
            if __debug__:
                print 'Iterating over rows of CSV file.'
            try:
                imei = row[2]
                timestamp = datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S')
                if __debug__:
                    print 'Creating song object.'
                song = Song(row[4])
                activity = row[8]
                location = tuple([float(coordinate) for coordinate in row[7].split(',')])
                if __debug__:
                    print 'Creating user state object.'
                user_state = UserState(imei, activity, location, timestamp, song)
                user_state.write()
            except discogs.DiscogsAPIError:
                pass


def main():
    """
    Runs the parsing on the csv file, and writes the updates to the user
    states to disk.
    """
    args = sys.argv
    if __debug__:
        print 'Starting the parsing of CSV file...'
    parse_csv(args[1])



if __name__ == '__main__':
    main()
