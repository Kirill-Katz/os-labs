#!/usr/bin/env bash
# Lab 5 observations. Run as the normal Linux user in the course VM.
set +e
mkdir -p "$HOME/os-lab5"
workdir=$(mktemp -d "$HOME/os-lab5/run.XXXXXX")
exec > >(tee "$HOME/os-lab5/lab5-results.txt") 2>&1
cd "$workdir" || exit 1

echo '=== environment ==='
whoami
printf 'workdir=%s\n' "$PWD"
date -Is

echo '=== part 1: paths and types ==='
ls /
ls -ld /etc /etc/passwd /bin /dev/null /tmp
ls -l /dev | head
ls -l /dev/null /dev/vda /dev/sda 2>&1
file /usr/bin/ls /etc/passwd /bin
du -sh /var/log 2>/dev/null
du -sh /usr 2>/dev/null

echo '=== part 2: inodes and links ==='
echo hello > notes.txt
stat notes.txt
ls -li notes.txt
ln notes.txt hard.txt
ls -li notes.txt hard.txt
rm notes.txt
cat hard.txt
ls -li hard.txt
ln -s hard.txt soft.txt
ls -li hard.txt soft.txt
cat soft.txt
rm hard.txt
cat soft.txt
ls -l soft.txt
stat soft.txt
mkdir d
ls -ld d
mkdir d/x d/y
ls -ld d
echo x > one.txt
ls -l one.txt
du -h one.txt
truncate -s 1G big.img
ls -lh big.img
du -h big.img
rm big.img

echo '=== part 3: permissions ==='
echo secret > s.txt
chmod 600 s.txt
ls -l s.txt
chmod 000 s.txt
ls -l s.txt
cat s.txt
chmod u+r s.txt
cat s.txt
umask
touch new.txt
mkdir newdir
ls -ld new.txt newdir
mkdir box
echo hi > box/f
chmod u=r,go= box
ls -ld box
ls box
cat box/f
chmod u=x,go= box
ls -ld box
ls box
cat box/f
chmod 755 box
ls -l /usr/bin/passwd
ls -ld /tmp
cat /etc/shadow
ls -l /etc/shadow

echo '=== part 4: disks and proc ==='
lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINTS
df -h /
mount | grep ' / '
findmnt -no SOURCE,FSTYPE,TARGET /
grep -c '^processor' /proc/cpuinfo
grep '^MemTotal:' /proc/meminfo
head -3 /proc/meminfo
head -5 /proc/self/status
ls -l /proc/self/fd

echo '=== done ==='
