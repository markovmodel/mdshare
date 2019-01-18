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

import string
import random
import pytest
import os
from .. import default_repository as REPO
from ..utils import LoadError
from ..utils import file_hash
from ..utils import url_join
from ..utils import download_file
from ..utils import attempt_to_download_file
from ..utils import download_wrapper


REPO_URL = REPO.url.rstrip('/')
FILE = 'mdshare-test-00.txt'
HASH = '5cbb04531c2e9fa7cc1e5d83195a2f81'


def local_file():
    file = ''.join([random.choice(string.ascii_letters)
                    for x in range(20)])
    return os.path.join('.', file)


def file_check(file):
    checksum = file_hash(file)
    os.remove(file)
    if checksum != HASH:
        raise AssertionError()


def test_file_hash():
    if file_hash('LICENSE') != 'bb3ca60759f3202f1ae42e3519cd06bc':
        raise AssertionError()


def test_file_hash_break():
    with pytest.raises(TypeError):
        file_hash(None)
    with pytest.raises(FileNotFoundError):
        file_hash('THIS IS NOT A FILE')


def test_url_join():
    url = f'{REPO_URL}/{FILE}'
    if url_join(REPO_URL, FILE) != url:
        raise AssertionError()
    if url_join(REPO_URL, FILE) != url:
        raise AssertionError()
    if url_join(REPO_URL,  f'/{FILE}') != url:
        raise AssertionError()
    if url_join(f'{REPO_URL}/',  f'/{FILE}') != url:
        raise AssertionError()
    if url_join(f'{REPO_URL}//', FILE) != url:
        raise AssertionError()
    if url_join(REPO_URL,  f'//{FILE}') != url:
        raise AssertionError()


def test_url_join_break():
    with pytest.raises(AttributeError):
        url_join(REPO_URL, None)
    with pytest.raises(AttributeError):
        url_join(None, FILE)
    with pytest.raises(AttributeError):
        url_join(REPO_URL, 1)
    with pytest.raises(AttributeError):
        url_join(1, FILE)


def test_download_file():
    file_check(download_file(REPO, FILE, local_file()))


def test_download_file_break():
    with pytest.raises(LoadError):
        download_file(REPO, None, local_file())
    with pytest.raises(LoadError):
        download_file(REPO, 'not-an-existing-file', local_file())
    with pytest.raises(AttributeError):
        download_file(None, FILE, local_file())
    with pytest.raises(AttributeError):
        download_file('not-a-repository', FILE, local_file())


def test_attempt_to_download_file():
    file_check(attempt_to_download_file(REPO, FILE, local_file()))
    file_check(
        attempt_to_download_file(
            REPO, FILE, local_file(), max_attempts=10))


def test_attempt_to_download_file_break():
    with pytest.raises(LoadError):
        attempt_to_download_file(REPO, None, local_file())
    with pytest.raises(AttributeError):
        attempt_to_download_file(None, FILE, local_file())
    with pytest.raises(IsADirectoryError):
        attempt_to_download_file(REPO, FILE, '.')
    with pytest.raises(LoadError):
        attempt_to_download_file(
            REPO, FILE, local_file(), max_attempts=0)
    with pytest.raises(LoadError):
        attempt_to_download_file(
            REPO, 'not-an-existing-file', local_file())


def test_download_wrapper():
    file_check(download_wrapper(REPO, FILE))
    file_check(download_wrapper(REPO, FILE, max_attempts=10))
    with open(FILE, 'w') as fh:
        fh.write('nonsense content')
    if file_hash(download_wrapper(REPO, FILE)) == HASH:
        raise AssertionError()
    file_check(download_wrapper(REPO, FILE, force=True))


def test_download_wrapper_break():
    with pytest.raises(TypeError):
        download_wrapper(REPO, None)
    with pytest.raises(LoadError):
        download_wrapper(REPO, 'not-an-existing-file')
    with pytest.raises(RuntimeError):
        download_wrapper(REPO, FILE, working_directory=None)
    with pytest.raises(AttributeError):
        download_wrapper(None, FILE)
    with pytest.raises(AttributeError):
        download_wrapper('not-a-repository', FILE)
    with pytest.raises(LoadError):
        download_wrapper(REPO, FILE, max_attempts=0)
