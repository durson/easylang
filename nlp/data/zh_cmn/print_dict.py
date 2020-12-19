#!/usr/bin/env python3

import sys
import orjson as json

from pathlib import Path


def main(argv):
    if len(argv) != 2:
        raise ValueError("Usage: dict-path")

    dict_path = Path(argv[1])
    if not dict_path.exists():
        raise RuntimeError(f"{dict_path} does not exist.")

    with open(dict_path, "r") as fp:
        d = json.loads(fp.read())
        for entry in d:
            print(json.dumps(entry).decode())


main(sys.argv)
