# This file implements functions and ressources used for file syncronization

import filecmp as fc
import os


def needs_syncing(path1, path2):

    '''
    Checks if a file needs syncing or not.

    Arguments:
        path1 & path2: Path to the file as String

    Return value:
        Path to file that is outdated or none.
    '''

    ret = fc.cmp(path1, path2)

    if (ret is False):  # files are different

        fs1 = os.stat(path1)
        fs2 = os.stat(path2)

        # sync the one which has a later modificaton date
        if (fs1.st_mtime > fs2.st_mtime):
            return path2
        else:
            return path1

    return ret


def list_files():
    '''
    Lists files that are under tracked for syncing.

    Arguments:
        none

    Return value:
        String which lists all files with path
    '''

    raise 'Not implemented yet'


def add_file(path):
    '''
    Adds a file to tracking list.

    Argument:
        Path to the file.

    Return value:
        True if it succeeded, False otherwise
    '''

    raise 'Not implemented yet'
