#!/usr/bin/env python2.7

class Output:
    def __init__(self, name):
        self.name = name

class Interface:
    def __init__(self):
        pass

    def get_outputs(self):
        return [
            Output("Monitor"),
            Output("Headphone 1"),
            Output("Headphone 2"),
        ]
