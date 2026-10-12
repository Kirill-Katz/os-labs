#!/usr/bin/env bash
set -u
cd /home/class
base=http://192.168.64.1:8765
for name in args_linux.c sleep.c; do
  wget -q -O "$name" "$base/$name"
done
cp args.c xv6-riscv/user/args.c
cp sleep.c xv6-riscv/user/sleep.c
gcc -Wall -Wextra -o args args_linux.c
{
  echo '=== setup ==='
  find /home/class -name os2026-setup.sh -print
  command -v riscv64-linux-gnu-gcc
  command -v qemu-system-riscv64
  echo '=== user.h ==='
  grep -nE 'pause|sleep' xv6-riscv/user/user.h
  echo '=== UPROGS ==='
  grep -nE '_sleep|_args' xv6-riscv/Makefile
  echo '=== sleep.c ==='
  cat xv6-riscv/user/sleep.c
  echo '=== args.c ==='
  cat xv6-riscv/user/args.c
  echo '=== build ==='
  make -C xv6-riscv -s
  echo '=== bash shell comparison ==='
  mkdir -p /home/class/shtest
  cd /home/class/shtest
  touch README
  echo hello > f ; cat < f
  ls | grep READ
  (echo a; echo b) | wc
  echo one ; echo two
  echo bg & wait
  ls *
  echo "$HOME"
  echo "a b"
  mkdir -p d ; cd d ; ls ..
  cd ..
  echo '=== bash args ==='
  cp /home/class/args_linux.c .
  /home/class/args one              two         three
  /home/class/args *.c "x y"
  /home/class/args "$HOME"
  /home/class/args 'single quoted'
  echo '=== shell source ==='
  cd /home/class/xv6-riscv
  wc -l user/sh.c
  grep -n '#define' user/sh.c
  grep -n 'case ' user/sh.c
  grep -n 'cd' user/sh.c | head
  echo '=== shell special characters ==='
  grep -nE '\*|\$' user/sh.c | head -25
} > /home/class/lab4-results.txt 2>&1
