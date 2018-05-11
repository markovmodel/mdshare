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
import warnings
from urllib.request import urlretrieve
from urllib.error import HTTPError
from ftplib import FTP
from humanfriendly import format_size
from fnmatch import fnmatch

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

def attempt_to_download_file(
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

def download_wrapper(
        remote_filename, working_directory='.',
        repository='http://ftp.imp.fu-berlin.de/pub/cmb-data/',
        max_attempts=3, delay=3, blur=0.1):
    '''Download a file if necessary.

    Arguments:
        remote_filename (str): name of the file in the repository
        working_directory (str): directory where the file should be saved
        repository (str): URL of the remote source directory
        max_attempts (int): number of download attempts
        delay (int): delay between attempts in seconds
        blur (float): degree of blur to randomize the delay
    '''
    if working_directory is None:
        local_path = None
    else:
        os.makedirs(working_directory, exist_ok=True)
        local_path = os.path.join(working_directory, remote_filename)
    if local_path is not None and os.path.exists(local_path):
        return local_path
    return attempt_to_download_file(
        repository, remote_filename, local_path=local_path,
        max_attempts=max_attempts, delay=delay, blur=blur)

def load(
        remote_filename, working_directory='.', local_filename=None,
        repository='http://ftp.imp.fu-berlin.de/pub/cmb-data/',
        max_attempts=3, delay=3, blur=0.1):
    '''Download a file if it is necessary (DEPRECATED).

    Arguments:
        remote_filename (str): name of the file in the repository
        working_directory (str): directory where the file should be saved
        local_filename (str): name under which the file should be saved
        repository (str): URL of the remote source directory
        max_attempts (int): number of download attempts
        delay (int): delay between attempts in seconds
        blur (float): degree of blur to randomize the delay
    '''
    warnings.warn(
        'load() is deprecated, use fetch() instead',
        DeprecationWarning,
        stacklevel=2)
    if working_directory is None:
        local_path = None
    else:
        os.makedirs(working_directory, exist_ok=True)
        if local_filename is None:
            local_filename = remote_filename
        local_path = os.path.join(working_directory, local_filename)
    if local_path is not None and os.path.exists(local_path):
        return local_path
    return attempt_to_download_file(
        repository, remote_filename, local_path=local_path,
        max_attempts=max_attempts, delay=delay, blur=blur)

def fetch(
        filename_pattern, working_directory='.',
        repository='http://ftp.imp.fu-berlin.de/pub/cmb-data/',
        max_attempts=3, delay=3, blur=0.1):
    '''Download one or more file(s) if necessary.

    Arguments:
        filename_pattern (str): name of the file(s) in the repository
        working_directory (str): directory where the file(s) should be saved
        repository (str): URL of the remote source directory
        max_attempts (int): number of download attempts
        delay (int): delay between attempts in seconds
        blur (float): degree of blur to randomize the delay
    '''
    files = search(filename_pattern, repository=repository)
    if len(files) == 0:
        url = '%s/%s' % (repository, filename_pattern)
        print('File not found: ' + url)
        raise HTTPError(url, 404, 'File(s) not found', None, None)
    result = [
        download_wrapper(
            remote_filename, working_directory=working_directory,
            repository=repository, max_attempts=max_attempts,
            delay=delay, blur=blur) for remote_filename in files]
    if len(result) == 1:
        return result[0]
    return result

def get_available_files_dict(repository):
    # Login to the FTP and get available files
    iftp = FTP(repository[0])
    iftp.login()
    # Go to subdirectories
    for idir in repository[1:]:
        iftp.cwd(idir)
    # Get the ls -l output
    available_files = {tup[0]:tup[1] for tup in iftp.mlsd()
                       if tup[0] not in ['.', '..']}
    iftp.close()
    return available_files

def catalogue(repository='http://ftp.imp.fu-berlin.de/pub/cmb-data/'):
    '''Prints a human-friendly list of availaible files/sizes.

    Arguments:
        repository (str): address of the FTP server
    '''
    avail_files =  get_available_files_dict(
        repository.lstrip('http://').split('/'))
    for key, value in sorted(avail_files.items()):
        print('%-060s %s' % (key, format_size(int(value['size']))))

def search(
        filename_pattern,
        repository='http://ftp.imp.fu-berlin.de/pub/cmb-data/'):
    '''Returns a list of available files matching a filename_pattern.

    Arguments:
        filname_pattern (str): filename pattern, allows for Unix shell-style wildcards
        repository (str): address of the FTP server
    '''
    avail_files =  get_available_files_dict(
        repository.lstrip('http://').split('/'))
    return [key for key in sorted(avail_files.keys())
            if fnmatch(key, filename_pattern)]
