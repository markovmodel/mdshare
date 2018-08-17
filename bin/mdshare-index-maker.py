#!/usr/bin/env python

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

from mdshare.utils import file_hash
from argparse import ArgumentParser
from yaml import load, dump
import fnmatch
import tarfile
import os

"""Build or test a catalogue; see mdshare/data/template for a build example"""


def filter_files(files, patterns):
    """Keep only those files which match at least on pattern"""
    include = set()
    for pattern in patterns:
        match = fnmatch.filter(files, pattern)
        include = include | set(match)
    return list(sorted(include))


def get_metadata(file):
    """Get a dict with file hash and size"""
    return dict(
        hash=file_hash(file),
        size=os.path.getsize(file))


def make_container(container, files):
    """Make a .tar.gz container from a list of files"""
    with tarfile.open(container, 'w:gz') as fh:
        for file in files:
            fh.add(file)


def build(template):
    """Build the catalogues from the given template"""
    for key in ('url', 'include', 'containers'):
        assert key in template, \
        'Cannot build without {} key'.format(key)

    db = dict(
        url=template['url'],
        index=dict(),
        containers=dict())

    files = filter_files(os.listdir(), template['include'])
    for file in files:
        db['index'].update({file: get_metadata(file)})

    for container, patterns in template['containers'].items():
        make_container(container, filter_files(files, patterns))
        db['containers'].update({container: get_metadata(container)})

    catalogue = '{}.yaml'.format(template['name'])
    with open(catalogue, 'w') as fh:
        fh.write(dump(db))

    checksum = '{}.md5'.format(template['name'])
    with open(checksum, 'w') as fh:
        fh.write(file_hash(catalogue))

    print('catalogue written to: {}'.format(catalogue))
    print('checksum written to:  {}'.format(checksum))


def test(catalogue):
    raise NotImplementedError()


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument(
        'mode',
        help='action to take [ build | test ]',
        metavar='MODE')
    parser.add_argument(
        'yaml',
        help='yaml file with catalogue or catalogue template',
        metavar='FILE')
    args = parser.parse_args()

    with open(args.yaml, 'r') as fh:
        yaml_file = load(fh)

    if args.mode.lower() == 'build':
        build(yaml_file)
    elif args.mode.lower() == 'test':
        test(yaml_file)
    else:
        raise ValueError('Unsupported mode: {}'.format(args.mode))
