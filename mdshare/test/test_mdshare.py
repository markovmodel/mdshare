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

from .. import load
import numpy as np
import os
import pytest
import urllib

def examine_test_file(path):
    with np.load(path) as fh:
        np.testing.assert_equal(
            fh['range_0_100_int16'],
            np.arange(0, 100).astype(np.int16))
        np.testing.assert_equal(
            fh['linspace_0_1_100_float32'],
            np.linspace(0, 1, 100).astype(np.float32).reshape(25, -1))
        os.remove(path)

def test_load_npz_file_local():
    examine_test_file(load('mdshare-test.npz'))

def test_load_npz_file_temp():
    examine_test_file(load(
        'mdshare-test.npz', working_directory=None))

def test_load_npz_file_local_newname():
    examine_test_file(load(
        'mdshare-test.npz', local_filename='testfile.npz'))

def test_load_npz_file_temp_newname():
    examine_test_file(load(
        'mdshare-test.npz',
        working_directory=None,
        local_filename='testfile.npz'))

def test_load_nonexistent_url():
    with pytest.raises(urllib.error.HTTPError):
        load('non-existent-file-on-the-ftp-server')
