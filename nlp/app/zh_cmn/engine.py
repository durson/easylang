# coding: utf-8

from .engine_dict import ZhCmnEngineDict
from .engine_lm import ZhCmnEngineLm
from .common import *


class ZhCmnEngine:
    def iso():
        return iso()


    def __init__(self, cfg):
        self.engine_dict = ZhCmnEngineDict(cfg)
        self.engine_lm = ZhCmnEngineLm(cfg, self.engine_dict)


    def describe(self, text):
        return self.engine_dict.describe(text)


    def predict(self, corrid, text):
        return self.engine_lm.predict(corrid, text)
