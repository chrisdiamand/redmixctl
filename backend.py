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


CHANNEL_SEPARATOR = " + "


class CardNotFoundError(Exception):
    pass


class StereoVolumeMixer:
    def __init__(self, mixer_elem_L: alsaaudio.Mixer, mixer_elem_R: alsaaudio.Mixer):
        self.L = mixer_elem_L
        self.R = mixer_elem_R

    def mixer(self) -> str:
        return CHANNEL_SEPARATOR.join([self.L.mixer(), self.R.mixer()])

    def getvolume(self) -> typing.List[int]:
        volume_L = self.L.getvolume()[0]
        volume_R = self.R.getvolume()[0]
        return [int((volume_L + volume_R) / 2)]

    def setvolume(self, volume: int):
        self.L.setvolume(volume)
        self.R.setvolume(volume)


class StereoEnumMixer:
    def __init__(self, mixer_elem_L: alsaaudio.Mixer, mixer_elem_R: alsaaudio.Mixer,
                 linked_sources: typing.List[typing.Tuple[str, str]]):
        self.L = mixer_elem_L
        self.R = mixer_elem_R

        current_L, choices_L = self.L.getenum()
        current_R, choices_R = self.R.getenum()
        assert choices_L == choices_R
        self.choices = choices_L

        assert "Off" in self.choices

        for (choice_L, choice_R) in linked_sources:
            logger.info("Remove %s from %s", choice_L, self.choices)
            self.choices.remove(choice_L)
            self.choices.remove(choice_R)
            self.choices.append(CHANNEL_SEPARATOR.join([choice_L, choice_R]))

    def mixer(self) -> str:
        return CHANNEL_SEPARATOR.join([self.L.mixer(), self.R.mixer()])

    def getenum(self) -> typing.Tuple[str, typing.List[str]]:
        current_L, choices_L = self.L.getenum()
        current_R, choices_R = self.R.getenum()

        if current_L == current_R and current_L in self.choices:
            return current_L, self.choices

        if current_L != current_R:
            stereo_choice_value = CHANNEL_SEPARATOR.join([current_L, current_R])
            if stereo_choice_value in self.choices:
                return (stereo_choice_value, self.choices)

            if current_L in self.choices:
                set_enum_value(self.R, "Off")
                return current_L, self.choices

            if current_R in self.choices:
                set_enum_value(self.L, "Off")
                return current_R, self.choices

        set_enum_value(self.L, "Off")
        set_enum_value(self.R, "Off")
        return "Off", self.choices

    def setenum(self, choice: int):
        choice_str = self.choices[choice]
        channels = choice_str.split(CHANNEL_SEPARATOR)
        if len(channels) == 1:
            set_enum_value(self.L, channels[0])
            set_enum_value(self.R, channels[0])
        elif len(channels) == 2:
            set_enum_value(self.L, channels[0])
            set_enum_value(self.R, channels[1])
        else:
            assert False, f"More than 2 channels in '{choice_str}'"


class Source:
    def __init__(self, interface, name: str):
        self.interface = interface
        self.name = name

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
    def __init__(self, interface, name_L, name_R,
                 input_volume_control_names_L, input_volume_control_names_R):

        assert len(input_volume_control_names_L) == len(input_volume_control_names_R)

        self.interface = interface
        self.name = CHANNEL_SEPARATOR.join([name_L, name_R])
        self.mixer_elems = []

        for i in range(0, len(input_volume_control_names_L)):
            input_volume_control_name_L = input_volume_control_names_L[i]
            input_volume_control_name_R = input_volume_control_names_R[i]
            mixer_elem_L = interface.mixer_elems[input_volume_control_name_L]
            mixer_elem_R = interface.mixer_elems[input_volume_control_name_R]
            self.mixer_elems.append(StereoVolumeMixer(mixer_elem_L, mixer_elem_R))


def get_mixer_elems(card_index: int) -> typing.Dict[str, alsaaudio.Mixer]:
    # Get the mixer element for each available mixer control
    mixer_elems: typing.Dict[str, alsaaudio.Mixer] = {}
    for mixer_elem_name in alsaaudio.mixers(cardindex=card_index):
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
        self.init_forced_values()

    def get_inputs(self):
        return self.sources

    def get_outputs(self):
        return self.outputs

    def get_mixes(self):
        return self.mixes

    def get_mixer_inputs(self):
        return self.mixer_inputs

    def get_global_settings(self):
        return [self.mixer_elems[i] for i in self.model.global_settings]

    def init_monitorable_sources(self):
        """Initialise objects representing the physical inputs and PCM outputs that
        can be included in the mix"""
        self.sources = []

        for name in self.model.physical_inputs:
            self.sources += [Source(self, name)]

        for name in self.model.pcm_outputs:
            self.sources += [Source(self, name)]

    def init_outputs(self):
        self.outputs = []

        mono_outputs = list(self.model.physical_outputs)
        for (output_L, output_R) in self.model.stereo_sinks:
            mono_outputs.remove(output_L)
            mono_outputs.remove(output_R)

        for name in mono_outputs:
            mixer_elem = self.mixer_elems[name]
            output = Output(self, name, mixer_elem)
            self.outputs += [output]

        for (output_L, output_R) in self.model.stereo_sinks:
            mixer_elem_L = self.mixer_elems[output_L]
            mixer_elem_R = self.mixer_elems[output_R]
            mixer_elem = StereoEnumMixer(mixer_elem_L, mixer_elem_R, self.model.stereo_sources)
            output = Output(self, CHANNEL_SEPARATOR.join([output_L, output_R]), mixer_elem)
            self.outputs += [output]

    def init_mixer_inputs(self):
        self.mixer_inputs: list[MixerInput] = []
        for name in self.model.mixer_inputs:
            mixer_elem: alsaaudio.Mixer = self.mixer_elems[name]
            mixer_input: MixerInput = MixerInput(self, name, mixer_elem)
            self.mixer_inputs.append(mixer_input)

    def init_mixes(self):
        self.mixes = []
        model_mixes = sorted(self.model.mixes)
        for i in range(0, len(model_mixes), 2):
            mix_name_L = model_mixes[i]
            mix_name_R = model_mixes[i + 1]
            input_volume_control_names_L = self.model.mixes[mix_name_L]
            input_volume_control_names_R = self.model.mixes[mix_name_R]
            self.mixes.append(Mix(self, mix_name_L, mix_name_R,
                                  input_volume_control_names_L,
                                  input_volume_control_names_R))

    def init_forced_values(self):
        for name in self.model.force_enum_values:
            mixer_elem = self.mixer_elems[name]
            set_enum_value(mixer_elem, self.model.force_enum_values[name])

        for name in self.model.force_volumes:
            mixer_elem = self.mixer_elems[name]
            volume = self.model.force_volumes[name]
            mixer_elem.setvolume(volume)
