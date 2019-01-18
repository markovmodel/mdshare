#!/usr/bin/env python

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

from mdshare import fetch, Repository
from mdshare.utils import file_hash
from argparse import ArgumentParser
from yaml import load, dump
import fnmatch
import tarfile
import os


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


def build(template_file):
    """Build the catalogues from the given template"""
    with open(template_file, 'r') as fh:
        template = load(fh)

    for key in ('url', 'include', 'containers'):
        if key not in template:
            raise RuntimeError(f'Cannot build without {key} key')

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

    catalogue = f'{template["name"]}.yaml'
    with open(catalogue, 'w') as fh:
        fh.write(dump(db))

    checksum = f'{template["name"]}.md5'
    with open(checksum, 'w') as fh:
        fh.write(file_hash(catalogue))

    print(f'catalogue written to: {catalogue}')
    print(f'checksum written to:  {checksum}')


def test(catalogue_file, checksum_file):
    repository = Repository(catalogue_file, checksum_file)
    working_directory = 'mdshare-testing-area'
    os.mkdir(working_directory)
    for file in repository.index:
        local_file = fetch(
            file,
            working_directory=working_directory,
            repository=repository)
        os.remove(local_file)
    for file in repository.containers:
        local_files = fetch(
            file,
            working_directory=working_directory,
            repository=repository)
        try:
            os.remove(local_files)
        except TypeError:
            for local_file in local_files:
                os.remove(local_file)
    os.rmdir(working_directory)


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
    parser.add_argument(
        'md5',
        help='md5 checksum file of the catalogue',
        metavar='FILE',
        nargs='?')
    args = parser.parse_args()

    if args.mode.lower() == 'build':
        build(args.yaml)
    elif args.mode.lower() == 'test':
        test(args.yaml, args.md5)
    else:
        raise ValueError(f'Unsupported mode: {args.mode}')
