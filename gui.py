#!/usr/bin/env python2.7


from __future__ import print_function
import wx

import backend


class MixerTab(wx.Window):
    def __init__(self, parent, iface, output):
        wx.Window.__init__(self, parent)

        self.output = output
        self.parent = parent
        self.initialize()

    def initialize(self):
        sizer = wx.GridBagSizer()

        self.entry = wx.TextCtrl(self, -1, value=u"Enter text here.")
        sizer.Add(self.entry, (0, 0), (1, 1), wx.EXPAND)
        self.Bind(wx.EVT_TEXT_ENTER, self.OnPressEnter, self.entry)

        button = wx.Button(self, -1, label="Click me !")
        sizer.Add(button, (0, 1))
        self.Bind(wx.EVT_BUTTON, self.OnButtonClick, button)

        self.label = wx.StaticText(self, -1, label=u'Hello !')
        self.label.SetBackgroundColour(wx.BLUE)
        self.label.SetForegroundColour(wx.WHITE)
        sizer.Add(self.label, (1, 0), (1, 2), wx.EXPAND)

        self.slider = wx.Slider(self, -1, style=wx.SL_VERTICAL | wx.SL_INVERSE)
        sizer.Add(self.slider, (2, 2), span=(16, 1), flag=wx.EXPAND)

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
