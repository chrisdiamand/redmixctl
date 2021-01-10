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
import typing
import wx

import backend
import version

logger = logging.getLogger(version.NAME + "." + __name__)


class EnumMixerElemChoice(wx.Choice):
    """wx.Choice which automatically displays and updates the value of an enum
    mixer element"""
    def __init__(self, parent, mixer_elem: alsaaudio.Mixer, on_change: typing.Callable[[], None]=None):
        self.name = mixer_elem.mixer()
        self.mixer_elem = mixer_elem
        self.extra_on_change = on_change
        current, choices = mixer_elem.getenum()

        wx.Choice.__init__(self, parent, choices=choices)
        self.Bind(wx.EVT_CHOICE, self.on_change)
        index_of_current_value = self.FindString(current)
        self.SetSelection(index_of_current_value)

    def on_change(self, event):
        value = event.GetString()
        logger.debug("%s selection changed to %s", self.name, value)
        backend.set_enum_value(self.mixer_elem, value)

        if self.extra_on_change:
            self.extra_on_change()


class Fader(wx.Window):
    def __init__(self, parent, mixer_elem):
        wx.Window.__init__(self, parent)

        self.mixer_elem = mixer_elem
        self.parent = parent

        sizer = wx.GridBagSizer()
        slider = wx.Slider(self, wx.ID_ANY, style=wx.SL_VERTICAL | wx.SL_INVERSE)
        self.Bind(wx.EVT_SLIDER, self.update, slider)

        sizer.Add(slider, (1, 1), span=(10, 3), flag=wx.EXPAND)

        self.label = wx.StaticText(self, wx.ID_ANY, label=mixer_elem.mixer())
        sizer.Add(self.label, (12, 1))

        self.SetSizerAndFit(sizer)
        self.Show(True)

    def set_label(self, label):
        current_label = self.label.GetLabel()
        if current_label != label:
            logger.debug("Setting label for %s control from '%s' to '%s'",
                         self.mixer_elem.mixer(), current_label, label)
        self.label.SetLabel(label)
        self.label.Refresh()
        self.Refresh()

    def update(self, event):
        logger.info("%s [%s] changed to %d", self.label.GetLabel(), self.mixer_elem.mixer(), event.GetInt())


class MixerTab(wx.Window):
    def __init__(self, parent, iface: backend.Interface, mix: backend.Mix):
        wx.Window.__init__(self, parent)

        self.iface = iface
        self.mix = mix
        self.parent = parent

        assert len(mix.mixer_elems) == len(iface.get_mixer_inputs())

        self.initialize()
        self.update_fader_names()

    def initialize(self):
        self.sizer = wx.BoxSizer()

        pos = 3
        self.sizer.AddSpacer(10)
        self.faders = []
        for mixer_elem in self.mix.mixer_elems:
            fader = Fader(self, mixer_elem)
            self.faders.append(fader)

            self.sizer.Add(fader)
            pos += 1
        self.sizer.AddSpacer(10)

        self.SetSizerAndFit(self.sizer)
        self.Show(True)

    def update_fader_names(self):
        """This is called when the input sources are changed - we need to go
        through each fader and change the caption if it's now connected to
        something different.
        """
        for i in range(0, len(self.faders)):
            input_connection_mixer_elem = self.iface.get_mixer_inputs()[i]
            mixer_input_source = input_connection_mixer_elem.mixer_elem.getenum()[0]
            self.faders[i].set_label(mixer_input_source)

        self.Layout()
        self.Refresh()
        self.Update()


class MixerTabs(wx.Notebook):
    def __init__(self, parent, iface):
        wx.Notebook.__init__(self, parent)

        self.mix_tabs = []
        for mix in iface.get_mixes():
            mix_tab = MixerTab(self, iface, mix)
            self.mix_tabs += [mix_tab]
            self.AddPage(mix_tab, mix.name)


class InputSettingsPanel(wx.Panel):
    def __init__(self, parent, app, iface):
        wx.Panel.__init__(self, parent)
        self.app = app
        self.iface = iface

        panel_sizer = wx.StaticBoxSizer(wx.VERTICAL, self, "Mixer inputs")

        selection_sizer = wx.GridSizer(2)

        for mixer_input in self.iface.get_mixer_inputs():
            selection_sizer.Add(wx.StaticText(self, wx.ID_ANY, label=mixer_input.name), 50,
                                wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_CENTRE)
            selector = EnumMixerElemChoice(self, mixer_input.mixer_elem, on_change=self.input_settings_changed)
            selection_sizer.Add(selector, 0, wx.ALIGN_CENTRE)

        panel_sizer.Add(selection_sizer, flag=wx.ALL, border=5)

        self.SetSizerAndFit(panel_sizer)
        self.Show()

    def input_settings_changed(self):
        mix_tabs = self.app.frame.tabs.mix_tabs
        for mix_tab in mix_tabs:
            mix_tab.update_fader_names()
            mix_tab.Update()


class OutputSettingsPanel(wx.Panel):
    def __init__(self, parent, app, iface):
        wx.Panel.__init__(self, parent)
        self.app = app
        self.iface = iface

        panel_sizer = wx.StaticBoxSizer(wx.VERTICAL, self, "Outputs")

        outputs_sizer = wx.GridSizer(4)

        self.outputs = []
        for output in self.iface.get_outputs():
            outputs_sizer.Add(wx.StaticText(self, wx.ID_ANY, label=output.name), 50,
                              wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_RIGHT)
            mix_selector = EnumMixerElemChoice(self, output.mixer_elem)
            outputs_sizer.Add(mix_selector, 0, wx.ALIGN_CENTRE)

        panel_sizer.Add(outputs_sizer, flag=wx.ALL, border=5)

        self.SetSizerAndFit(panel_sizer)
        self.Show()


class MainWindow(wx.Frame):
    def __init__(self, app, iface):
        wx.Frame.__init__(self, None, wx.ID_ANY, "Scarlett Mixer")

        self.input_settings = InputSettingsPanel(self, app, iface)
        self.tabs = MixerTabs(self, iface)
        self.output_settings = OutputSettingsPanel(self, app, iface)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.input_settings, proportion=0, flag=wx.ALL, border=5)
        sizer.Add(self.tabs, proportion=1, flag=wx.ALL, border=5)
        sizer.Add(self.output_settings, proportion=0, flag=wx.ALL, border=5)
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
