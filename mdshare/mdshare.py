#   This file is part of the markovmodel/mdshare project.
#   Copyright (C) 2017, 2018 Computational Molecular Biology Group,
#   Freie Universitaet Berlin (GER)
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Lesser General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU Lesser General Public License
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
        filename=local_path)
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
        except HTTPError as e:
            if e.code == 404:
                print('File not found: ' + e.url)
                raise
            else:
                print(e)
        except IOError as e:
            print(e)
        try:
            return filename
        except UnboundLocalError:
            pass
    raise RuntimeError(
        'could not download file: ' + str(repository + remote_filename))

def load(
    remote_filename, working_directory='.', local_filename=None,
    repository='http://ftp.imp.fu-berlin.de/pub/cmb-data/',
    max_attempts=3, delay=3, blur=0.1):
    '''Download a file if it is necessary.

    Arguments:
        remote_filename (str): name of the file in the repository
        working_directory (str): directory where the file should be saved
        local_filename (str): name under which the file should be saved
        repository (str): URL of the remote source directory
        max_attempts (int): number of download attempts
        delay (int): delay between attempts in seconds
        blur (float): degree of blur to randomize the delay
    '''
    if working_directory is None:
        local_path = None
    else:
        os.makedirs(working_directory, exist_ok=True)
        if local_filename is None:
            local_filename = remote_filename
        local_path = os.path.join(working_directory, local_filename)
    if local_path is not None and os.path.exists(local_path):
        return local_path
    return attempted_download(
        repository, remote_filename, local_path=local_path,
        max_attempts=max_attempts, delay=delay, blur=blur)
