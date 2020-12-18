#!/bin/bash
set -eu -o pipefail

lang=zh_cmn

while true; do
    echo -n "user> "
    read line
    echo -n "asnwer> "
    curl -s -X POST \
         --header "lang: $lang" \
         --data "$line" \
         localhost:8000/nlp/describe \
        | python3 -c "
import sys
import orjson
import json
msg = sys.stdin.read()
try:
    j = orjson.loads(msg)
    print(json.dumps(j, indent=2, ensure_ascii=False))
except Exception as e:
    print('error', str(e))
    print(msg)
"
    echo
done
