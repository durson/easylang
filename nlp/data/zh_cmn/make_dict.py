#!/usr/bin/env python3

from math import log, exp
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


def get_vocab(cedict, counts):
    vocab_parsed = {}
    vocab = {}
    for parsed in cedict:
        chars = list(parsed["simplified"])
        if len(chars) == 1:
            char = chars[0]
            if char in vocab_parsed:
                vocab_parsed[char].append(parsed)
            else:
                vocab_parsed[char] = [parsed]
        for char in chars:
            vocab[char] = 1
    vocab = sorted(vocab.keys())

    def retrieve_char_or_dummy(char):
        if char in vocab_parsed:
            parsed_arr = vocab_parsed[char]
        else:
            english = f"Letter {char}"
            if char in list("0123456789"):
                english = f"Number {char}"
            parsed_arr = [{
                "traditional": char,
                "simplified": char,
                "pinyin": char,
                "english": english,
            }]
        for parsed in parsed_arr:
            parsed["count"] = counts.get(char, -99.0)
        return parsed_arr

    vocab_out = []
    for char in vocab:
        vocab_out += retrieve_char_or_dummy(char)
    return vocab_out


def filter_surnames(cedict):
    for i in range(len(cedict)-1, -1, -1):
        if "surname " in cedict[i]["english"]:
            if cedict[i]["traditional"] == cedict[i+1]["traditional"]:
                cedict.pop(i)


def main(argv):
    if len(argv) != 4:
        raise ValueError("Usage: cedict words-count output-dir")

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

    counts_path = Path(argv[2])
    if not counts_path.exists():
        raise RuntimeError(f"{counts_path} does not exist.")

    counts = {}
    total_count = 0
    with open(counts_path, "r") as fp:
        for line in fp:
            line = line.rstrip("\n")
            _, word, _, count = map(lambda s: s[1:-1], line.split(","))
            if len(word) > 1:
                continue
            count = int(count)
            counts[word] = count
            total_count += count
    for key in counts:
        counts[key] = log(max(counts[key] / total_count, exp(-99.0)))

    output_dir = Path(argv[3])
    if not output_dir.exists():
        output_dir.mkdir(exist_ok=True)

    vocab = get_vocab(cedict, counts)
    with open(output_dir.joinpath("vocab.json"), "w") as fp:
        fp.write(json.dumps(vocab).decode())
    with open(output_dir.joinpath("dict.json"), "w") as fp:
        fp.write(json.dumps(cedict).decode())


main(sys.argv)
