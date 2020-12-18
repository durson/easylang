#!/usr/bin/env python3

import sys
import json

from pathlib import Path


def parse_line(line):
    if line.startswith("#") or line == "":
        return None
    line = line.rstrip("/")
    line = line.split("/")
    if len(line) < 2:
        return None
    characters, pinyin = line[0].split("[")
    english = line[1]

    traditional, simplified = characters.split()
    pinyin = pinyin.rstrip().rstrip("]")

    parsed = {}
    parsed["traditional"] = traditional
    parsed["simplified"] = simplified
    parsed["pinyin"] = pinyin
    parsed["english"] = english
    return parsed


def filter_surnames(cedict):
    for i in range(len(cedict)-1, -1, -1):
        if "surname " in cedict[i]["english"]:
            if cedict[i]["traditional"] == cedict[i+1]["traditional"]:
                cedict.pop(i)


def main(argv):
    cedict_path = Path("cedict_1_0_ts_utf-8_mdbg.txt")
    if not cedict_path.exists():
        raise RuntimeError(f"{cedict_path} does not exist.")

    cedict = []
    with open(cedict_path, "r") as fp:
        for line in fp:
            line = line.rstrip("\n")
            parsed = parse_line(line)
            if parsed is not None:
                cedict.append(parsed)
    filter_surnames(cedict)
    return cedict


parsed_dict = main(sys.argv)

print("\n".join(map(lambda d: str(d), parsed_dict)))
