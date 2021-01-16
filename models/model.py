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


import alsaaudio
import logging
import typing


logger = logging.getLogger("redmixctl." + __name__)


class Model:
    def __init__(self, *,
                 canonical_name: str,
                 name: str,
                 physical_inputs: typing.List[str],
                 pcm_inputs: typing.List[str],
                 physical_outputs: typing.List[str],
                 pcm_outputs: typing.List[str],
                 mixes: typing.Dict[str, typing.List[str]],
                 mixer_inputs: typing.List[str],
        ):

        assert canonical_name
        assert name

        # Each physical input should have a PCM input
        assert len(physical_inputs) == len(pcm_inputs)
        # ... and the same for outputs
        assert len(physical_outputs) == len(pcm_outputs)

        # Different models may have different numbers of mixes. There are
        # usually the same number of mixer inputs as physical inputs, but we
        # shouldn't assume that's the case; we need flexibility here anyway
        # to allow e.g. sacrificing monitoring of a physical input in favour of
        # a signal from the PC, e.g. a click track.

        self.canonical_name = canonical_name
        self.name = name
        self.physical_inputs = physical_inputs
        self.pcm_inputs = pcm_inputs
        self.physical_outputs = physical_outputs
        self.pcm_outputs = pcm_outputs
        self.mixes = mixes
        self.mixer_inputs = mixer_inputs

    def validate_mixer_elems(self, mixer_elems):
        """Verify that all the mixer elements specified in the model actually exist"""
        passed = True
        # Every sink (physical output or mixer input) should be an enum, and should
        # have every physical input, mix, and output PCM as a possible value.
        source_enum_values = set(["Off"] + self.physical_inputs +
                                 list(self.mixes.keys()) + self.pcm_outputs)
        for output in self.physical_outputs + self.mixer_inputs:
            if output not in mixer_elems:
                logger.info("Missing mixer element %s", output)
                return False

            elem = mixer_elems[output]
            current, enum_values = elem.getenum()
            if set(enum_values) != source_enum_values:
                logger.info("Source selections for output %s do not match expected values from model", output)
                logger.info("Expected: %s", ", ".join(sorted(source_enum_values)))
                logger.info("Got: %s", ", ".join(sorted(enum_values)))

        return passed
