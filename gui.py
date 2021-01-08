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
import logging
import wx

import backend
import version

logger = logging.getLogger(version.NAME + "." + __name__)


class Fader(wx.Window):
    def __init__(self, parent, source):
        wx.Window.__init__(self, parent)

        self.source = source
        self.parent = parent

        sizer = wx.GridBagSizer()
        slider = wx.Slider(self, wx.ID_ANY, style=wx.SL_VERTICAL | wx.SL_INVERSE)
        self.Bind(wx.EVT_SLIDER, self.update, slider)

        sizer.Add(slider, (1, 1), span=(10, 3), flag=wx.EXPAND)

        label = wx.StaticText(self, wx.ID_ANY, label=source.name)
        sizer.Add(label, (12, 1))

        self.SetSizerAndFit(sizer)
        self.Hide()

    def update(self, event):
        logger.info("%s changed to %d", self.source.name, event.GetInt())


class MixerTab(wx.Window):
    def __init__(self, parent, iface, output):
        wx.Window.__init__(self, parent)

        self.iface = iface
        self.output = output
        self.parent = parent
        self.initialize()
        self.update()

    def initialize(self):
        self.sizer = wx.BoxSizer()

        pos = 3
        self.sizer.AddSpacer(10)
        self.faders = []
        for source in self.iface.get_inputs():
            fader = Fader(self, source)
            self.faders.append(fader)

            self.sizer.Add(fader)
            pos += 1
        self.sizer.AddSpacer(10)

        self.SetSizerAndFit(self.sizer)
        self.Show(True)

    def update(self):
        for fader in self.faders:
            if fader.source.is_monitored():
                fader.Show()
            else:
                fader.Hide()
        self.Fit()


class MixerTabs(wx.Notebook):
    def __init__(self, parent, iface):
        wx.Notebook.__init__(self, parent)

        self.mix_tabs = []
        for mix_name in iface.model.mixes:
            mix_tab = MixerTab(self, iface, mix_name)
            self.mix_tabs += [mix_tab]
            self.AddPage(mix_tab, mix_name)


class InputSettingsPanel(wx.Panel):
    def __init__(self, parent, app, iface):
        wx.Panel.__init__(self, parent)
        self.app = app
        self.iface = iface

        sizer = wx.StaticBoxSizer(wx.VERTICAL, self, "Inputs to monitor")

        choices = []
        enabled_sources = []
        for source in iface.get_inputs():
            choices += [source.name]
            if source.is_monitored():
                enabled_sources += [source.name]

        self.monitorable_inputs = wx.CheckListBox(self, choices=choices)
        self.monitorable_inputs.SetCheckedStrings(enabled_sources)
        self.Bind(wx.EVT_CHECKLISTBOX, self.monitorable_inputs_changed, self.monitorable_inputs)

        sizer.Add(self.monitorable_inputs, flag=wx.ALL | wx.EXPAND, border=5)
        self.SetSizerAndFit(sizer)

        self.Show()

    def monitorable_inputs_changed(self, event):
        name = event.GetString()
        index = event.GetInt()
        enabled = self.monitorable_inputs.IsChecked(index)
        if enabled:
            logger.info("%s enabled", name)
        else:
            logger.info("%s disabled", name)

        source = self.iface.get_inputs()[index]
        if enabled:
            source.add_to_monitored_inputs()
        else:
            source.remove_from_monitored_inputs()

        mix_tabs = self.app.frame.tabs.mix_tabs
        for mix_tab in mix_tabs:
            mix_tab.update()


class OutputSettingsPanel(wx.Panel):
    def __init__(self, parent, app, iface):
        wx.Panel.__init__(self, parent)
        self.app = app
        self.iface = iface

        panel_sizer = wx.StaticBoxSizer(wx.VERTICAL, self, "Outputs")
        #panel_sizer.Add(wx.StaticText(self, label="Outputs"))

        outputs_sizer = wx.GridSizer(4)

        self.outputs = []
        for output in self.iface.get_outputs():
            outputs_sizer.Add(wx.StaticText(self, wx.ID_ANY, label=output.name), 50,
            wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_RIGHT)
            mix_selector = wx.Choice(self, choices=self.iface.model.mixes + ["Off"])
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
