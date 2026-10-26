# Lab 6 observations

Recorded in the local xv6-riscv tree under QEMU on 26 October 2026. The disk image was rebuilt with `make clean && make fs.img` before the run. Values such as inode numbers depend on the programs included in `UPROGS`.

## Part 1: directory entries and types

`kernel/stat.h` defines type 1 as directory (`T_DIR`), type 2 as regular file (`T_FILE`), and type 3 as device (`T_DEVICE`). The root is inode 1 (`ROOTINO` in `kernel/fs.h`). Its `.` and `..` both point to inode 1 because it has no parent above itself. A directory entry is 16 bytes: a 2-byte inode number plus a 14-byte name. A newly created directory contains `.` (itself) and `..` (its parent), hence 32 bytes.

```text
$ ls .
.              1 1 1024
..             1 1 1024
README         2 2 2441
... (other built-in programs)
console        3 27 0
$ mkdir a
$ ls a
.              1 28 32
..             1 1 1024
```

## Part 2: mystat and hard links

`mystat` calls `stat()` on each supplied path, prints the type, inode, link count and size, and reports failures to file descriptor 2 while continuing with later paths.

```text
$ mystat README . console
README: file, inode 2, links 1, size 2441 bytes
.: directory, inode 1, links 2, size 1024 bytes
console: device, inode 27, links 1, size 0 bytes
$ ln README r2
$ mystat README r2
README: file, inode 2, links 2, size 2441 bytes
r2: file, inode 2, links 2, size 2441 bytes
$ rm README
$ mystat r2
r2: file, inode 2, links 1, size 2441 bytes
$ cat r2 | wc
48 336 2441
```

After `ln`, both names have inode 2, the same size, and link count 2. After `rm README`, `r2` still refers to inode 2 with the same 2441-byte content, while its link count falls to 1. The root link count is 2 here because `mkdir a` had already added a child directory.

`kernel/sysfile.c`, in `sys_unlink`, decrements the target with `ip->nlink--;` and writes it with `iupdate(ip);`. When the count reaches zero and the last in-memory reference is dropped, `iput()` in `kernel/fs.c` calls `itrunc(ip)` to free its data blocks. The on-disk `struct dinode` fields are `type`, `major`, `minor`, `nlink`, `size`, and `addrs[NDIRECT + 1]` (12 direct addresses and one indirect address).

## Part 3: file system limits

`kernel/fs.h` sets `BSIZE=1024`, `NDIRECT=12`, `NINDIRECT=BSIZE/sizeof(uint)=256`, and `DIRSIZ=14`. A long name is cut to 14 bytes in the directory entry:

```text
$ mkdir averyveryverylongname
$ ls .
averyveryveryl 1 29 32
```

The maximum file length is `(12 + 1024/4) * 1024 = 274432` bytes (268 KiB). The image layout printed by `make fs.img` was:

```text
nmeta 47 (boot, super, log blocks 31, inode blocks 13, bitmap blocks 1) blocks 1953 total 2000
```

Thus the whole disk has 2000 blocks, of which 31 are log blocks, 13 are inode blocks, and 1953 are data blocks. The other 3 are boot, superblock, and bitmap.

## Part 4: recursive find

`find` walks directory entries, skips free slots and `.`/`..`, compares each last component with the requested name, and closes each directory after reading it.

```text
$ mkdir a/b
$ echo x > a/b/r2
$ echo y > a/r2
$ find . r2
./a/b/r2
./a/r2
./r2
$ find a b
a/b
```

The two files created with `echo` have separate inodes from the root-level `r2`. To check hard-link identity independently, I created `r3` as a link to `cat`:

```text
$ ln cat r3
$ find . r3
./r3
$ mystat cat r3
cat: file, inode 7, links 2, size 37344 bytes
r3: file, inode 7, links 2, size 37344 bytes
```
