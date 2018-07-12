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
import sys
import warnings

from urllib.error import HTTPError
from humanfriendly import format_size
from fnmatch import fnmatch
from html.parser import HTMLParser
from collections import defaultdict
from functools import wraps


DEFAULT_REPOSITORY = 'http://ftp.imp.fu-berlin.de/pub/cmb-data/'
TIMEOUT = 15
_connection = None
_path = None


def _get_connection(repository):
    from  http.client import HTTPConnection
    global _connection, _path
    if _connection is None:
        import re
        matches = re.match('(https?://)([^:^/]*)(:\\d*)?(.*)?', repository)
        assert matches
        assert matches.group(1) == 'http://', 'only http implemented, but given was %s' % matches.group(0)
        server = matches.group(2)
        port = matches.group(3)
        _path = matches.group(4)
        _connection = HTTPConnection(server, port=80 if port is None else port, timeout=TIMEOUT)
    return _connection, _path


def _download_file(repository, remote_filename, local_path=None, callback=None):
    """Download a file.

    Arguments:
        repository (str): URL of the remote source directory
        remote_filename (str): name of the file in the repository
        local_filename (str): local path where the file should be saved
    """
    conn, path = _get_connection(repository)
    conn.request('GET', path + remote_filename)
    response = conn.getresponse()
    if response.code == 404:
        raise

    if local_path is None:
        import tempfile
        local_path = tempfile.mktemp()

    blocksize = 1024*8
    i = 0
    # TODO: check size and total read!
    with open(local_path, 'wb') as fh:
        while True:
            data = response.read(blocksize)
            if not data:
                break
            fh.write(data)
            if callback:
                callback(i, blocksize)
            i += 1

    return local_path


def _attempt_to_download_file(
        repository, remote_filename, local_path=None,
        max_attempts=3, callback=None):
    """Retry to download a file several times if necessary.

    Arguments:
        repository (str): URL of the remote source directory
        remote_filename (str): name of the file in the repository
        local_filename (str): local path where the file should be saved
        max_attempts (int): number of download attempts
    """
    attempt = 0
    filename = None
    def fault_handler(exception):
        print(exception)
        try:
            # remove faulty files
            os.unlink(filename)
        except:
            pass
        raise exception

    while attempt < max_attempts:
        attempt += 1
        try:
            filename = _download_file(
                repository, remote_filename, local_path=local_path, callback=callback)
            break
        except HTTPError as e:
            if e.code == 404:
                print('File not found: ' + e.url)
                raise
            else:
                print(e)
        except (IOError, KeyboardInterrupt) as e:
            fault_handler(e)
    if filename is None:
        raise RuntimeError('could not download file: {repo}{fn}'.format(repo=repository, fn=remote_filename))
    return filename


def _download_wrapper(
        remote_filename, working_directory='.',
        repository=DEFAULT_REPOSITORY,
        max_attempts=3, callbacks=None):
    """Download a file if necessary.

    Arguments:
        remote_filename (str): name of the file in the repository
        working_directory (str): directory where the file should be saved
        repository (str): URL of the remote source directory
        max_attempts (int): number of download attempts
    """
    if working_directory is None:
        local_path = None
    else:
        os.makedirs(working_directory, exist_ok=True)
        local_path = os.path.join(working_directory, remote_filename)
    if local_path is not None and os.path.exists(local_path):
        return local_path
    return _attempt_to_download_file(
        repository, remote_filename, local_path=local_path,
        max_attempts=max_attempts, callback=callbacks)


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
    return _attempt_to_download_file(
        repository, remote_filename, local_path=local_path,
        max_attempts=max_attempts)


def fetch(
        filename_pattern, working_directory='.',
        repository=DEFAULT_REPOSITORY,
        max_attempts=3, delay=3, blur=0.1, show_progress=True):
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
        pg = progress_reporter.ProgressReporter_()

        total = sum(x[1] for x in files)
        def update(n, blk, stage):
            downloaded = n * blk
            # print(downloaded, total)
            inc = max(0, downloaded - pg._prog_rep_progressbars[stage].n)
            pg.update(inc, stage=stage)
            # total progress
            pg.update(max(0, total - downloaded), stage=-1)
        from functools import partial
        tqdm_args = {'unit': 'B', 'file': sys.stdout, 'unit_scale': True}
        pg.register(total, description='total', tqdm_args=tqdm_args, stage=-1)
        for i, (f, size) in enumerate(files):
            if working_directory is not None:
                path = os.path.join(working_directory, f)
                if os.path.exists(path):
                    callbacks.append(None)
                else:
                    pg.register(size, description='downloading {}'.format(f),
                                tqdm_args=tqdm_args, stage=i)
                    callbacks.append(partial(update, stage=i))
        files = [f for f, size in files]
    else:
        from unittest.mock import MagicMock
        pg = MagicMock()
        callbacks = [None] * len(files)

    with pg.context():
        result = [
          _download_wrapper(
            remote_filename, working_directory=working_directory,
            repository=repository, max_attempts=max_attempts, callbacks=progress)
            for remote_filename, progress in zip(files, callbacks)]
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
def _get_available_files_dict(repository):
    """Obtains a dictionary of available files/sizes.

    Arguments:
        repository (str): address of the FTP server
    """
    conn, path = _get_connection(repository)
    conn.request('GET', path)
    response = conn.getresponse()
    data = response.read()
    response.close()
    available_files = defaultdict(dict)
    class GetLinksParser(HTMLParser):
        def handle_starttag(self, tag, attrs):
            if tag == 'a' and len(attrs) >= 1 and attrs[0][0] =='href':
                fname = attrs[0][1]
                if not fname.startswith('?'):
                    available_files[fname].clear()
    p = GetLinksParser()
    p.feed(data.decode())
    del data
    invalid = []
    import http
    from pprint import pprint
    t_total = 0
    for file in available_files:
        f_url = repository + '/' + file
        try:
            #site = urlopen(f_url)
            #meta = site.info()
            #site.close()

            #conn.set_debuglevel(10)
            hdrs = {'Host': 'ftp.imp.fu-berlin.de', 'User-Agent': 'Python-urllib/3.6', 'Connection': 'close'}
            import time
            start = time.time()
            conn.request('GET', path + '/' + file, headers=hdrs, encode_chunked=False)
            response = conn.getresponse()
            stop = time.time()
            d = stop - start
            t_total += d
            s = int(response.headers.get('Content-Length', 0))
            #pprint(headers)
            response.close()
            #if 'Content-Length' in headers:
            #    s = int(headers['Content-Length'])
            #else:
            #    s = 0
            #s = int(meta.get("Content-Length"))
            available_files[file]['size'] = s
        except HTTPError:
            invalid.append(file)
        except http.client.BadStatusLine:
            invalid.append(file)
    for f in invalid:
        available_files.pop(f)
    #pprint(available_files)
    print('t:', t_total)

    return available_files


def catalogue(repository=DEFAULT_REPOSITORY):
    """Prints a human-friendly list of available files/sizes.

    Arguments:
        repository (str): address of the FTP server
    """
    avail_files =  _get_available_files_dict(repository)
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
    avail_files = _get_available_files_dict(repository)
    if return_sizes:
        return [(key, avail_files[key]['size']) for key in sorted(avail_files.keys())
                if fnmatch(key, filename_pattern)]
    return [key for key in sorted(avail_files.keys())
            if fnmatch(key, filename_pattern)]
