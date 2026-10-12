![[Pasted image 20260928165634.png]]
### Part 1
![[Pasted image 20260928165854.png]]

![[Pasted image 20260928170044.png]]

1. The files are owned by the `root` user and belong to the `root` group.
2. After `chmod 600 note.txt`, the first ten characters are `-rw-------`: `-` means it is a regular file, `rw-` means the owner can read and write it, and `---` for both group and others means they have no permissions.
3. `/etc` — contains system-wide configuration files.
`/var` — contains variable data such as logs, caches, spool files, and other data that changes while the system is running.

### Part 2
![[Pasted image 20260928170205.png]]![[Pasted image 20260928170254.png]]

![[Pasted image 20260928170430.png]]

Process number 1 is bash:
![[Pasted image 20260928170538.png]]

There are 5 processes in my docker container:
![[Pasted image 20260928170610.png]]

The state line says "S" for the sleeping process:
![[Pasted image 20260928170655.png]]

### Part 3
The free -h result:![[Pasted image 20260928170733.png]]
The VM has 7.7Gb and 1.3 of it is free

Swap is disk memory that can be used as RAM for a short period of time when there is not enough RAM there is 1GB of it.

The sleep is using 1288KB which is like a megabyte of memory which is more that I would expect it to consume:

![[Pasted image 20260928170942.png]]

### Part 4
![[Pasted image 20260928171027.png]]

My root is mounted in the /var/ directory of my file system which is mounted to the MacOS disk.
![[Pasted image 20260928171149.png]]

The operating system manages **CPU/processes, memory, storage/filesystems, and I/O devices**. I inspected them using `ps` for processes, `/proc/<pid>/status` or `free` for memory, `lsblk` for storage, and `ls /dev` for devices. These commands show how the OS exposes and tracks the main resources it is responsible for managing.

Devices:
![[Pasted image 20260928171542.png]]

A Docker container was used to run all the commands
