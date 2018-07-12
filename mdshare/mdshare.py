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
import warnings
from urllib.request import urlretrieve, urlopen
from urllib.error import HTTPError
from humanfriendly import format_size
from fnmatch import fnmatch
from html.parser import HTMLParser
from collections import defaultdict
from functools import wraps


DEFAULT_REPOSITORY = 'http://ftp.imp.fu-berlin.de/pub/cmb-data/'


def download_file(repository, remote_filename, local_path=None, callback=None):
    """Download a file.

    Arguments:
        repository (str): URL of the remote source directory
        remote_filename (str): name of the file in the repository
        local_filename (str): local path where the file should be saved
    """
    filename, message = urlretrieve(
        repository + remote_filename,
        filename=local_path, reporthook=callback)
    return filename


def attempt_to_download_file(
        repository, remote_filename, local_path=None,
        max_attempts=3, delay=3, blur=0.1, callback=None):
    """Retry to download a file several times if necessary.

    Arguments:
        repository (str): URL of the remote source directory
        remote_filename (str): name of the file in the repository
        local_filename (str): local path where the file should be saved
        max_attempts (int): number of download attempts
        delay (int): delay between attempts in seconds
        blur (float): degree of blur to randomize the delay
    """
    attempt = 0
    while attempt < max_attempts:
        attempt += 1
        try:
            filename = download_file(
                repository, remote_filename, local_path=local_path, callback=callback)
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
        repository=DEFAULT_REPOSITORY,
        max_attempts=3, delay=3, blur=0.1, callbacks=None):
    """Download a file if necessary.

    Arguments:
        remote_filename (str): name of the file in the repository
        working_directory (str): directory where the file should be saved
        repository (str): URL of the remote source directory
        max_attempts (int): number of download attempts
        delay (int): delay between attempts in seconds
        blur (float): degree of blur to randomize the delay
    """
    if working_directory is None:
        local_path = None
    else:
        os.makedirs(working_directory, exist_ok=True)
        local_path = os.path.join(working_directory, remote_filename)
    if local_path is not None and os.path.exists(local_path):
        return local_path
    return attempt_to_download_file(
        repository, remote_filename, local_path=local_path,
        max_attempts=max_attempts, delay=delay, blur=blur, callback=callbacks)


def load(
        remote_filename, working_directory='.', local_filename=None,
        repository=DEFAULT_REPOSITORY,
        max_attempts=3, delay=3, blur=0.1):
    """Download a file if it is necessary (DEPRECATED).

    Arguments:
        remote_filename (str): name of the file in the repository
        working_directory (str): directory where the file should be saved
        local_filename (str): name under which the file should be saved
        repository (str): URL of the remote source directory
        max_attempts (int): number of download attempts
        delay (int): delay between attempts in seconds
        blur (float): degree of blur to randomize the delay
    """
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
        repository=DEFAULT_REPOSITORY,
        max_attempts=3, delay=3, blur=0.1, callbacks=None, show_progress=True):
    """Download one or more file(s) if necessary.

    Arguments:
        filename_pattern (str): name of the file(s) in the repository
        working_directory (str): directory where the file(s) should be saved
        repository (str): URL of the remote source directory
        max_attempts (int): number of download attempts
        delay (int): delay between attempts in seconds
        blur (float): degree of blur to randomize the delay
    """
    try:
        import progress_reporter
        from tqdm import tqdm
        have_progress_reporter = True
    except ImportError:
        have_progress_reporter = False
    files = search(filename_pattern, repository=repository, return_sizes=show_progress and have_progress_reporter)

    if len(files) == 0:
        url = '%s/%s' % (repository, filename_pattern)
        print('File not found: ' + url)
        raise HTTPError(url, 404, 'File(s) not found', None, None)

    if have_progress_reporter and show_progress:
        callbacks = []
        pg = progress_reporter.ProgressReporter()

        def update(n, blk, total, stage):
            downloaded = n * blk
            # print(downloaded, total)
            inc = max(0, downloaded - pg._prog_rep_progressbars[stage].n)
            pg._progress_update(inc, stage=stage)
        from functools import partial
        for i, (f, size) in enumerate(files):
            if working_directory is not None:
                path = os.path.join(working_directory, f)
                if os.path.exists(path):
                    callbacks.append(None)
                else:
                    pg._progress_register(size, description='downloading {}'.format(f),
                                          tqdm_args={'unit':'B'}, stage=i)
                    callbacks.append(partial(update, stage=i))
        files = [f for f, size in files]
    else:
        callbacks = [None] * len(files)

    result = [
        download_wrapper(
            remote_filename, working_directory=working_directory,
            repository=repository, max_attempts=max_attempts,
            delay=delay, blur=blur, callbacks=progress) for remote_filename, progress in zip(files, callbacks)]
    if len(result) == 1:
        return result[0]
    return result


def _cache(func):
    cache = {}
    @wraps(func)
    def f(url):
        if url in cache:
            result = cache[url]
        else:
            result = func(url)
            cache[url] = result
        return result
    return f


@_cache
def get_available_files_dict(repository):
    """Obtains a dictionary of available files/sizes.

    Arguments:
        repository (str): address of the FTP server
    """
    site = urlopen(repository)
    data = site.read()
    site.close()
    available_files = defaultdict(dict)
    class GetLinksParser(HTMLParser):
        def handle_starttag(self, tag, attrs):
            if tag == 'a' and len(attrs) >= 1 and attrs[0][0] =='href':
                fname = attrs[0][1]
                if not fname.startswith('?'):
                    available_files[fname].clear()
    p = GetLinksParser()
    p.feed(data.decode())
    invalid = []
    for file in available_files:
        f_url = repository + '/' + file
        try:
            site = urlopen(f_url)
            meta = site.info()
            site.close()
            s = int(meta .get("Content-Length"))
            available_files[file]['size'] = s
        except HTTPError:
            invalid.append(file)
    for f in invalid:
        available_files.pop(f)
    return available_files


def catalogue(repository=DEFAULT_REPOSITORY):
    """Prints a human-friendly list of available files/sizes.

    Arguments:
        repository (str): address of the FTP server
    """
    avail_files =  get_available_files_dict(repository)
    for key, value in sorted(avail_files.items()):
        print('%-060s %s' % (key, format_size(value['size'])))


def search(
        filename_pattern,
        repository=DEFAULT_REPOSITORY, return_sizes=False):
    """Returns a list of available files matching a filename_pattern.

    Arguments:
        filname_pattern (str): filename pattern, allows for Unix shell-style wildcards
        repository (str): address of the FTP server
    """
    avail_files = get_available_files_dict(repository)
    if return_sizes:
        return [(key, avail_files[key]['size']) for key in sorted(avail_files.keys())
                if fnmatch(key, filename_pattern)]
    return [key for key in sorted(avail_files.keys())
            if fnmatch(key, filename_pattern)]
