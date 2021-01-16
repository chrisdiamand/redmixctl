#!/usr/bin/env python3

# Copyright 2017, 2021 Chris Diamand
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
import sys
import typing

import version
import models

logger = logging.getLogger(version.NAME + "." + __name__)


class CardNotFoundError(Exception):
    pass


class Source:
    def __init__(self, interface, name: str, pcm_input: str = None):
        self.interface = interface
        self.name = name

        # For physical inputs, ensure the PCM input sending the input audio back to
        # the PC corresponds to the correct input.
        if pcm_input:
            mixer_elem = interface.mixer_elems[pcm_input]
            set_enum_value(mixer_elem, name)

        # At init, try and detect if this input is already set as a mixer input
        self.mixer_input = None
        for mixer_input in self.interface.model.mixer_inputs:
            mixer_elem = self.interface.mixer_elems[mixer_input]
            current_value, _ = mixer_elem.getenum()
            if current_value == self.name:
                self.mixer_input = mixer_input


def set_enum_value(mixer_elem: alsaaudio.Mixer, enum_value):
    current, enum_values = mixer_elem.getenum()
    current_index = -1
    target_index = -1
    for index in range(0, len(enum_values)):
        if enum_values[index] == current:
            current_index = index
        if enum_values[index] == enum_value:
            target_index = index

    if target_index < 0 or target_index >= len(enum_values):
        logger.error("Couldn't set enum value for %s to '%s' (choices: %s)"
                     % (mixer_elem.mixer(), enum_value, str(enum_values)))
        return

    logger.debug("Setting %s from %s [%d] to %s [%d]" %
                 (mixer_elem.mixer(), current, current_index, enum_value, target_index))
    mixer_elem.setenum(target_index)


class Output:
    def __init__(self, interface, name, mixer_elem):
        self.interface = interface
        self.name = name
        self.mixer_elem = mixer_elem


class MixerInput:
    def __init__(self, interface, name, mixer_elem):
        self.interface = interface
        self.name = name
        self.mixer_elem = mixer_elem

    def get_value(self):
        return self.mixer_elem.getenum()[0]


class Mix:
    def __init__(self, interface, name, input_volume_control_names):
        self.interface = interface
        self.name = name
        self.mixer_elems = []
        for input_volume_control_name in input_volume_control_names:
            mixer_elem = interface.mixer_elems[input_volume_control_name]
            self.mixer_elems.append(mixer_elem)


def get_mixer_elems(card_index: int) -> typing.Dict[str, alsaaudio.Mixer]:
    # Get the mixer element for each available mixer control
    mixer_elems: typing.Dict[str, alsaaudio.Mixer] = {}
    for mixer_elem_name in alsaaudio.mixers(cardindex=card_index):
        logger.debug("Found mixer element '%s'" % mixer_elem_name)
        elem = alsaaudio.Mixer(control=mixer_elem_name, cardindex=card_index)
        assert mixer_elem_name not in mixer_elems
        mixer_elems[mixer_elem_name] = elem
    return mixer_elems


def find_card_index(model: models.Model) \
        -> typing.Tuple[int, typing.Dict[str, alsaaudio.Mixer]]:

    card_indexes = alsaaudio.card_indexes()

    for i in card_indexes:
        (name, _) = alsaaudio.card_name(i)
        if name == model.name:
            logger.debug("Card %d matches model name %s [%s]",
                         i, model.canonical_name, model.name)
            mixer_elems = get_mixer_elems(i)

            if model.validate_mixer_elems(mixer_elems):
                return i, mixer_elems
            else:
                logger.warning("Card %d [%s] does not match the %s model",
                               i, name, model.canonical_name)
                logger.warning("Are controls enabled in the kernel driver? " +
                               "You may need to run something like the following:")
                logger.warning("  echo 'options snd_usb_audio device_setup=1' " +
                               "| sudo tee /etc/modprobe.d/scarlett-internal-mixer.conf")

    raise CardNotFoundError()


class Interface:
    def __init__(self, card_index, mixer_elems, model):
        self.card_index = card_index
        self.mixer_elems = mixer_elems
        self.model = model

        self.init_monitorable_sources()
        self.init_outputs()
        self.init_mixer_inputs()
        self.init_mixes()

    def get_inputs(self):
        return self.sources

    def get_outputs(self):
        return self.outputs

    def get_mixes(self):
        return self.mixes

    def get_mixer_inputs(self):
        return self.mixer_inputs

    def init_monitorable_sources(self):
        """Initialise objects representing the physical inputs and PCM outputs that
        can be included in the mix"""
        self.sources = []

        assert len(self.model.physical_inputs) == len(self.model.pcm_inputs)
        for i in range(0, len(self.model.physical_inputs)):
            name = self.model.physical_inputs[i]
            pcm_input = self.model.pcm_inputs[i]
            self.sources += [Source(self, name, pcm_input=pcm_input)]

        for name in self.model.pcm_outputs:
            self.sources += [Source(self, name)]

    def init_outputs(self):
        self.outputs = []

        for name in self.model.physical_outputs:
            mixer_elem = self.mixer_elems[name]
            output = Output(self, name, mixer_elem)
            self.outputs += [output]

    def init_mixer_inputs(self):
        self.mixer_inputs: list[MixerInput] = []
        for name in self.model.mixer_inputs:
            mixer_elem: alsaaudio.Mixer = self.mixer_elems[name]
            mixer_input: MixerInput = MixerInput(self, name, mixer_elem)
            self.mixer_inputs.append(mixer_input)

    def init_mixes(self):
        self.mixes = []
        for mix_name in sorted(self.model.mixes):
            input_volume_control_names = self.model.mixes[mix_name]
            self.mixes.append(Mix(self, mix_name, input_volume_control_names))
