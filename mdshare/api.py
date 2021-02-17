# This file is part of the markovmodel/mdshare project.
# Copyright (C) 2017-2019 Computational Molecular Biology Group,
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
import tarfile
from tempfile import mkdtemp
from .utils import LoadError, download_wrapper
from .repository import Repository
from . import default_repository


def load_repository(catalogue_file, checksum_file=None):
    """Load a repository catalogue from file

    Arguments:
        catalogue_file (str): filename of the catalogue
        checksum_file (str): filename of the catalogue's checksum
    """
    return Repository(catalogue_file, checksum_file)


def search(filename_pattern, repository=None):
    """Returns a list of available files matching a filename_pattern.

    Arguments:
        filename_pattern (str): filename pattern, allows for Unix shell-style wildcards
        repository (Repository): repository object
    """
    if repository is None:
        repository = default_repository
    if not isinstance(repository, Repository):
        raise TypeError('received {type(repository)} instead of Repository')
    return repository.search(filename_pattern)


def catalogue(repository=None):
    """Prints a human-friendly list of available files/sizes.

    Arguments:
        repository (Repository): repository object
    """
    if repository is None:
        repository = default_repository
    if not isinstance(repository, Repository):
        raise TypeError('received {type(repository)} instead of Repository')
    print(repository)


def fetch(
        remote_filename, working_directory='.', repository=None,
        max_attempts=3, force=False, show_progress=True):
    """Download a file if it is not already at the traget location.

    Arguments:
        remote_filename (str): name of the file in the repository
        working_directory (str): directory where the file should be saved
        repository (Repository): repository object
        max_attempts (int): number of download attempts
        force (boolean): enforce download even if file exists
        show_progress (boolean): show download progress
    """
    if repository is None:
        repository = default_repository
    if not isinstance(repository, Repository):
        raise TypeError('received {type(repository)} instead of Repository')
    if working_directory is None:
        working_directory = mkdtemp()
    else:
        os.makedirs(working_directory, exist_ok=True)
    try:
        import progress_reporter
        have_progress_reporter = True
    except ImportError:
        have_progress_reporter = False

    stack = repository.stack(remote_filename)
    if len(stack) == 0:
        raise LoadError(remote_filename, 'no match in repository')

    if have_progress_reporter and show_progress:
        callbacks = []
        pg = progress_reporter.ProgressReporter_()
        total = sum(item['size'] for item in stack)

        def update(n, blk, stage):
            downloaded = n * blk
            inc = max(
                0, downloaded - pg._prog_rep_progressbars[stage].n)
            pg.update(inc, stage=stage)
            # total progress
            try:
                pg.update(inc, stage=-1)
            except RuntimeError:
                pass

        from functools import partial
        tqdm_args = dict(unit='B', file=sys.stdout, unit_scale=True)

        n_progress_bars = 0
        for stage, item in enumerate(stack):
            if working_directory is not None:
                path = os.path.join(working_directory, item['file'])
                if os.path.exists(path) and not force:
                    callbacks.append(None)
                else:
                    pg.register(
                        item['size'],
                        description=f'downloading {item["file"]}',
                        tqdm_args=tqdm_args,
                        stage=stage)
                    callbacks.append(partial(update, stage=stage))
                    n_progress_bars += 1
        if n_progress_bars > 1:
            pg.register(
                total, description='total', tqdm_args=tqdm_args, stage=-1)
    else:
        from unittest.mock import MagicMock
        pg = MagicMock()
        callbacks = [None] * len(stack)

    result = []
    with pg.context():
        for item, progress in zip(stack, callbacks):
            file = download_wrapper(
                repository,
                item['file'],
                working_directory=working_directory,
                max_attempts=max_attempts,
                force=force,
                callback=progress)
            if item['unpack']:

                def inspect(members):
                    for member in members:
                        path, filename = os.path.split(member.name)
                        if path == '':
                            yield member, filename

                with tarfile.open(file, 'r:gz') as fh:
                    members = []
                    for member, filename in inspect(fh):
                        members.append(member)
                        result.append(
                            os.path.join(working_directory, filename))
                    fh.extractall(
                        path=working_directory, members=members)
                os.remove(file)
            else:
                result.append(file)

    if len(result) == 0:
        raise LoadError(remote_filename, 'this should not have happend!')
    elif len(result) == 1:
        return result[0]
    return result
