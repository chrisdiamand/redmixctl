#!/usr/bin/env python2.7

# Copyright 2017 Chris Diamand
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


from __future__ import print_function
import alsaaudio
import logging
import re

import version

logger = logging.getLogger(version.NAME + "." + __name__)


class Input:
    def __init__(self, name):
        self.name = name


class Output:
    def __init__(self, name):
        self.name = name


def get_supported_cards():
    ret = list()
    card_indexes = alsaaudio.card_indexes()

    for num in card_indexes:
        (name, longname) = alsaaudio.card_name(num)
        if longname.startswith("Focusrite Scarlett"):
            logger.info("Supported card %d: %s" % (num, longname))
            ret += [num]
        else:
            logger.info("Unsupported card %d: %s" % (num, longname))

    return ret


def find_card_index(cardname):
    card_indexes = get_supported_cards()
    ret = None

    if not card_indexes:
        logger.error("No supported cards found")
        return None

    if cardname:
        card_indexes = [num for num in card_indexes
                        if re.match(cardname, alsaaudio.card_name(num)[0])]

        if not card_indexes:
            logger.error("No supported cards matching '%s' found" % cardname)
            return None

    if len(card_indexes) > 1:
        if cardname:
            logger.warn("Multiple supported cards matching '%s':" % cardname)
        else:
            logger.warn("Multiple supported cards:")
        for num in card_indexes:
            (name, longname) = alsaaudio.card_name(num)
            logger.warn("%d: %s (%s)" % (num, name, longname))

    return card_indexes[0]


class Interface:
    def __init__(self, cardname=None):
        self.card_index = find_card_index(cardname)
        self.get_mixer_elems()

        self.inputs = [
            Input("Analog 1"),
            Input("Analog 2"),
            Input("Analog 3"),
            Input("Analog 4"),
            Input("Analog 5"),
            Input("Analog 6"),
            Input("Analog 7"),
            Input("Analog 8"),
        ]

        self.outputs = self.find_outputs()

    def get_mixer_elems(self):
        self.mixer_elems = []
        for name in alsaaudio.mixers(cardindex=self.card_index):
            elem = alsaaudio.Mixer(control=name, cardindex=self.card_index)
            self.mixer_elems.append(elem)

    def get_inputs(self):
        return self.inputs

    def get_outputs(self):
        return self.outputs

    def find_outputs(self):
        ret = []
        prog = re.compile("Master ([0-9]+) \((.*)\)")
        for elem in self.mixer_elems:
            elem_name = elem.mixer()
            m = prog.match(elem_name)
            if not m:
                continue
            index = int(m.groups()[0])
            name = m.groups()[1]
            logger.info("Found output %d/%s, from '%s'" % (index, name, elem_name))
            output = Output(name)
            ret += [output]
        return ret
