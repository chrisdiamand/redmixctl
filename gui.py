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
    def __init__(self, parent, level_mixer_elem: alsaaudio.Mixer, input_select_mixer_elem: alsaaudio.Mixer):
        wx.Window.__init__(self, parent)

        self.level_mixer_elem = level_mixer_elem
        self.parent = parent

        sizer = wx.GridBagSizer()
        self.slider = wx.Slider(self, wx.ID_ANY, style=wx.SL_VERTICAL | wx.SL_INVERSE)
        self.Bind(wx.EVT_SLIDER, self.update, self.slider)
        # Devices use arbitrary ranges but pyalsaaudio converts them to
        # percentages for us.
        self.slider.SetRange(0, 100)

        sizer.Add(self.slider, (1, 1), span=(10, 1), flag=wx.EXPAND)

        self.input_select = EnumMixerElemChoice(self, input_select_mixer_elem,
                                                on_change=self.input_settings_changed)
        sizer.Add(self.input_select, (12, 1), flag=wx.ALIGN_CENTRE)

        self.refresh_from_alsa()

        self.SetSizerAndFit(sizer)
        self.Show(True)

    def refresh_from_alsa(self):
        vol = self.level_mixer_elem.getvolume()[0]

        self.slider.SetValue(vol)

    def update(self, event):
        vol = event.GetInt()
        logger.debug("%s changed to %d", self.level_mixer_elem.mixer(), event.GetInt())
        self.level_mixer_elem.setvolume(vol)

    def input_settings_changed(self):
        mixertab = self.parent
        mixertabs = mixertab.parent
        mixertabs.refresh_input_settings()


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

        self.faders_sizer = wx.GridSizer(num_cols)
        pos = 3
        self.faders = []
        for i in range(0, len(self.mix.mixer_elems)):
            level_mixer_elem = self.mix.mixer_elems[i]
            input_select_mixer_elem = self.iface.get_mixer_inputs()[i].mixer_elem
            fader = Fader(self, level_mixer_elem, input_select_mixer_elem)
            self.faders.append(fader)

            self.faders_sizer.Add(fader)
            pos += 1

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
        for fader in self.faders:
            fader.input_select.refresh_from_alsa()


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
            outputs_sizer.Add(wx.StaticText(self, wx.ID_ANY, label=output.name), 50,
                              wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_RIGHT)

            mix_selector = EnumMixerElemChoice(self, output.mixer_elem)
            outputs_sizer.Add(mix_selector, 0, wx.ALIGN_CENTRE)

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
            settings_sizer.Add(choice_box, 0, wx.ALIGN_CENTRE)

        panel_sizer.Add(settings_sizer, flag=wx.ALL, border=5)

        self.SetSizerAndFit(panel_sizer)
        self.Show()


class MainWindow(wx.Frame):
    def __init__(self, app, iface):
        wx.Frame.__init__(self, None, wx.ID_ANY, "redmixctl")

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
