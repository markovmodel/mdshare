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

import random
import string
import pytest
import os
from yaml import dump
from ..utils import LoadError
from ..utils import file_hash
from ..repository import Category
from ..repository import Repository


def randomizer(length, pattern=None):
    sample = ''.join([random.choice(string.ascii_letters)
                      for x in range(length)])
    if pattern is None:
        return sample
    return '{s}-{p}-{s}'.format(s=sample, p=pattern)


def make_random_category_dict(n, m):
    def metadata():
        return dict(
            size=random.randint(100, 100000),
            hash=randomizer(32))

    patterns = [randomizer(10) + str(i) for i in range(n)]
    files = []
    for pattern in patterns:
        files += [randomizer(10, pattern) + str(i) for i in range(m)]
    data = {file: metadata() for file in files}
    return patterns, files, data


class RandomCatalogue(object):
    def __init__(self, npattern, nentries, ncontainers, mode=0):
        _, _, index = make_random_category_dict(npattern, nentries)
        _, _, containers = make_random_category_dict(ncontainers, 1)
        self.data = dict(
            url='http://{}.{}/{}'.format(
                randomizer(10), randomizer(3), randomizer(7)),
            index=index,
            containers=containers)
        self.offset = ''
        if mode == 1:
            self.data.pop('url')
        elif mode == 2:
            self.data.pop('index')
        elif mode == 3:
            self.data.pop('containers')
        elif mode == 4:
            self.offset = randomizer(42)
        self.file = randomizer(25)

    def __enter__(self):
        with open(self.file + '.yaml', 'w') as fh:
            fh.write(dump(self.data))
        with open(self.file + '.md5', 'w') as fh:
            fh.write(file_hash(self.file + '.yaml') + self.offset)
        return (self.data, self.file)

    def __exit__(self, exception_type, exception_value, traceback):
        os.remove(self.file + '.yaml')
        os.remove(self.file + '.md5')


def test_category():
    n, m = random.randint(2, 6), random.randint(2, 6)
    patterns, files, data = make_random_category_dict(n, m)
    category = Category(data)
    assert len(category.keys()) == n * m
    for pattern in patterns:
        assert len(category.search('*-{}-*'.format(pattern))) == m
        assert len(category.search('*-{}-*'.format(pattern[1:-1]))) == 0
    string = str(category)
    for file in files:
        for key in ('hash', 'size'):
            assert category[file][key] == data[file][key]
        assert file in string


def test_repository():
    args = [random.randint(2, 7) for _ in range(3)]
    with RandomCatalogue(*args, mode=0) as (data, file):
        repository = Repository(file + '.yaml', file + '.md5')
    string = str(repository)
    assert repository.url == data['url']
    assert data['url'] in string
    for file in data['index']:
        assert file in string
        assert file in repository.index
        location, metadata = repository.lookup(file)
        assert location == 'index'
        assert metadata['size'] == data['index'][file]['size']
        assert metadata['hash'] == data['index'][file]['hash']
        assert repository.size(file) == data['index'][file]['size']
        assert repository.hash(file) == data['index'][file]['hash']
    for file in data['containers']:
        assert file in string
        assert file in repository.containers
        location, metadata = repository.lookup(file)
        assert location == 'containers'
        assert metadata['size'] == data['containers'][file]['size']
        assert metadata['hash'] == data['containers'][file]['hash']
        assert repository.size(file) == data['containers'][file]['size']
        assert repository.hash(file) == data['containers'][file]['hash']


def test_repository_break():
    for mode in range(4):
        with RandomCatalogue(4, 3, 2, mode=mode + 1) as (data, file):
            with pytest.raises(RuntimeError):
                Repository(file + '.yaml', file + '.md5')
    args = [random.randint(2, 7) for _ in range(3)]
    with RandomCatalogue(*args, mode=0) as (data, file):
        repository = Repository(file + '.yaml', file + '.md5')
    for location in ('index', 'containers'):
        for file in data[location]:
            with pytest.raises(LoadError):
                repository.lookup(file[1:-1])
    
