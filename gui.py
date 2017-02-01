#!/usr/bin/env python2.7


from __future__ import print_function
import wx

import backend


class MixerTab(wx.Window):
    def __init__(self, parent, iface, output):
        wx.Window.__init__(self, parent)

        self.iface = iface
        self.output = output
        self.parent = parent
        self.initialize()

    def initialize(self):
        sizer = wx.GridBagSizer()

        pos = 3
        for inpt in self.iface.get_inputs():
            slider = wx.Slider(self, wx.ID_ANY, style=wx.SL_VERTICAL | wx.SL_INVERSE)
            sizer.Add(slider, (1, pos), span=(10, 2), flag=wx.EXPAND)

            label = wx.StaticText(self, wx.ID_ANY, label=inpt.name)
            sizer.Add(label, (12, pos))

            pos += 3

        sizer.AddGrowableCol(0)
        self.SetSizerAndFit(sizer)
        self.SetSizeHints(-1, self.GetSize().y, -1, self.GetSize().y)
        self.Show(True)

    def OnButtonClick(self, event):
        self.label.SetLabel(self.entry.GetValue() +
                            " (You clicked the button)")

    def OnPressEnter(self, event):
        self.label.SetLabel(self.entry.GetValue() + " (You pressed ENTER)")


class MixerTabs(wx.Frame):
    def __init__(self, parent, id, iface):
        wx.Frame.__init__(self, parent, id, "Scarlett Mixer")

        self.tabs = wx.Notebook(self)

        for output in iface.get_outputs():
            page = MixerTab(self.tabs, iface, output)
            self.tabs.AddPage(page, output.name)

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
