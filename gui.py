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
    def __init__(self, parent, inpt):
        wx.Window.__init__(self, parent)

        self.inpt = inpt
        self.parent = parent

        sizer = wx.GridBagSizer()
        slider = wx.Slider(self, wx.ID_ANY, style=wx.SL_VERTICAL | wx.SL_INVERSE)
        sizer.Add(slider, (1, 1), span=(10, 3), flag=wx.EXPAND)

        label = wx.StaticText(self, wx.ID_ANY, label=inpt.name)
        sizer.Add(label, (12, 1))

        self.SetSizerAndFit(sizer)
        self.Show(True)


class MixerTab(wx.Window):
    def __init__(self, parent, iface, output):
        wx.Window.__init__(self, parent)

        self.iface = iface
        self.output = output
        self.parent = parent
        self.initialize()

    def initialize(self):
        sizer = wx.BoxSizer()

        pos = 3
        sizer.AddSpacer(10)
        for inpt in self.iface.get_inputs():
            fader = Fader(self, inpt)

            sizer.Add(fader)
            pos += 1
        sizer.AddSpacer(10)

        self.SetSizerAndFit(sizer)
        self.Show(True)


class MixerTabs(wx.Notebook):
    def __init__(self, parent, iface):
        wx.Notebook.__init__(self, parent)

        for output in iface.get_outputs():
            page = MixerTab(self, iface, output)
            self.AddPage(page, output.name)


class CommonSettingsPanel(wx.Panel):
    def __init__(self, parent, iface):
        wx.Panel.__init__(self, parent)
        self.Show()

        sizer = wx.BoxSizer(wx.VERTICAL)

        sizer.Add(wx.StaticText(self, label="Inputs to monitor"))

        choices = [source.name for source in iface.get_inputs()]
        monitorable_inputs = wx.CheckListBox(self, choices=choices)
        #self.monitorable_inputs = []
        #for source in iface.get_inputs():
        #    monitorable_input = wx.CheckBox(self, label=source.name)
        #    sizer.Add(monitorable_input)
        #    self.monitorable_inputs += [monitorable_input]

        sizer.Add(monitorable_inputs)
        self.SetSizerAndFit(sizer)


class MainWindow(wx.Frame):
    def __init__(self, iface):
        wx.Frame.__init__(self, None, wx.ID_ANY, "Scarlett Mixer")

        self.settings = CommonSettingsPanel(self, iface)
        self.tabs = MixerTabs(self, iface)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.settings)
        sizer.Add(self.tabs)
        self.SetSizerAndFit(sizer)

        self.Show(True)


class MixerApp(wx.App):
    def __init__(self, iface):
        self.iface = iface

        wx.App.__init__(self)

    def OnInit(self):
        frame = MainWindow(self.iface)
        frame.Show(True)
        self.SetTopWindow(frame)

        return True
