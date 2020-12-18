# coding: utf-8

import orjson as json

from pathlib import Path
from .common import *


class ZhCmnEngineDict:
    def __init__(self, cfg):
        dict_path = Path(cfg[iso()]["engine_dict"]["dict_path"])
        with open(dict_path.joinpath("dict.json"), "r") as fp:
            dict_json = json.loads(fp.read())
        with open(dict_path.joinpath("vocab.json"), "r") as fp:
            vocab_json = json.loads(fp.read())

        d = {}
        v = {}
        for entry in dict_json:
            d[entry["simplified"]] = entry
        for entry in vocab_json:
            v[entry["simplified"]] = entry

        self.d = d
        self.v = v


    def describe(self, text):
        output = []
        start = 0
        while start < len(text):
            end = len(text)
            for end in range(len(text), start, -1):
                subtext = text[start:end]
                if subtext in self.d:
                    output.append(self.d[subtext])
                    start = end
                    break
                elif end == start + 1:
                    if subtext in self.v:
                        output.append(self.v[subtext])
                    start = end
                    break
        return output
