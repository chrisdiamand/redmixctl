#!/usr/bin/env python2.7


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


class MixerTabs(wx.Frame):
    def __init__(self, parent, id, iface):
        wx.Frame.__init__(self, parent, id, "Scarlett Mixer")

        sizer = wx.BoxSizer()

        self.tabs = wx.Notebook(self)

        for output in iface.get_outputs():
            page = MixerTab(self.tabs, iface, output)
            self.tabs.AddPage(page, output.name)

        sizer.Add(self.tabs)
        self.SetSizerAndFit(sizer)

        self.Show(True)


class MixerApp(wx.App):
    def __init__(self, iface):
        self.iface = iface

        wx.App.__init__(self)

    def OnInit(self):
        frame = MixerTabs(None, wx.ID_ANY, self.iface)
        frame.Show(True)
        self.SetTopWindow(frame)

        return True
