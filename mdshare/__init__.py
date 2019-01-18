#   This file is part of the markovmodel/mdshare project.
#   Copyright (C) 2017-2019 Computational Molecular Biology Group,
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


__author__ = 'Christoph Wehmeyer'
__email__ = 'christoph.wehmeyer@fu-berlin.de'
__credits__ = ['Guillermo Pérez-Hernández', 'Martin K. Scherer'],


from pkg_resources import get_distribution, DistributionNotFound
try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    __version__ = 'unknown'
del get_distribution, DistributionNotFound


from .repository import Repository
from os.path import dirname, join
from warnings import warn
try:
    default_repository = Repository(
        join(dirname(__file__), 'data', 'mdshare-catalogue.yaml'),
        join(dirname(__file__), 'data', 'mdshare-catalogue.md5'))
except FileNotFoundError:
    warn('Cannot build the default repository: missing file(s)!')
    default_repository = None
except RuntimeError as e:
    warn(f'Cannot build the default repository: {e.args[0]}')
    default_repository = None
del dirname, join, warn


from .api import load_repository, search, catalogue, fetch
from .utils import LoadError


def load(*args, **kwargs):
    raise NotImplementedError('use fetch')
