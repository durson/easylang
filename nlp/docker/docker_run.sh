#!/bin/bash
set -eu -o pipefail

if [[ $# -lt 1 ]]; then
    echo "Usage: $0 [port] [opts..]"
    exit 1
fi

# opts
port=$1 ; shift

# config
timeout=10000
graceful_timeout=3000
workers_per_core=8
max_workers=1
log_level=error

nvidia-docker run --rm -it \
              --net=host \
              -e PORT=$port \
              -e TIMEOUT=$timeout \
              -e WORKERS_PER_CORE=$workers_per_core \
              -e MAX_WORKERS=$max_workers \
              -e LOG_LEVEL=$log_level \
              -e OPTS=$@ \
              --name easylang_nlp_container \
              easylang/nlp
