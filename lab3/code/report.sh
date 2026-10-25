#!/bin/bash
# usage: ./report.sh access.log
log=$1
if [ ! -f "$log" ]; then
    echo "no such file: $log" >&2
    exit 1
fi

total=$(wc -l < "$log")
fails=$(grep -c ' FAIL ' "$log")
echo "$total requests, $fails failed"

for n in {0..6}; do
    count=$(awk -v user="user$n" '$3 == user && $4 == "FAIL" {count++} END {print count+0}' "$log")
    echo "user$n: $count failures"
done
