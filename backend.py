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
from pyalsa import alsacard, alsamixer
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
    card_numbers = alsacard.card_list()

    for num in card_numbers:
        longname = alsacard.card_get_longname(num)
        if longname.startswith("Focusrite Scarlett"):
            logger.info("Supported card %d: %s" % (num, longname))
            ret += [num]
        else:
            logger.info("Unsupported card %d: %s" % (num, longname))

    return ret


def find_card_number(cardname):
    card_numbers = get_supported_cards()
    print(card_numbers)
    ret = None

    if not card_numbers:
        logger.error("No supported cards found")
        return None

    if cardname:
        card_numbers = [num for num in card_numbers
                        if re.match(cardname, alsacard.card_get_name(num))]

        if not card_numbers:
            logger.error("No supported cards matching '%s' found" % cardname)
            return None

    if len(card_numbers) > 1:
        if cardname:
            logger.warn("Multiple supported cards matching '%s':" % cardname)
        else:
            logger.warn("Multiple supported cards:")
        for num in card_numbers:
            logger.warn("%d: %s (%s)" % (num, alsacard.card_get_num(num),
                                         alsacard.card_get_longname(num)))

    return card_numbers[0]


class Interface:
    def __init__(self, cardname=None):
        self.card_number = find_card_number(cardname)
        m = alsamixer.Mixer()
        print(m)
        m.attach("hw:%d" % self.card_number)
        m.load()
        print(m.list())

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

        self.outputs = [
            Output("Monitor"),
            Output("Headphone 1"),
            Output("Headphone 2"),
            Output("SPDIF"),
        ]

    def get_inputs(self):
        return self.inputs

    def get_outputs(self):
        return self.outputs
