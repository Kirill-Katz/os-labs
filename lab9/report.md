# Lab 9 — Watching System Calls with strace

## Aim and environment

Observe Linux system calls from outside a process, then use descriptor-based file I/O directly. All compilation, runs, traces and tests were performed on Ubuntu 24.04.5 LTS (aarch64), using GCC 13.3.0 and strace 6.8.

The supplied two-page handout lists Part 3 in its overview but ends after Part 2's Observe question. The counting exercise below is a supplement based on that heading; no missing instructions or questions are invented.

## Part 1 — A real command

Ran `strace -f -e trace=openat,read,write,close ls -l` in a clean, one-file directory. The runner sends traces to `ls.trace` with `-o` and captures stdout separately in `ls.stdout`.

- Observed 38 filtered calls: 10 openat, 11 read, 16 close, 1 write.
- The final separate full `strace -c ls -l` run counted 113 calls (an earlier run counted 114). This is roughly a hundred, not a fixed requirement.
- Startup loads libraries; long listings also read user/group information. Actual directory-entry reads use `getdents64`, which the four-call filter hides; the full summary shows two such calls.
- The summary's 12 errors include unsuccessful environment probes; `ls` itself exited successfully.

**Observe: Which system call does ls use to print to the screen? To which descriptor does it write?**

`write`, to descriptor **1**, standard output. The recorded call was `write(1, ..., 59) = 59`. In this capture stdout was redirected to a file; when connected to a terminal, that same descriptor sends output to the screen.

## Part 2 — File round trip

Built `code/syscalls.c` with `gcc -std=c11 -Wall -Wextra -Werror -O0 -g`. The program uses open/write/read/close for the file and printf only for diagnostics. Compared with the handout example it checks failures before indexing the buffer, handles short writes and interrupted I/O, and checks normal-path closes.

```text
open returned descriptor 3
write sent 14 bytes
read got 14 bytes: hello, kernel
```

Observed file calls, excerpted from `report_files/output/syscalls.trace`:

```text
openat(AT_FDCWD, "note.txt", O_WRONLY|O_CREAT|O_TRUNC, 0644) = 3
write(3, "hello, kernel\n", 14)         = 14
close(3)                                = 0
openat(AT_FDCWD, "note.txt", O_RDONLY)  = 3
read(3, "hello, kernel\n", 63)          = 14
close(3)                                = 0
```

The C library's open wrapper becomes Linux openat in this environment. These are libc wrappers, not handwritten syscall assembly. `AT_FDCWD` resolves the relative pathname against the current directory. `O_TRUNC` discards old contents; creation mode 0644 is subject to umask (022 here). The message contains 14 bytes including newline, excluding its C null terminator. The 63-byte request reserves one byte for termination; read returns the 14 bytes available in this tiny file. The example uses a single read, not a general file-copy loop.

**Observe: The descriptor returned by the first openat is 3, not 0, 1 or 2. Why are those three already taken?**

They are inherited standard descriptors: **0 = stdin**, **1 = stdout**, **2 = stderr**. With those open, the lowest unused descriptor is 3. The dynamic loader briefly used and closed 3 before main; the second file open reuses 3 after the program closes it. A descriptor is a per-process handle, not a permanent file identifier.

## Part 3 — Count write calls (supplement)

Ran `strace -c -e trace=write ./syscalls` and independently captured `strace -e trace=write ./syscalls`.

The summary counted **two write calls**: one sends 14 bytes to note.txt (fd 3); one sends 80 bytes of diagnostics to stdout (fd 1). Three printf calls became one write because stdout was redirected to a regular file and libc buffered the messages until exit. The file write appears before the buffered diagnostics in the trace. Terminal line buffering can produce a different stdout call count.

## Verification and conclusion

All 15 verifier assertions passed on the final rerun: exact normal/traced/counting output, exact file bytes, ordered file syscall sequence, independent write-count agreement, truncation of an existing longer file, clean failure when note.txt is a directory, and clean write failure through a symlink to /dev/full. Read/close error branches were reviewed but not separately fault-injected.

System calls expose kernel operations and actual byte counts; descriptors can be reused after close. Startup and metadata work explain why a simple command makes many calls. Stdio buffering explains why source-level print counts differ from kernel write counts.

See `report.pdf` for the formatted report and `report_files/output/` for original evidence. To run the core exercise on Ubuntu:

```sh
sudo apt update
sudo apt install gcc libc6-dev strace
cd lab9/code
gcc -std=c11 -Wall -Wextra -Werror -O0 -g -o /tmp/syscalls syscalls.c
mkdir -p /tmp/lab9-run
cd /tmp/lab9-run
/tmp/syscalls
strace -f -e trace=openat,read,write,close ls -l
strace -e trace=openat,write,read,close /tmp/syscalls
strace -c -e trace=write /tmp/syscalls
```

When stdout is a terminal, buffering and the write count can differ from the captured regular-file output.
