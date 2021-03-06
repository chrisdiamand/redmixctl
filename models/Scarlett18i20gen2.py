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

from . import model

canonical_name = "18i20gen2"

name = "Scarlett 18i20 USB"

physical_inputs = [
    "Analogue 1",
    "Analogue 2",
    "Analogue 3",
    "Analogue 4",
    "Analogue 5",
    "Analogue 6",
    "Analogue 7",
    "Analogue 8",
    "S/PDIF 1",
    "S/PDIF 2",
    "ADAT 1",
    "ADAT 2",
    "ADAT 3",
    "ADAT 4",
    "ADAT 5",
    "ADAT 6",
    "ADAT 7",
    "ADAT 8"
]

physical_outputs = [
    "Analogue Output 01",
    "Analogue Output 02",
    "Analogue Output 03",
    "Analogue Output 04",
    "Analogue Output 05",
    "Analogue Output 06",
    "Analogue Output 07",
    "Analogue Output 08",
    "Analogue Output 09",
    "Analogue Output 10",
    "S/PDIF Output 1",
    "S/PDIF Output 2",
    "ADAT Output 1",
    "ADAT Output 2",
    "ADAT Output 3",
    "ADAT Output 4",
    "ADAT Output 5",
    "ADAT Output 6",
    "ADAT Output 7",
    "ADAT Output 8"
]

pcm_outputs = [
    "PCM 1",
    "PCM 2",
    "PCM 3",
    "PCM 4",
    "PCM 5",
    "PCM 6",
    "PCM 7",
    "PCM 8",
    "PCM 9",
    "PCM 10",
    "PCM 11",
    "PCM 12",
    "PCM 13",
    "PCM 14",
    "PCM 15",
    "PCM 16",
    "PCM 17",
    "PCM 18",
    "PCM 19",
    "PCM 20"
]

mixes = {
    "Mix A": [
        "Mix A Input 01",
        "Mix A Input 02",
        "Mix A Input 03",
        "Mix A Input 04",
        "Mix A Input 05",
        "Mix A Input 06",
        "Mix A Input 07",
        "Mix A Input 08",
        "Mix A Input 09",
        "Mix A Input 10",
        "Mix A Input 11",
        "Mix A Input 12",
        "Mix A Input 13",
        "Mix A Input 14",
        "Mix A Input 15",
        "Mix A Input 16",
        "Mix A Input 17",
        "Mix A Input 18"
    ],
    "Mix B": [
        "Mix B Input 01",
        "Mix B Input 02",
        "Mix B Input 03",
        "Mix B Input 04",
        "Mix B Input 05",
        "Mix B Input 06",
        "Mix B Input 07",
        "Mix B Input 08",
        "Mix B Input 09",
        "Mix B Input 10",
        "Mix B Input 11",
        "Mix B Input 12",
        "Mix B Input 13",
        "Mix B Input 14",
        "Mix B Input 15",
        "Mix B Input 16",
        "Mix B Input 17",
        "Mix B Input 18"
    ],
    "Mix C": [
        "Mix C Input 01",
        "Mix C Input 02",
        "Mix C Input 03",
        "Mix C Input 04",
        "Mix C Input 05",
        "Mix C Input 06",
        "Mix C Input 07",
        "Mix C Input 08",
        "Mix C Input 09",
        "Mix C Input 10",
        "Mix C Input 11",
        "Mix C Input 12",
        "Mix C Input 13",
        "Mix C Input 14",
        "Mix C Input 15",
        "Mix C Input 16",
        "Mix C Input 17",
        "Mix C Input 18"
    ],
    "Mix D": [
        "Mix D Input 01",
        "Mix D Input 02",
        "Mix D Input 03",
        "Mix D Input 04",
        "Mix D Input 05",
        "Mix D Input 06",
        "Mix D Input 07",
        "Mix D Input 08",
        "Mix D Input 09",
        "Mix D Input 10",
        "Mix D Input 11",
        "Mix D Input 12",
        "Mix D Input 13",
        "Mix D Input 14",
        "Mix D Input 15",
        "Mix D Input 16",
        "Mix D Input 17",
        "Mix D Input 18"
    ],
    "Mix E": [
        "Mix E Input 01",
        "Mix E Input 02",
        "Mix E Input 03",
        "Mix E Input 04",
        "Mix E Input 05",
        "Mix E Input 06",
        "Mix E Input 07",
        "Mix E Input 08",
        "Mix E Input 09",
        "Mix E Input 10",
        "Mix E Input 11",
        "Mix E Input 12",
        "Mix E Input 13",
        "Mix E Input 14",
        "Mix E Input 15",
        "Mix E Input 16",
        "Mix E Input 17",
        "Mix E Input 18"
    ],
    "Mix F": [
        "Mix F Input 01",
        "Mix F Input 02",
        "Mix F Input 03",
        "Mix F Input 04",
        "Mix F Input 05",
        "Mix F Input 06",
        "Mix F Input 07",
        "Mix F Input 08",
        "Mix F Input 09",
        "Mix F Input 10",
        "Mix F Input 11",
        "Mix F Input 12",
        "Mix F Input 13",
        "Mix F Input 14",
        "Mix F Input 15",
        "Mix F Input 16",
        "Mix F Input 17",
        "Mix F Input 18"
    ],
    "Mix G": [
        "Mix G Input 01",
        "Mix G Input 02",
        "Mix G Input 03",
        "Mix G Input 04",
        "Mix G Input 05",
        "Mix G Input 06",
        "Mix G Input 07",
        "Mix G Input 08",
        "Mix G Input 09",
        "Mix G Input 10",
        "Mix G Input 11",
        "Mix G Input 12",
        "Mix G Input 13",
        "Mix G Input 14",
        "Mix G Input 15",
        "Mix G Input 16",
        "Mix G Input 17",
        "Mix G Input 18"
    ],
    "Mix H": [
        "Mix H Input 01",
        "Mix H Input 02",
        "Mix H Input 03",
        "Mix H Input 04",
        "Mix H Input 05",
        "Mix H Input 06",
        "Mix H Input 07",
        "Mix H Input 08",
        "Mix H Input 09",
        "Mix H Input 10",
        "Mix H Input 11",
        "Mix H Input 12",
        "Mix H Input 13",
        "Mix H Input 14",
        "Mix H Input 15",
        "Mix H Input 16",
        "Mix H Input 17",
        "Mix H Input 18"
    ],
    "Mix I": [
        "Mix I Input 01",
        "Mix I Input 02",
        "Mix I Input 03",
        "Mix I Input 04",
        "Mix I Input 05",
        "Mix I Input 06",
        "Mix I Input 07",
        "Mix I Input 08",
        "Mix I Input 09",
        "Mix I Input 10",
        "Mix I Input 11",
        "Mix I Input 12",
        "Mix I Input 13",
        "Mix I Input 14",
        "Mix I Input 15",
        "Mix I Input 16",
        "Mix I Input 17",
        "Mix I Input 18"
    ],
    "Mix J": [
        "Mix J Input 01",
        "Mix J Input 02",
        "Mix J Input 03",
        "Mix J Input 04",
        "Mix J Input 05",
        "Mix J Input 06",
        "Mix J Input 07",
        "Mix J Input 08",
        "Mix J Input 09",
        "Mix J Input 10",
        "Mix J Input 11",
        "Mix J Input 12",
        "Mix J Input 13",
        "Mix J Input 14",
        "Mix J Input 15",
        "Mix J Input 16",
        "Mix J Input 17",
        "Mix J Input 18"
    ]
}

mixer_inputs = [
    "Mixer Input 01",
    "Mixer Input 02",
    "Mixer Input 03",
    "Mixer Input 04",
    "Mixer Input 05",
    "Mixer Input 06",
    "Mixer Input 07",
    "Mixer Input 08",
    "Mixer Input 09",
    "Mixer Input 10",
    "Mixer Input 11",
    "Mixer Input 12",
    "Mixer Input 13",
    "Mixer Input 14",
    "Mixer Input 15",
    "Mixer Input 16",
    "Mixer Input 17",
    "Mixer Input 18"
]

# On the 18i20, each physical output has a dedicated mixer control for its
# volume. For now, set most outputs to HW-controlled using force_enum_values,
# and only display faders for the headphone outputs.
force_enum_values = {
    "Line Out 01 Volume Control": "HW",
    "Line Out 02 Volume Control": "HW",
    "Line Out 03 Volume Control": "HW",
    "Line Out 04 Volume Control": "HW",
    "Line Out 05 Volume Control": "HW",
    "Line Out 06 Volume Control": "HW",
    "Line Out 07 Volume Control": "SW",
    "Line Out 08 Volume Control": "SW",
    "Line Out 09 Volume Control": "SW",
    "Line Out 10 Volume Control": "SW",

    # For physical inputs, ensure the PCM input sending the input audio back to
    # the PC corresponds to the correct input.
    "PCM 01": "Analogue 1",
    "PCM 02": "Analogue 2",
    "PCM 03": "Analogue 3",
    "PCM 04": "Analogue 4",
    "PCM 05": "Analogue 5",
    "PCM 06": "Analogue 6",
    "PCM 07": "Analogue 7",
    "PCM 08": "Analogue 8",
    "PCM 09": "S/PDIF 1",
    "PCM 10": "S/PDIF 2",
    "PCM 11": "ADAT 1",
    "PCM 12": "ADAT 2",
    "PCM 13": "ADAT 3",
    "PCM 14": "ADAT 4",
    "PCM 15": "ADAT 5",
    "PCM 16": "ADAT 6",
    "PCM 17": "ADAT 7",
    "PCM 18": "ADAT 8",
}

# Headphone levels can be controlled using the physical dial, so just force
# them to max volume instead of bothering with a GUI fader.
force_volumes = {
    "Line 07 (Headphones 1 L)": 100,
    "Line 08 (Headphones 1 R)": 100,
    "Line 09 (Headphones 2 L)": 100,
    "Line 10 (Headphones 2 R)": 100,
}

global_settings = [
    "Clock Source Clock Source",
]

stereo_sources = [(f"PCM {i}", f"PCM {i+1}") for i in range(1, 20, 2)] + [
    ("S/PDIF 1", "S/PDIF 2"),
]

stereo_sinks = [
    ("Analogue Output 01", "Analogue Output 02"),
    ("Analogue Output 03", "Analogue Output 04"),
    ("Analogue Output 05", "Analogue Output 06"),
    ("Analogue Output 07", "Analogue Output 08"),
    ("Analogue Output 09", "Analogue Output 10"),
    ("S/PDIF Output 1", "S/PDIF Output 2"),
]

Scarlett18i20gen2 = model.Model(
    canonical_name=canonical_name,
    name=name,
    physical_inputs=physical_inputs,
    physical_outputs=physical_outputs,
    pcm_outputs=pcm_outputs,
    mixes=mixes,
    mixer_inputs=mixer_inputs,
    force_enum_values=force_enum_values,
    force_volumes=force_volumes,
    global_settings=global_settings,
    stereo_sources=stereo_sources,
    stereo_sinks=stereo_sinks,
)
