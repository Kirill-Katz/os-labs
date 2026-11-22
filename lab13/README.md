# Lab 13 — Semaphores in Your Own Kernel

- **Submission report:** [report.pdf](report.pdf)
- **Four required Observe answers:** [notes.txt](notes.txt)
- **Working modified xv6 tree:** [../xv6-riscv/](../xv6-riscv/)
- **Matching changed sources and patch:** [code/](code/)
- **Editable report and assignment:** [report_files/](report_files/)
- **Original checkpoints and test evidence:** [report_files/output/](report_files/output/)

All three required parts are complete. The new syscalls are **sem_init = 24, sem_down = 25, sem_up = 26**, and semaphore IDs **0–7** refer to one global table shared by all processes. Existing `sync` (22) and Lab 10 `trace` (23) remain intact. The optional `sem_trydown` syscall 27 is not included.

## Build and boot on Ubuntu

```sh
sudo apt update
sudo apt install build-essential gcc-riscv64-linux-gnu \
  binutils-riscv64-linux-gnu qemu-system-misc bc perl
# From the repository root:
cd xv6-riscv
make clean
make -j4 TOOLPREFIX=riscv64-linux-gnu- kernel/kernel fs.img
make qemu TOOLPREFIX=riscv64-linux-gnu- CPUS=3
```

At the xv6 prompt:

```text
semtest
mix
mix
mix lock
mix lock
semcheck
semsleep
trace 117440512 semprobe
trace 32 grep hello README
usertests -q
```

Ctrl-A followed by X exits QEMU. While `semsleep` displays its waiting-child message, Ctrl-P prints the process table; look for its child in state `sleep`. The program posts after its observation interval and reaps the child. Recorded tools: Ubuntu 24.04.5 LTS (aarch64), RISC-V GCC 13.3.0 and QEMU 8.2.2, with three guest CPUs and 128 MiB RAM.

`semtest` must print the parent before the child, then three strict ping/pong pairs, then `semtest: OK`. The handout program leaves return values unchecked, so the final OK string alone is not sufficient evidence: verify the full sequence and run the checked regressions too. `mix` may interleave letters because one 30-letter line plus newline uses 31 separate writes. `mix lock` must produce five intact A lines and five intact b lines; the whole-line order need not match the sample.

## Implementation

| Files | Role |
| --- | --- |
| `kernel/syscall.h`, `user/user.h`, `user/usys.pl` | Numbers, declarations and generated ecall stubs. |
| `kernel/sem.c` | Eight counting semaphores; argument checks; protected down/up operations and wakeups. |
| `kernel/main.c`, `kernel/defs.h` | Initialize semaphore locks at boot; expose the internal initialization and interruptible-sleep entry points. |
| `kernel/proc.c` | Preserve ordinary sleep and add a narrowly scoped killable two-phase sleep path for semaphore waits. |
| `kernel/syscall.c` | Handler registration and trace names for the three new calls. |
| `Makefile` | Link `kernel/sem.o`; include the required programs and three test tools in the disk image. |
| `user/semtest.c`, `user/mix.c` | Required handout programs. |
| `user/semcheck.c`, `user/semsleep.c`, `user/semprobe.c` | Checked semantic regression, sleeping-state evidence, and trace-name probe. |

`sem_down` registers the semaphore address under its spinlock, releases the lock before sleeping, then reacquires it and checks again. `sem_up` increments and wakes all waiters on the same address. A wakeup is not a reserved token; the `while` is required. Each handler rejects IDs outside 0–7; init also rejects negative values.

### Small robustness additions

- `seminit()` explicitly initializes each spinlock before user processes start.
- Up rejects a count increment at `0x7fffffff`, avoiding signed overflow without changing the current count.
- `sleep_killable()` closes a kill-after-registration/before-sleep timing gap. The existing sleep body is shared privately through `sleep_common`: ordinary `sleep()` preserves the original behavior, while the semaphore-specific path checks `p->killed` under the process lock immediately before becoming sleeping. The semaphore handler then checks cancellation after returning. This avoids changing unrelated kernel wait semantics.

The sleep interface is still this tree's two-phase `sleep_prepare`/release/sleep/reacquire design, not the xv6 book's incompatible `sleep(chan, lock)` API. The cancellation guard was motivated by code inspection; no pre-fix failure is claimed to have been reproduced.

These are global teaching objects, not named or owned POSIX semaphores. Initialize/reset before concurrent use; concurrent reset, access control, FIFO fairness, and automatic recovery of a permit held by an exiting process are outside this implementation's contract.

## Recorded checkpoints and tests

`checkpoint1.txt` is the genuine intermediate run captured after the numbers and user stubs but before kernel handlers existed. It begins with unknown calls 24/25 and the child before the parent. Its later errors and ping/pong characters interleave. The report's excerpt is explicitly shortened; the full capture is retained. The final submitted sources contain the completed implementation, so they are not expected to reproduce that historical checkpoint.

The final run includes three exact `semtest` runs, two unlocked and three locked `mix` runs, focused regressions, a Ctrl-P snapshot, trace probes, and the complete quick suite. Results:

- All eight IDs and invalid argument cases checked.
- Overflow guard preserves the maximum count.
- Six waiting children complete after six posts.
- 1000 ping/pong rounds complete without a missed-wakeup hang.
- Twenty immediate/already-blocked waiter kills are reaped successfully.
- The captured waiter is in `sleep` state and later wakes normally.
- All three new syscall names work through the existing tracer.
- The old read trace still returns 1023, 965, 453, 0.
- **68 tests in `usertests -q`: ALL TESTS PASSED.** Memory-protection tests deliberately print user-trap diagnostics; those are not kernel panics.
- **62 evidence assertions pass**, including byte-for-byte comparison of fourteen source copies with the tested integrated tree.

A sleeping-state snapshot supports the blocking design but is not a CPU-utilization benchmark. The stress/cancellation tests are useful regressions, not exhaustive coverage of all schedules.

## Repeat the final automated run

On Ubuntu, from the repository root:

```sh
sudo apt install python3 python3-pexpect
python3 lab13/code/run_qemu.py final
python3 lab13/code/verify.py
```

The runner boots QEMU, waits for real prompts, captures each command and a complete session, sends Ctrl-P for the sleeping-state evidence, and exits QEMU. Its timeout is bounded per command, with a longer allowance for the quick suite. It does not roll back the sources to recreate Part 1. The verifier also checks the retained historical baseline/checkpoint, so keep those files.

Rerunning overwrites final captures. Update quoted observations/PIDs and the report excerpts before rebuilding. The source copies must match the integrated files; changes to either require refreshing their counterpart. Original build/boot tooling and environment logs are retained separately from the report prose.

## Source copies and patch

The integrated tree is the primary submission. `code/` includes fourteen complete changed-file copies and `semaphores.patch`, including all six new source files. The patch is against this repository's **pre-Lab-13** tree, which includes earlier lab programs and the trace implementation, not arbitrary upstream xv6. From a matching repository root, use `git apply lab13/code/semaphores.patch`; do not reapply it to the already-modified tree.

## Rebuild the report

With `pdflatex`, Latin Modern, microtype, needspace, booktabs, amsmath and listings installed:

```sh
cd lab13/report_files
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=.. report.tex
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=.. report.tex
rm -f ../report.aux ../report.log ../report.out ../report.toc
```

The cover, contents, experiment sections, complete Observe Q&A, verification and conclusion follow the previous reports. The handout asks for the modified tree to be committed; a local commit is not a push to the course repository.
