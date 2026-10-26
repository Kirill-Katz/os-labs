# Lab 7 — Three Small Programs

I built and ran the four required POSIX C programs on macOS on 26 October 2026. `gcc --version` reported Apple clang 21.0.0. I used `/tmp/lab7-run` for binaries and generated files so the submitted `code/` directory contains only sources. The C sources are also mirrored in `../xv6-riscv/lab7-linux/`; they are Linux/POSIX exercises and are deliberately outside xv6's `UPROGS`.

All four sources compiled with `gcc -std=c11 -Wall -Wextra -Werror`. The optional three-stage pipeline was not part of the required work.

## Part 1 — fork, exec, wait

Final `run.c` executes `ls -l`. I changed its `execlp` line in temporary copies to run `date` and `nosuchprog`, then restored the final source to `ls`.

```text
$ ./run
parent: my PID is 55082
child:  my PID is 55084, my parent is 55082
total 536
... (directory listing)
parent: child 55084 ended with status 0

$ ./run_date
parent: my PID is 52683
child:  my PID is 52695, my parent is 52683
Mon Oct 26 11:05:35 EET 2026
parent: child 52695 ended with status 0

$ ./run_missing
parent: my PID is 52681
child:  my PID is 52694, my parent is 52681
exec: No such file or directory
parent: child 52694 ended with status 127
```

1. `execlp` replaces the child process image when it succeeds, so execution does not return to the following `perror` line. With `nosuchprog`, lookup fails and `execlp` returns, causing `perror("exec")` to print the error.
2. The child's "my parent" value is 55082 in the `ls` run, the PID printed by the original parent process. The `date` and failing runs similarly show their own parent PIDs.
3. The parent sees exit status 0 for `ls` and 127 for `nosuchprog`; the latter is explicitly passed to `exit(127)` after the failed `execlp`.

## Part 2 — zombie

`zombie.c` runs `ls -l` and sleeps 20 seconds before `waitpid`. I started it in the background, inspected the parent and its child after two seconds, then checked again after the parent finished:

```text
$ ./zombie > /dev/null &
$ sleep 2
$ ps -o pid,ppid,stat,command -p 54291
  PID  PPID STAT COMMAND
54291 54289 SN   ./zombie
$ ps -axo pid,ppid,stat,command | awk '$2 == 54291 {print}'
54293 54291 ZN   <defunct>
$ wait
$ ps -axo pid,ppid,stat,command | awk '$2 == 54291 {print}'
(no rows)
```

1. The child's `STAT` begins with `Z`, meaning zombie: it has exited, but its parent has not yet collected its status. The `N` shown by macOS is a scheduling flag.
2. After 20 seconds the defunct child is gone. The `waitpid(pid, &status, 0)` line reaps it.

## Part 3 — output redirection

```text
$ ./redirect
open gave descriptor 1
done: the listing is in out.txt
$ head -3 out.txt
total 448
-rw-r--r--@ 1 chirilcat  wheel      0 Oct 26 11:05 out.txt
-rwxr-xr-x@ 1 chirilcat  wheel  33848 Oct 26 11:05 pipeline
```

1. `open` returned 1 because the child first closed descriptor 1 (standard output), and `open` selects the lowest free descriptor.
2. `ls` still writes to descriptor 1, but that descriptor now refers to `out.txt`, so its listing goes to the file. The diagnostic from `fprintf(stderr, ...)` still appears on screen through descriptor 2.
3. To redirect standard error, close descriptor 2 before opening `err.txt` (or use `dup2` to assign the opened file to descriptor 2).

## Part 4 — pipe

```text
$ ./pipeline
      77
$ ls /etc | wc -l
      77
```

1. Yes, both pipelines printed 77 on this host. In the C program, `ls` writes to the pipe and `wc -l` reads from it.
2. I made a temporary test variant that commented out the parent's `close(p[1]);`. It stayed running. The process table showed the parent and `wc -l` still active after two seconds; the `ls` child had already ended:

```text
  PID  PPID STAT COMMAND
54803 54801 SN   ./pipeline_broken
54806 54803 SN   wc -l
```

3. `wc` is waiting for end-of-file on the pipe, which cannot arrive while the parent still holds an open copy of its write end. I stopped the temporary test processes after recording their state; the submitted `pipeline.c` closes both parent pipe ends.

## Conclusion

The runs show that `fork` creates a child, `exec` replaces its program, and `waitpid` reaps it. Redirection and pipelines work by assigning file or pipe endpoints to the standard descriptors before `exec`. Closing unused pipe ends is necessary for the reader to observe end-of-file.
