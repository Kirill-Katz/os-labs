#!/bin/sh
# Run from lab9/ in the Docker image; all generated evidence stays on the mount.
set -eu
cd /work
mkdir -p report_files/output
out=/work/report_files/output
exec > "$out/session.txt" 2>&1
set -x
uname -a
cat /etc/os-release
gcc --version
strace --version
umask 022
gcc -std=c11 -Wall -Wextra -Werror -O0 -g -o "$out/syscalls" code/syscalls.c
# A small, fixed directory makes the ls experiment independent of the host tree.
rm -rf "$out/work"
mkdir -p "$out/work/listing"
cd "$out/work"
printf 'Lab 9 strace fixture\n' > listing/example.txt
cd listing
strace -f -e trace=openat,read,write,close -o "$out/ls.trace" ls -l > "$out/ls.stdout"
strace -c -o "$out/ls.summary" ls -l > /dev/null
cd ..
"$out/syscalls" > "$out/syscalls.stdout"
cp note.txt "$out/note.txt"
strace -e trace=openat,write,read,close -o "$out/syscalls.trace" "$out/syscalls" > "$out/syscalls-traced.stdout"
strace -c -e trace=write -o "$out/write.summary" "$out/syscalls" > "$out/count.stdout"
strace -e trace=write -o "$out/write.trace" "$out/syscalls" > /dev/null
python3 /work/code/verify.py
