#!/usr/bin/env bash
# Recreates the command sequence documented in the Lab 1 report.
# Run inside a Linux container; observed values depend on that container.
set -u

scratch_dir=$(mktemp -d)
sleep_pid=
rss_pid=
cleanup() {
  if [[ -n $sleep_pid ]]; then kill "$sleep_pid" 2>/dev/null || true; fi
  if [[ -n $rss_pid ]]; then kill "$rss_pid" 2>/dev/null || true; fi
  rm -rf -- "$scratch_dir"
}
trap cleanup EXIT

echo '=== files and permissions ==='
ls -la "$HOME"
printf 'note\n' > "$scratch_dir/note.txt"
ls -l "$scratch_dir/note.txt"
chmod 600 "$scratch_dir/note.txt"
ls -l "$scratch_dir/note.txt"

echo '=== processes ==='
sleep 300 &
sleep_pid=$!
jobs
ps -ef | grep '[s]leep'
ps aux
ps aux | wc -l
head -20 "/proc/$sleep_pid/status"
grep '^State:' "/proc/$sleep_pid/status"

echo '=== memory ==='
free -h
sleep 1000 &
rss_pid=$!
grep '^VmRSS:' "/proc/$rss_pid/status"

echo '=== storage and devices ==='
lsblk
findmnt /
ls /dev
