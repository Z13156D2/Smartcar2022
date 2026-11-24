#!/usr/bin/env python3
"""Run an archived script with the project's original flat imports available."""
from __future__ import print_function

import argparse
import os
from pathlib import Path
import runpy
import sys


def main():
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('script', help='Python script path relative to repository root')
    parser.add_argument('args', nargs=argparse.REMAINDER, help='Arguments for the script')
    options = parser.parse_args()
    target = (root / options.script).resolve()
    try:
        target.relative_to(root)
    except ValueError:
        parser.error('Script must be inside the repository')
    if not target.is_file() or target.suffix != '.py':
        parser.error('Script must be an existing .py file')
    # Preserve imports such as `from camera import Camera` after moving scripts.
    sys.path[:0] = [str(target.parent), str(root / 'src'),
                    str(root / 'third_party' / 'runtime')]
    os.chdir(str(root))
    sys.argv = [str(target)] + options.args
    runpy.run_path(str(target), run_name='__main__')


if __name__ == '__main__':
    main()
