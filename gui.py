#!/usr/bin/env python2.7

from __future__ import print_function

import wx


class MixerTab(wx.Window):
    def __init__(self, parent, name):
        wx.Window.__init__(self, parent)

        self.name = name
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
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title)
        self.parent = parent

        self.tabs = wx.Notebook(self)
        self.pages = [
            MixerTab(self.tabs, "Monitors"),
            MixerTab(self.tabs, "Headphone 1"),
            MixerTab(self.tabs, "Headphone 2"),
        ]
        for p in self.pages:
            self.tabs.AddPage(p, p.name)

        self.Show(True)


class MixerApp(wx.App):
    def OnInit(self):
        frame = MixerTabs(None, -1, "Scarlett Mixer")
        frame.Show(True)
        self.SetTopWindow(frame)

        return True


def main():
    app = MixerApp()
    app.MainLoop()


if __name__ == "__main__":
    main()
