#!/usr/bin/env python3
# PYTHON_ARGCOMPLETE_OK


# Functions to detect a mixer-compatible audio interface and match its
# available control elements (i.e. the controls shown by alsamixer) to a JSON
# schema.


try:
    import argcomplete
except ImportError:
    argcomplete = None

import alsaaudio
import argparse
import json
import logging
import re
import sys
import typing


logger = logging.getLogger("ScarlettMixer.redcard")


def is_volume_range(r):
    """Helper to ignore volume ranges from 0 to 0"""
    if r and type(r) == list and any(i for i in r):
        return True
    return False


def mixer_element_to_json(name: str, elem: alsaaudio.Mixer):
    if elem.mixer() != name:
        logger.warn("Mixer element has name '%s' but elem.mixer() returns '%s'",
                    name, elem.mixer())

    ret = dict()

    switchcap = elem.switchcap()
    if switchcap:
        ret["switchcap"] = switchcap

    volumecap = elem.volumecap()
    if volumecap:
        ret["volumecap"] = elem.volumecap()

    enum = elem.getenum()
    if enum:
        current_value, possible_values = enum
        ret["getenum"] = possible_values

    try:
        r = elem.getrange(alsaaudio.PCM_CAPTURE)
    except alsaaudio.ALSAAudioError:
        pass
    else:
        if is_volume_range(r):
            ret["getrange_capture"] = r

    try:
        r = elem.getrange(alsaaudio.PCM_PLAYBACK)
    except alsaaudio.ALSAAudioError:
        pass
    else:
        if is_volume_range(r):
            ret["getrange_playback"] = r

    return ret


def cmd_describe(args):
    """List the available control elements for a named interface and their
    potential values"""
    card_indexes: typing.List[int] = alsaaudio.card_indexes()

    m = re.match(r'hw:([0-9]+)', args.interface, re.IGNORECASE)

    if not m:
        logger.error("Invalid interface format: '%s'", args.interface)
        sys.exit(1)

    card_index: int = int(m.group(1))

    if card_index not in card_indexes:
        logger.error("No such card index: '%d' (available: %s)", index,
                      ", ".join([str(i) for i in card_indexes]))
        sys.exit(1)

    (name, longname) = alsaaudio.card_name(card_index)

    logger.info("Selected card %s: %s", args.interface, longname)

    mixer_elems = dict()
    for name in alsaaudio.mixers(cardindex=card_index):
        elem = alsaaudio.Mixer(control=name, cardindex=card_index)
        mixer_elems[name] = mixer_element_to_json(name, elem)

    json.dump(mixer_elems, sys.stdout, sort_keys=True, indent=4)


def get_card_indexes() -> typing.List[str]:
    return ["hw:" + str(i) for i in alsaaudio.card_indexes()]


def parse_args():
    ap = argparse.ArgumentParser()

    subparsers = ap.add_subparsers(dest="COMMAND")
    subparsers.required = True

    describe = subparsers.add_parser("describe")
    describe.add_argument("interface", type=str, choices=get_card_indexes())
    describe.set_defaults(func=cmd_describe)

    if argcomplete:
        argcomplete.autocomplete(ap)

    return ap.parse_args()


def main():
    logging.basicConfig(level=logging.INFO)
    args = parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
