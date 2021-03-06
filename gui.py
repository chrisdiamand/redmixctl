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
import typing
import wx  # type: ignore

import backend
import version

logger = logging.getLogger(version.NAME + "." + __name__)


def table_dimensions(num_items, max_cols):
    # First, calculate the number of rows.
    num_rows = int(num_items / max_cols)
    # Add a row for the remainder if required
    if num_items % max_cols > 0:
        num_rows += 1

    # Then, find the number of colums that fits `num_items` items onto `rows`
    # rows with the smallest possible number of gaps in the last row.
    num_cols = int(num_items / num_rows)
    if num_items % num_rows > 0:
        num_cols += 1
    return (num_rows, num_cols)


def test_table_dimensions():
    assert table_dimensions(20, 4) == (5, 4)
    assert table_dimensions(18, 10) == (2, 9)
    assert table_dimensions(1, 1) == (1, 1)
    assert table_dimensions(5, 10) == (1, 5)
    assert table_dimensions(7, 8) == (1, 7)
    assert table_dimensions(8, 8) == (1, 8)
    assert table_dimensions(9, 8) == (2, 5)
    assert table_dimensions(25, 10) == (3, 9)


class EnumMixerElemChoice(wx.Choice):
    """wx.Choice which automatically displays and updates the value of an enum
    mixer element"""
    def __init__(self, parent, mixer_elem: alsaaudio.Mixer, on_change: typing.Callable[[], None] = None):
        self.name = mixer_elem.mixer()
        self.mixer_elem = mixer_elem
        self.extra_on_change = on_change
        _, choices = mixer_elem.getenum()

        wx.Choice.__init__(self, parent, choices=choices)
        self.Bind(wx.EVT_CHOICE, self.on_change)
        self.refresh_from_alsa()

    def refresh_from_alsa(self):
        current, _ = self.mixer_elem.getenum()
        index_of_current_value = self.FindString(current)
        self.SetSelection(index_of_current_value)

    def on_change(self, event):
        value = event.GetString()
        logger.debug("%s selection changed to %s", self.name, value)
        backend.set_enum_value(self.mixer_elem, value)

        if self.extra_on_change:
            self.extra_on_change()


class Fader(wx.Window):
    def __init__(self, parent, level_mixer_elem: backend.SupportsVolumeMixer):
        wx.Window.__init__(self, parent)

        self.level_mixer_elem = level_mixer_elem
        self.parent = parent

        sizer = wx.GridBagSizer()
        self.slider = wx.Slider(self, wx.ID_ANY, style=wx.SL_VERTICAL | wx.SL_INVERSE)
        self.Bind(wx.EVT_SLIDER, self.update, self.slider)
        # Devices use arbitrary ranges but pyalsaaudio converts them to
        # percentages for us.
        vmin, vmax = self.level_mixer_elem.getrange(units=alsaaudio.VOLUME_UNITS_DB)
        vminf = vmin / 100.0
        vmaxf = vmax / 100.0
        self.slider.SetRange(vminf, vmaxf)
        logger.debug(f"Range of {level_mixer_elem.mixer()} is {vminf} dB - {vmaxf} dB")

        sizer.Add(self.slider, (1, 1), span=(10, 1), flag=wx.EXPAND)

        self.refresh_from_alsa()

        self.SetSizerAndFit(sizer)
        self.Show(True)

    def refresh_from_alsa(self):
        vol = self.level_mixer_elem.getvolume(units=alsaaudio.VOLUME_UNITS_DB)[0]

        self.slider.SetValue(vol / 100.0)

    def update(self, event):
        vol = event.GetInt()
        logger.debug("%s changed to %d", self.level_mixer_elem.mixer(), event.GetInt())
        self.level_mixer_elem.setvolume(int(vol * 100.0), units=alsaaudio.VOLUME_UNITS_DB)


class MixerTab(wx.Window):
    def __init__(self, parent, iface: backend.Interface, mix: backend.Mix):
        wx.Window.__init__(self, parent)

        self.iface = iface
        self.mix = mix
        self.parent = parent

        assert len(mix.mixer_elems) == len(iface.get_mixer_inputs())

        # Don't have more than 10 faders in a row to avoid super long thin
        # windows going off the sides of the screen.
        _, num_cols = table_dimensions(len(self.mix.mixer_elems), 10)

        self.faders_sizer = wx.FlexGridSizer(num_cols)
        self.faders_sizer.SetFlexibleDirection(wx.VERTICAL)
        self.faders = []
        self.input_selectors = []
        i = 0
        while i < len(self.mix.mixer_elems):
            num_faders_on_row = min(num_cols, len(self.mix.mixer_elems) - i)
            for j in range(i, i + num_faders_on_row):
                level_mixer_elem = self.mix.mixer_elems[j]
                fader = Fader(self, level_mixer_elem)
                self.faders.append(fader)
                self.faders_sizer.Add(fader, flag=wx.ALIGN_CENTRE)

            for j in range(i, i + num_faders_on_row):
                input_select_mixer_elem: alsaaudio.Mixer = self.iface.get_mixer_inputs()[j].mixer_elem
                input_select = EnumMixerElemChoice(self, input_select_mixer_elem,
                                                   on_change=self.input_settings_changed)
                self.input_selectors.append(input_select)

                self.faders_sizer.Add(input_select, flag=wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, border=2)

            i += num_faders_on_row

        self.sizer = wx.BoxSizer()
        self.sizer.AddSpacer(10)
        self.sizer.Add(self.faders_sizer)
        self.sizer.AddSpacer(10)
        self.SetSizerAndFit(self.sizer)
        self.Show(True)

    def refresh_input_settings(self):
        """All mixes use the same mapping of physical inputs to mixer inputs.
        So when they are changed in one tab, this is called to update the
        selections in all other mix tabs.
        """
        for input_select in self.input_selectors:
            input_select.refresh_from_alsa()

    def input_settings_changed(self):
        mixertabs = self.parent
        mixertabs.refresh_input_settings()


class MixerTabs(wx.Notebook):
    def __init__(self, parent, iface):
        wx.Notebook.__init__(self, parent)

        self.mix_tabs = []
        for mix in iface.get_mixes():
            mix_tab = MixerTab(self, iface, mix)
            self.mix_tabs += [mix_tab]
            self.AddPage(mix_tab, mix.name)

    def refresh_input_settings(self):
        for mix_tab in self.mix_tabs:
            mix_tab.refresh_input_settings()


class OutputSettingsPanel(wx.Panel):
    def __init__(self, parent, app, iface):
        wx.Panel.__init__(self, parent)
        self.app = app
        self.iface = iface

        panel_sizer = wx.StaticBoxSizer(wx.VERTICAL, self, "Outputs")

        _, num_cols = table_dimensions(len(self.iface.get_outputs()), 4)

        # Double the columns - each row is a text label + choice box
        outputs_sizer = wx.GridSizer(num_cols * 2)

        self.outputs = []
        for output in self.iface.get_outputs():
            label = output.name.replace(backend.CHANNEL_SEPARATOR, "\n")
            outputs_sizer.Add(wx.StaticText(self, wx.ID_ANY, label=label), 50,
                              wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_RIGHT)

            mix_selector = EnumMixerElemChoice(self, output.mixer_elem)
            outputs_sizer.Add(mix_selector, 0, wx.ALIGN_CENTRE | wx.EXPAND | wx.ALL, border=2)

        panel_sizer.Add(outputs_sizer, flag=wx.ALL, border=5)

        self.SetSizerAndFit(panel_sizer)
        self.Show()


class GlobalSettingsPanel(wx.Panel):
    def __init__(self, parent, app, iface):
        wx.Panel.__init__(self, parent)
        self.app = app
        self.iface = iface

        panel_sizer = wx.StaticBoxSizer(wx.VERTICAL, self, "Global Settings")

        # TODO: Use the same number of rows as the output settings panel.
        settings_sizer = wx.GridSizer(2)

        for mixer_elem in self.iface.get_global_settings():
            settings_sizer.Add(wx.StaticText(self, wx.ID_ANY, label=mixer_elem.mixer()), 50,
                               wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_RIGHT)

            choice_box = EnumMixerElemChoice(self, mixer_elem)
            settings_sizer.Add(choice_box, 0, wx.ALIGN_CENTRE | wx.EXPAND | wx.ALL, border=2)

        panel_sizer.Add(settings_sizer, flag=wx.ALL, border=5)

        self.SetSizerAndFit(panel_sizer)
        self.Show()


class MainWindow(wx.Frame):
    def __init__(self, app, iface):
        wx.Frame.__init__(self, None, wx.ID_ANY, f"redmixctl - {iface.model.name}")

        self.tabs = MixerTabs(self, iface)
        self.output_settings = OutputSettingsPanel(self, app, iface)
        self.global_settings = GlobalSettingsPanel(self, app, iface)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.tabs, proportion=1, flag=wx.ALL, border=5)

        settings_sizer = wx.BoxSizer(wx.HORIZONTAL)
        settings_sizer.Add(self.output_settings, flag=wx.ALL, border=5)
        settings_sizer.Add(self.global_settings, flag=wx.TOP | wx.BOTTOM | wx.RIGHT, border=5)

        sizer.Add(settings_sizer, proportion=0, flag=wx.ALL)
        self.SetSizerAndFit(sizer)

        self.Show(True)


class MixerApp(wx.App):
    def __init__(self, iface):
        self.iface = iface

        wx.App.__init__(self)

    def OnInit(self):
        self.frame = MainWindow(self, self.iface)
        self.frame.Show(True)
        self.SetTopWindow(self.frame)

        return True
