#!/usr/bin/env python3

# Copyright 2021 Chris Diamand
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import typing


from .model import Model
from . import Scarlett18i20gen2


MODELS: typing.List[Model] = [
    Scarlett18i20gen2.Scarlett18i20gen2
]


def all_canonical_names() -> typing.List[str]:
    return [m.canonical_name for m in MODELS]
