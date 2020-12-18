#!/bin/bash
set -eu -o pipefail

zcat cedict_1_0_ts_utf-8_mdbg.txt.gz > cedict_1_0_ts_utf-8_mdbg.txt
zcat words_types.txt.gz > words_types.txt

rm -rf dict/
./make_dict.py cedict_1_0_ts_utf-8_mdbg.txt words_types.txt dict/
