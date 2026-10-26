# Lab 8 — The same calls inside xv6

I rebuilt the integrated `xv6-riscv` tree with `make clean && make fs.img`, booted it in QEMU, and ran the required programs on 26 October 2026. The final `user/run.c` executes `echo`. I made temporary `ls` and missing-program variants for the requested observations, then restored the final source and disk image. Both source files and the Makefile are copied into `lab8/code/`.

## Part 1 — run

```text
$ run
parent: my pid is 3
child: my pid is 4
hello from the child
parent: child 4 ended with status 0
```

After temporarily changing the child to `char *args[] = { "ls", 0 }; exec("ls", args);`, it printed a directory listing and ended with status 0:

```text
$ run
parent: my pid is 3
child: my pid is 4
.              1 1 1024
..             1 1 1024
README         2 2 2441
... (other directory entries)
console        3 29 0
parent: child 4 ended with status 0
```

After temporarily changing the child to `exec("nosuchprog", args);`, it could not replace its program:

```text
$ run
parent: my pid is 3
child: my pid is 4
exec failed
parent: child 4 ended with status 1
```

1. The xv6 program uses `fork`, `exec`, and `wait`. The Lab 7 POSIX program uses `fork`, `execlp`, and `waitpid`. Both sequences create a child, replace the child's program, and collect its exit status. The library call names and arguments differ, while the process behavior is the same.
2. The `echo` program prints `hello from the child` after a successful `exec`. The original `run` code does not print that line; it provides the words as arguments to `echo`.
3. On failed `exec`, xv6's `run.c` calls `exit(1)`, while Lab 7's `run.c` calls `exit(127)`. The parent reports the exit code explicitly chosen by the child in each program.

## Part 2 — pingpong

```text
$ pingpong
6: received ping
5: received pong
$ pingpong
8: received ping
7: received pong
```

1. Each xv6 pipe carries bytes in one direction. The parent-to-child pipe delivers the initial byte and the child-to-parent pipe carries it back. Using separate pipes also gives each process a clear read end and write end to close when unused.
2. The parent's `read(c2p[0], &b, 1)` blocks until the child writes the reply byte. The later `wait(&status)` reaps the child; it is not the call that waits for the reply.

## Conclusion

The xv6 experiments reproduced the process steps from Lab 7 with xv6's smaller system-call interface. A successful `exec` runs the new program in the child; a failed one returns to the caller, which chooses its exit status. The two-pipe exchange showed that a blocking read orders the ping and pong messages without a separate timing delay.
