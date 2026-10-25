#!/usr/bin/env bash
# Recreate the 500-row access.log from the Lab 3 instructions.
set -euo pipefail

for i in $(seq 1 500); do
  echo "2026-10-05 10:$(printf %02d $((i % 60))) user$((i % 7)) $([ $((i % 5)) -eq 0 ] && echo FAIL || echo OK) /page$((i % 4))"
done > access.log

head -3 access.log
wc -l access.log
