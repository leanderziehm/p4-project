#!/usr/bin/env python3

import argparse
import glob
import os
import shutil
import subprocess
import sys
from pathlib import Path

BUILD_DIR = "build"
PCAP_DIR = "pcaps"
LOG_DIR = "logs"

P4C = "p4c-bm2-ss"
RUN_SCRIPT = "../../utils/run_exercise.py"

TOPO = os.environ.get("TOPO", "topology.json")

SOURCE_FILES = glob.glob("*.p4")

DEFAULT_PROG = os.environ.get("DEFAULT_PROG")
if not DEFAULT_PROG:
    DEFAULT_PROG = SOURCE_FILES[0] if SOURCE_FILES else None

DEFAULT_JSON = (
    os.path.join(BUILD_DIR, DEFAULT_PROG.replace(".p4", ".json"))
    if DEFAULT_PROG
    else None
)


def run_cmd(cmd):
    print(" ".join(cmd))
    subprocess.run(cmd, check=True)


def create_dirs():
    os.makedirs(BUILD_DIR, exist_ok=True)
    os.makedirs(PCAP_DIR, exist_ok=True)
    os.makedirs(LOG_DIR, exist_ok=True)


def compile_p4(p4_file):
    output_json = os.path.join(
        BUILD_DIR,
        Path(p4_file).with_suffix(".json").name
    )

    p4info_file = os.path.join(
        BUILD_DIR,
        f"{Path(p4_file).stem}.p4.p4info.txt"
    )

    cmd = [
        P4C,
        "--p4v", "16",
        "--p4runtime-files", p4info_file,
        "-o", output_json,
        p4_file,
    ]

    run_cmd(cmd)


def build():
    create_dirs()

    if not SOURCE_FILES:
        print("No .p4 files found.")
        return

    for p4_file in SOURCE_FILES:
        compile_p4(p4_file)


def run():
    build()

    cmd = ["sudo", "python3", RUN_SCRIPT, "-t", TOPO]

    if "NO_P4" not in os.environ and DEFAULT_JSON:
        cmd.extend(["-j", DEFAULT_JSON])

    bmv2_switch = os.environ.get("BMV2_SWITCH_EXE")
    if bmv2_switch:
        cmd.extend(["-b", bmv2_switch])

    run_cmd(cmd)


def stop():
    run_cmd(["sudo", "mn", "-c"])


def clean():
    try:
        stop()
    except subprocess.CalledProcessError:
        pass

    for pcap in glob.glob("*.pcap"):
        os.remove(pcap)

    for directory in [BUILD_DIR, PCAP_DIR, LOG_DIR]:
        shutil.rmtree(directory, ignore_errors=True)


def main():
    parser = argparse.ArgumentParser(description="P4 Exercise Build Tool")
    parser.add_argument(
        "command",
        choices=["build", "run", "stop", "clean"],
        nargs="?",
        default="run",
    )

    args = parser.parse_args()

    try:
        {
            "build": build,
            "run": run,
            "stop": stop,
            "clean": clean,
        }[args.command]()
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)


if __name__ == "__main__":
    main()