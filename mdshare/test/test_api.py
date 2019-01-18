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

import pytest
import os
from ..utils import LoadError
from ..utils import file_hash
from ..api import load_repository
from ..api import search
from ..api import catalogue
from ..api import fetch
from .. import default_repository

FILE = 'mdshare-test-00.txt'
HASH = '5cbb04531c2e9fa7cc1e5d83195a2f81'


def file_check(file):
    if file_hash(file) != HASH:
        raise AssertionError()
    os.remove(file)


def test_load_repository_break():
    with pytest.raises(TypeError):
        load_repository(None)
    with pytest.raises(FileNotFoundError):
        load_repository('not-a-repository')


def test_search():
    if len(search(FILE)) != 1:
        raise AssertionError()
    if search(FILE)[0] != FILE:
        raise AssertionError()
    if len(search(FILE[1:-1])) != 0:
        raise AssertionError()


def test_search_break():
    with pytest.raises(TypeError):
        search(FILE, 'not-a-repository')
    with pytest.raises(TypeError):
        search(None)


def test_catalogue(capsys):
    catalogue()
    captured = capsys.readouterr()
    if captured.out != f'{str(default_repository)}\n':
        raise AssertionError()


def test_catalogue_break():
    with pytest.raises(TypeError):
        catalogue('not-a-repository')


def test_fetch():
    file_check(fetch(FILE))
    file_check(fetch(f'*{FILE[1:-1]}*'))
    file_check(fetch(FILE, repository=default_repository))


def test_fetch_break():
    file = fetch(FILE)
    with pytest.raises(FileExistsError):
        fetch(FILE, working_directory=file)
    os.remove(file)
    with pytest.raises(TypeError):
        fetch(None)
    with pytest.raises(LoadError):
        fetch('not-an-existing-file-or-pattern')
    with pytest.raises(TypeError):
        fetch(FILE, repository='not-a-repository')
