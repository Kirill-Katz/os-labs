# Lab 10 — Add Your Own System Call: trace

- **Submission report:** [report.pdf](report.pdf)
- **Required Observe answers:** [notes.txt](notes.txt)
- **Working modified xv6 tree:** [../xv6-riscv/](../xv6-riscv/)
- **Matching changed sources and Makefile:** [code/](code/)
- **LaTeX source and handout:** [report_files/](report_files/)
- **Original boot, build and experiment output:** [report_files/output/](report_files/output/)

All three required parts are complete. `trace` is syscall **23**, leaving `sync` at 22. Kernel messages use `printk`. The optional ungraded `sysinfo` extension is not included.

## Build and boot on Ubuntu

```sh
sudo apt update
sudo apt install build-essential gcc-riscv64-linux-gnu \
  binutils-riscv64-linux-gnu qemu-system-misc bc perl
cd xv6-riscv
make clean
make -j4 TOOLPREFIX=riscv64-linux-gnu- kernel/kernel fs.img
make qemu TOOLPREFIX=riscv64-linux-gnu- CPUS=3
```

At the xv6 shell:

```text
trace 32 grep hello README
trace 2147483647 grep hello README
trace 2 usertests forkforkfork
trace 65536 echo hi
trace 2129920 grep hello README
trace 0 echo quiet
echo untraced
tracetest
usertests -q
```

Exit QEMU with Ctrl-A followed by X. The required read results are **1023, 965, 453, 0** with the unchanged 2441-byte README. Process IDs and fork scheduling can differ between boots. The recorded tools were Ubuntu 24.04.5 LTS, GCC 13.3.0, and QEMU 8.2.2, running xv6 with three CPUs and 128 MiB RAM.

## Implementation layout

| File | Change |
| --- | --- |
| `kernel/syscall.h` | Assign `SYS_trace` number 23. |
| `user/user.h`, `user/usys.pl` | Declare the call and generate its ecall stub. |
| `user/trace.c` | Set the mask, then exec the requested command; follows the handout. |
| `Makefile` | Include `trace` and the additional `tracetest` regression program. |
| `kernel/proc.h` | Add per-process `trace_mask`. |
| `kernel/proc.c` | Initialize/clear the mask and copy it in `kfork`. |
| `kernel/sysproc.c` | Decode the mask argument and store it on the current process. |
| `kernel/syscall.c` | Register the handler, map names, and print selected calls after dispatch. |
| `user/tracetest.c` | Test inheritance, independent child/parent masks, and disabling. |

`exec` deliberately does not clear the mask. The print is after the handler, so its output reports the handler result. Non-returning `exit` does not reach that location. The unsigned mask shift preserves the mask's bit pattern; supported syscall numbers currently fit in an `int` mask.

## Recorded checkpoints and verification

`checkpoint1.txt` is the genuine intermediate run made after the user-side changes but before the handler was added. It shows `unknown sys call 23`, then `trace: failed`. It is historical evidence, not the expected behavior of the completed submission.

The final boot records each command separately plus a complete session. All required experiments passed; `usertests -q` ran **68 tests** and ended with `ALL TESTS PASSED`. Deliberate user traps in memory-protection tests are expected. The test did not produce a kernel panic. Source copies match the tested integrated files.

To repeat the automated final run on Ubuntu, from the repository root:

```sh
sudo apt install python3 python3-pexpect
python3 lab10/code/run_qemu.py final
python3 lab10/code/verify.py
```

The runner uses the existing tree, boots QEMU and waits for real shell prompts, records output, and exits the emulator. It does not reset sources to recreate historical checkpoints. Running it overwrites final experiment evidence and can take several minutes. The verifier also checks the retained baseline and Part 1 checkpoint, so keep those files. To recheck existing output without booting, run only `verify.py`.

The excerpts used by the report are explicitly marked as shortened; full fork and regression transcripts are retained. If rerunning and rebuilding the report, refresh the excerpts from `fork.txt` and `regression.txt`, and check any quoted PIDs against the new results.

## Applying the source changes elsewhere

The integrated tree is the primary submission. `code/` contains ten complete changed-source copies, and `code/trace.patch` includes both new C files. The patch is based on this repository's pre-Lab-10 xv6 tree (including Labs 2, 4, 6 and 8), not an arbitrary upstream version. From a matching repository root, apply it with `git apply lab10/code/trace.patch`; do not apply it again to the already-modified submission.

## Rebuild the report

With `pdflatex`, Latin Modern, microtype, needspace and listings installed:

```sh
cd lab10/report_files
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=.. report.tex
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=.. report.tex
rm -f ../report.aux ../report.log ../report.out ../report.toc
```

The title page, contents, experiment sections, handout Q&A, and conclusion follow the previous reports. Original execution tooling and logs are retained separately from the report prose.
