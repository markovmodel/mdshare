# This file is part of the markovmodel/mdshare project.
# Copyright (C) 2017, 2018 Computational Molecular Biology Group,
# Freie Universitaet Berlin (GER)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import sys
import fnmatch
import logging
import warnings
from humanfriendly import format_size
from requests import HTTPError
from random import random
from hashlib import md5
from time import sleep
from yaml import load


class LoadError(KeyError):
    def __init__(self, file, message, *args, **kwargs):
        super(LoadError, self).__init__(*args, **kwargs)
        self.file = file
        self.message = message

    def __str__(self):
        return '{} [{}]'.format(self.file, self.message)


def file_hash(file, chunk_size=65536):
    """Compute the MD5 hash of a file.

    Arguments:
        file (str): path of the file to be hashed
        chunk_size (int): size of chunks to read
    """
    hash_ = md5()
    with open(file, 'rb') as fh:
        while True:
            data = fh.read(chunk_size)
            if not data:
                break
            hash_.update(data)
    return hash_.hexdigest()


def url_join(repository_url, file):
    """Compose a URL.

    Arguments:
        repository_url (str): url of the repository
        file (str): name of the file in the repository
    """
    return repository_url.rstrip('/') + '/' + file.lstrip('/')
    

def download_file(repository, file, local_path, callback=None):
    """Download a file.

    Arguments:
        repository (Repository): repository object
        file (str): name of the file in the repository
        local_filename (str): local path where the file should be saved
        callback (callable): callback function
    """
    location, metadata = repository.lookup(file)
    logging.debug(
        'Repository::{}::{} has checksum {} and size {}'.format(
            location, file, metadata['hash'], metadata['size']))
    logging.debug(
        'From <{}> download <{}> to <{}>'.format(
            repository.url, file, local_path))
    response = repository._get_connection().get(
        url_join(repository.url, file),
        stream=True)
    blocksize = 1024 * 8
    with open(local_path, 'wb') as fh:
        for i, data in enumerate(response.iter_content(blocksize)):
            fh.write(data)
            if callback is not None:
                callback(i, blocksize)
    checksum = file_hash(local_path)
    logging.debug(
        'Loaded file {} has {}'.format(
            local_path, checksum))
    if checksum != metadata['hash']:
        raise LoadError(file, 'checksum test failed')
    return local_path


def attempt_to_download_file(
        repository,
        file,
        local_path,
        max_attempts=3,
        callback=None):
    """Retry to download a file several times if necessary.

    Arguments:
        repository (Repository): repository object
        file (str): name of the file in the repository
        local_filename (str): local path where the file should be saved
        max_attempts (int): number of download attempts
        callback (callable): callback function
    """
    attempt = 0
    filename = None

    def fault_handler(filename, exception):
        print('error:', exception, file=sys.stderr)
        try:
            # remove faulty files
            os.unlink(filename)
        except:
            pass
        raise exception

    while attempt < max_attempts:
        attempt += 1
        logging.debug(
            'download attempt {}/{} ...'.format(attempt, max_attempts))
        try:
            filename = download_file(
                repository,
                file,
                local_path,
                callback=callback)
            break
        except (HTTPError, IOError, KeyboardInterrupt) as e:
            fault_handler(filename, e)
    if filename is None:
        raise LoadError(file, 'download failed')
    return filename


def download_wrapper(
        repository, file, working_directory='.',
        max_attempts=3, force=False, callback=None):
    """Download a file if necessary.

    Arguments:
        repository (Repository): repository object
        file (str): name of the file in the repository
        working_directory (str): directory where the file should be saved
        max_attempts (int): number of download attempts
        force (boolean): enforce download even if file exists
        callback (callable): callback function
    """
    logging.debug(
        'download_wrapper({}, {}, working_directory="{}",'
        ' max_attempts={}, force={})'.format(
            repository.url, file, working_directory,
            max_attempts, force))
    if working_directory is None:
        raise RuntimeError(
            'working_directory=None is illegal at this point')
    local_path = os.path.join(working_directory, file)
    logging.debug('local_path={}'.format(local_path))
    if os.path.exists(local_path) and not force:
        logging.debug(
            'local_path={} exists ... return'.format(local_path))
        return local_path
    logging.debug(
        'local_path={} does not exist ...'
        ' attempting download'.format(local_path))
    return attempt_to_download_file(
        repository,
        file,
        local_path,
        max_attempts=max_attempts,
        callback=callback)
