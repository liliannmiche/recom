# -*- coding: utf-8 -*-
"""
Parser Module for the Recommendation System.

@author: ymiche
@version: 0.1
"""

from user_state import UserState


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


    return user_states_dict


def write_user_states_to_disk(user_states_dict):
    """
    Writes the user states in the dictionary to disk.
    """
    for imei in user_states_dict.keys():
        for user_state in user_states_dict['imei']:
            user_state.write()


def main(file_path):
    """
    Runs the parsing on the csv file, and writes the updates to the user
    states to disk.
    """
    user_states_dict = parse_csv(file_path)
    write_user_states_to_disk(user_states_dict)


if __name___ == '__main__':
    main()
