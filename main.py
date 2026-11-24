#!/usr/bin/env python3
"""Meme Sprint 3 entry: write the meme image to /output/entry.png.

Standard library only. The image ships in this repository as entry.png
(it was drawn by draw.py, kept here as provenance); this program copies it
to the output path and verifies the copy byte-for-byte, exiting non-zero
on any mismatch.

Usage: python3 main.py [output_path]   (default /output/entry.png)
"""

import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(HERE, "entry.png")
DEFAULT_OUT = "/output/entry.png"


def main(argv):
    out = argv[1] if len(argv) > 1 else DEFAULT_OUT
    parent = os.path.dirname(os.path.abspath(out))
    if parent:
        os.makedirs(parent, exist_ok=True)
    shutil.copyfile(SOURCE, out)
    with open(SOURCE, "rb") as f:
        want = f.read()
    with open(out, "rb") as f:
        got = f.read()
    if got != want:
        print("error: output does not match shipped entry.png", file=sys.stderr)
        return 1
    print("wrote %s (%d bytes, verified)" % (out, len(got)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
