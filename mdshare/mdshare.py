#   This file is part of the markovmodel/mdshare project.
#   Copyright (C) 2017 Computational Molecular Biology Group,
#   Freie Universitaet Berlin (GER)
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import errno
from urllib.request import urlretrieve
from urllib.error import HTTPError

def download_file(repository, remote_filename, local_path=None):
    '''Download a file.

    Arguments:
        repository (str): URL of the remote source directory
        remote_filename (str): name of the file in the repository
        local_filename (str): local path where the file should be saved
    '''
    filename, message = urlretrieve(
        repository + remote_filename,
        filename=local_filename)
    return filename

def attempted_download(
    repository, remote_filename, local_path=None,
    max_attempts=3, delay=3, blur=0.1):
    '''Retry to download a file several times if necessary.

    Arguments:
        repository (str): URL of the remote source directory
        remote_filename (str): name of the file in the repository
        local_filename (str): local path where the file should be saved
        max_attempts (int): number of download attempts
        delay (int): delay between attempts in seconds
        blur (float): degree of blur to randomize the delay
    '''
    attempt = 0
    while attempt < max_attempts:
        attempt += 1
        try:
            filename = download_file(
                repository, remote_filename, local_path=local_path)
            return filename
        except HTTPError as e:
            if e.code not in [408, 500, 503, 504]:
                raise
        except IOError as e:
            if e.errno not in [110]:
                raise
    raise RuntimeError(
        'could not download file: ' + str(repository + remote_filename))

def lazy_download(
    repository, remote_filename, working_directory='.', local_filename=None,
    max_attempts=3, delay=3, blur=0.1):
    '''Download a file if it is necessary.

    Arguments:
        repository (str): URL of the remote source directory
        remote_filename (str): name of the file in the repository
        working_directory (str): directory where the file should be saved
        local_filename (str): name under which the file should be saved
        max_attempts (int): number of download attempts
        delay (int): delay between attempts in seconds
        blur (float): degree of blur to randomize the delay
    '''
    if working_directory is None:
        print('downloading to tmp')
        local_path = None
    else:
        try:
            os.makedirs(working_directory, exist_ok=True)
            print('creating wdir [-p]: ' + str(working_directory))
        except OSError as e:
            if e.errno == errno.EEXIST and os.path.isdir(working_directory):
                print('existing wdir: ' + str(working_directory))
                pass
            else:
                raise
        if local_filename is None:
            print('using remote filename for local: ' + str(remote_filename))
            local_filename = remote_filename
        local_path = os.path.join(working_directory, local_filename)
        print('checking local path: ' + str(local_path))
    if local_path is not None and os.path.exists(local_path):
        print('existing local file: ' + str(local_path))
        return local_path
    print('calling downloader: %s %s %s' % (str(repository), str(remote_filename), str(local_path)))
    return download_file(repository, remote_filename, local_filename=local_path)
