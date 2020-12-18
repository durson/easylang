#!/usr/bin/env python3

import sys
import orjson as json

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


def get_vocab(cedict):
    vocab_parsed = {}
    vocab = {}
    for parsed in cedict:
        chars = list(parsed["simplified"])
        if len(chars) == 1:
            vocab_parsed[chars[0]] = parsed
        for char in chars:
            vocab[char] = 1
    vocab = sorted(vocab.keys())

    def retrieve_char_or_dummy(char):
        if char in vocab_parsed:
            return vocab_parsed[char]
        else:
            english = f"Letter {char}"
            if char in list("0123456789"):
                english = f"Number {char}"
            return {
                "traditional": char,
                "simplified": char,
                "pinyin": char,
                "english": english
            }

    return list(map(retrieve_char_or_dummy, vocab))


def filter_surnames(cedict):
    for i in range(len(cedict)-1, -1, -1):
        if "surname " in cedict[i]["english"]:
            if cedict[i]["traditional"] == cedict[i+1]["traditional"]:
                cedict.pop(i)


def main(argv):
    if len(argv) != 3:
        raise ValueError("Usage: cedict-path output-dir")

    cedict_path = Path(argv[1])
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

    output_dir = Path(argv[2])
    if not output_dir.exists():
        output_dir.mkdir(exist_ok=True)

    vocab = get_vocab(cedict)
    with open(output_dir.joinpath("vocab.json"), "w") as fp:
        fp.write(json.dumps(vocab).decode())
    with open(output_dir.joinpath("dict.json"), "w") as fp:
        fp.write(json.dumps(cedict).decode())
    return cedict


parsed_dict = main(sys.argv)

print("\n".join(map(str, parsed_dict)))
