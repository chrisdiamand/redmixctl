#!/usr/bin/env python3
# PYTHON_ARGCOMPLETE_OK


try:
    import argcomplete  # type: ignore
except ImportError:
    argcomplete = None

import alsaaudio
import argparse
import json
import logging
import re
import sys
import typing


logger = logging.getLogger("dump_mixer_controls")


def is_volume_range(r):
    """Helper to ignore volume ranges from 0 to 0"""
    if r and type(r) == list and any(i for i in r):
        return True
    return False


def mixer_element_to_json(name: str, elem: alsaaudio.Mixer):
    if elem.mixer() != name:
        logger.warn("Mixer element has name '%s' but elem.mixer() returns '%s'",
                    name, elem.mixer())

    ret: typing.Dict[str, typing.Any] = dict()

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


def get_card_indexes() -> typing.List[str]:
    return ["hw:" + str(i) for i in alsaaudio.card_indexes()]


def parse_args():
    desc = ("Detect all available mixer control elements and dump as JSON. This "
            "helps to support and test different hardware without requiring it "
            "to be physically present")
    ap = argparse.ArgumentParser(description=desc)

    ap.add_argument("interface", type=str, choices=get_card_indexes())
    ap.add_argument("--output", "-o", type=argparse.FileType("wt"))

    if argcomplete:
        argcomplete.autocomplete(ap)

    args = ap.parse_args()

    if not args.output:
        args.output = sys.stdout

    return args


def main():
    """List the available control elements and their potential values"""

    logging.basicConfig(level=logging.INFO)
    args = parse_args()
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

    json.dump(mixer_elems, args.output, sort_keys=True, indent=4)


if __name__ == "__main__":
    main()
