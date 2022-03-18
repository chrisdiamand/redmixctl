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


PCM_CAPTURE: int
PCM_PLAYBACK: int

VOLUME_UNITS_PERCENTAGE: int
VOLUME_UNITS_RAW: int
VOLUME_UNITS_DB: int

class ALSAAudioError(Exception): ...


class Mixer():
    def __init__(self, control: str="Master", id: int=0, cardindex: int=-1, device: str="default"): ...
    def mixer(self) -> str: ...
    def switchcap(self) -> typing.List[str]: ...
    def volumecap(self) -> typing.List[str]: ...
    def getenum(self) -> typing.Tuple[str, typing.List[str]]: ...
    def getrange(self, pcmtype=PCM_PLAYBACK, units=VOLUME_UNITS_RAW) -> typing.Tuple[int, int]: ...
    def getvolume(self, pcmtype=PCM_PLAYBACK, units=VOLUME_UNITS_PERCENTAGE) -> typing.List[int]: ...
    def setenum(self, int): ...
    def setmute(self, mute: int): ...
    def setvolume(self, volume: int, channel: int=None, pcmtype=PCM_PLAYBACK, units=VOLUME_UNITS_PERCENTAGE): ...


def mixers(cardindex: int=-1, device: str="default") -> typing.List[str]: ...


def card_indexes() -> typing.List[int]: ...


def card_name(card_index: int) -> typing.Tuple[str, str]: ...
