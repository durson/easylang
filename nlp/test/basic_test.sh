#!/bin/bash
set -eu -o pipefail

corrid=100
lang=zh_cmn

while true; do
    echo -n "user> "
    read line
    echo -n "asnwer> "
    curl -s -X POST \
         --header "corrid: $corrid" \
         --header "lang: $lang" \
         --data "$line" \
         localhost:8000/nlp/generate || echo
    echo
done
