#!/usr/bin/env bash

SRC_DIR="$(dirname "${BASH_SOURCE[0]}")"/..

cd "${SRC_DIR}"

SRCS=(
    redmixctl
    backend.py
    gui.py
    models/*.py
    mixer_control_dumps/detect_controls.py
)

MYPYPATH=./stubs python3 -m mypy "${SRCS[@]}"
