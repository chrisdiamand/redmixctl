#!/usr/bin/env bash

SRC_DIR="$(dirname "${BASH_SOURCE[0]}")"/..

STATUS=0

cd "${SRC_DIR}"

SRCS=(
    redmixctl
    backend.py
    gui.py
    models/*.py
    mixer_control_dumps/detect_controls.py
)

function hrule() {
    echo "----------------------------"
}

function run_cmd() {
    hrule
    echo "$ $@"
    "$@"
    return $?
}

function check_result() {
    local cmd="$1" exit_status="$2"
    if [[ exit_status -eq 0 ]]; then
        echo "$cmd passed"
    else
        echo "$cmd failed with exit status $exit_status"
        STATUS=1
    fi
}

run_cmd env MYPYPATH=./stubs python3 -m mypy "${SRCS[@]}"
check_result "mypy" $?

run_cmd pycodestyle --max-line-length 109 "${SRCS[@]}"
check_result "pycodestyle" $?

hrule

if [[ $STATUS -eq 0 ]]; then
    echo "All checks passed"
else
    echo "One or more checks failed!"
fi

hrule

exit $STATUS
