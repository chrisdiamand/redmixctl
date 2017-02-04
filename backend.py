#!/usr/bin/env python2.7


from __future__ import print_function
from pyalsa import alsacard, alsamixer


class Input:
    def __init__(self, name):
        self.name = name


class Output:
    def __init__(self, name):
        self.name = name


def find_card_number(cardname):
    card_numbers = alsacard.card_list()
    print(card_numbers)
    ret = None
    for num in card_numbers:
        name = alsacard.card_get_name(num)
        longname = alsacard.card_get_longname(num)
        print(name, longname)

        if cardname and name == cardname:
            if not ret:
                ret = num
            else:
                print("Warning: Multiple interfaces matching '%s'" % cardname)
        elif not cardname:
            if longname.startswith("Focusrite Scarlett"):
                if not ret:
                    ret = num
                else:
                    print("Warning: Multiple scarlett interfaces found (at least %d:'%s' and %d:'%s')" % \
                            (ret, alsacard.card_get_name(ret), num, alsacard.card_get_name(num)))

    return ret


class Interface:
    def __init__(self, cardname=None):
        self.card_number = find_card_number(cardname)
        m = alsamixer.Mixer()
        print(m)
        m.attach("hw:%d" % self.card_number)
        m.load()
        print(m.list())

        self.inputs = [
            Input("Analog 1"),
            Input("Analog 2"),
            Input("Analog 3"),
            Input("Analog 4"),
            Input("Analog 5"),
            Input("Analog 6"),
            Input("Analog 7"),
            Input("Analog 8"),
        ]

        self.outputs = [
            Output("Monitor"),
            Output("Headphone 1"),
            Output("Headphone 2"),
            Output("SPDIF"),
        ]

    def get_inputs(self):
        return self.inputs

    def get_outputs(self):
        return self.outputs
