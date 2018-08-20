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

from humanfriendly import format_size
from yaml import load
import warnings
import requests
import fnmatch
import logging
from .utils import LoadError, file_hash, url_join


class Category(dict):
    def __init__(self, data):
        super(Category, self).__init__(data)

    def search(self, pattern):
        return fnmatch.filter(self.keys(), pattern)

    def __str__(self):
        string = ''
        for key in sorted(self.keys()):
            size, unit = format_size(self[key]['size']).split(' ')
            string += '{:50s}   {:6.1f} {}\n'.format(
                key, float(size), unit)
        return string.rstrip('\n')


class Repository(object):
    def __init__(self, catalogue_file, checksum_file=None):
        if checksum_file is not None:
            with open(checksum_file, 'r') as fh:
                if file_hash(catalogue_file) != fh.read():
                    raise RuntimeError(
                        'Checksums do not match, check'
                        ' your catalogue files!')
        self.catalogue_file = catalogue_file
        with open(self.catalogue_file, 'r') as fh:
            data = load(fh)
        for key in ('url', 'index', 'containers'):
            if key not in data:
                raise RuntimeError(
                    'Cannot build repository catalogue without'
                    ' the {} key'.format(key))
        self.url = data['url']
        self.index = Category(data['index'])
        self.containers = Category(data['containers'])
        self._connection = None

    def lookup(self, key):
        if key in self.index:
            return 'index', self.index[key]
        elif key in self.containers:
            return 'containers', self.containers[key]
        raise LoadError(key, 'file not in repository catalogue')

    def size(self, key):
        location, data = self.lookup(key)
        return data['size']

    def hash(self, key):
        location, data = self.lookup(key)
        return data['hash']

    def search(self, pattern):
        index = set(self.index.search(pattern))
        containers = set(self.containers.search(pattern))
        return list(sorted(index | containers))

    def stack(self, pattern):
        stack = []
        for file in self.search(pattern):
            location, data = self.lookup(file)
            unpack = location == 'containers'
            stack.append(
                dict(file=file, size=data['size'], unpack=unpack))
        return stack

    def _get_connection(self):
        if self._connection is None:
            self._connection = requests.session()
        return self._connection

    def __str__(self):
        string = 'Repository: {}\n'.format(self.url)
        string += 'Files:\n' + str(self.index) + '\n'
        string += 'Containers:\n' + str(self.containers)
        return string
