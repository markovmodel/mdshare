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

from .. import fetch, load, catalogue, search
import os
import pytest
from urllib.error import HTTPError

def examine_test_file(path, offset=0):
    with open(path, 'r') as fh:
        assert fh.readline()[:-1] == 'This is a test file'
        assert int(fh.readline()[:-1]) == 1 + offset
        assert float(fh.readline()[:-1]) == 2.0 + offset
        assert float(fh.readline()) == 3.0 + offset
    os.remove(path)

def test_load_npz_file_local():
    examine_test_file(load('mdshare-test-00.txt'))

def test_load_npz_file_temp():
    examine_test_file(load(
        'mdshare-test-00.txt', working_directory=None))

def test_load_npz_file_local_newname():
    examine_test_file(load(
        'mdshare-test-00.txt', local_filename='testfile.txt'))

def test_load_npz_file_temp_newname():
    examine_test_file(load(
        'mdshare-test-00.txt',
        working_directory=None,
        local_filename='testfile.txt'))

def test_load_nonexistent_url():
    with pytest.raises(HTTPError):
        load('non-existent-file-on-the-ftp-server')

def test_fetch_npz_file_local():
    for offset in range(2):
        examine_test_file(
            fetch('mdshare-test-%02d.txt' % offset),
            offset=offset)

def test_fetch_npz_file_temp():
    files = fetch('mdshare-test-??.txt', working_directory=None)
    for offset, file in enumerate(files):
        examine_test_file(file, offset=offset)

def test_fetch_nonexistent_url():
    with pytest.raises(HTTPError):
        fetch('non-existent-file-on-the-ftp-server')

def test_catalogue():
    catalogue()

def test_search():
    assert 'mdshare-test-00.txt' in search('mdshare-test-??.txt')
    assert 'mdshare-test-00.txt' in search('mdshare*test*')
    assert 'mdshare-test-00.txt' in search('mdshare-test-00.???')
    assert 'mdshare-test-01.txt' not in search('mdshare-test-00.???')
    assert 'mdshare-test-0i.txt' not in search('mdshare-test-??.???')
