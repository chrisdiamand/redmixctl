#!/usr/bin/env python2.7

class Input:
    def __init__(self, name):
        self.name = name

class Output:
    def __init__(self, name):
        self.name = name

class Interface:
    def __init__(self):
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
        ]

    def get_inputs(self):
        return self.inputs

    def get_outputs(self):
        return self.outputs
