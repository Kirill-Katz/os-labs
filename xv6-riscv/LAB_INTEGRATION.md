# Integrated OS lab programs

This is a vendored copy of [MIT xv6-riscv](https://github.com/mit-pdos/xv6-riscv), upstream commit `f780d7850765d74cbdcd1fff4b822d8829f7c9bd` (15 October 2026). The upstream license is retained in [LICENSE](LICENSE). The clone's nested `.git` directory was removed so this source is included in the parent OS labs repository; the parent repository's history was not rewritten.

| Lab | Program in this xv6 tree | Source of the integration |
| --- | --- | --- |
| 2 and 4 | [`user/sleep.c`](user/sleep.c) | [`../lab4/code/user/sleep.c`](../lab4/code/user/sleep.c), using `pause()` on current xv6 |
| 4 | [`user/args.c`](user/args.c) | [`../lab4/code/user/args.c`](../lab4/code/user/args.c) |
| 6 | [`user/mystat.c`](user/mystat.c) | [`../lab6/code/user/mystat.c`](../lab6/code/user/mystat.c) |
| 6 | [`user/find.c`](user/find.c) | [`../lab6/code/user/find.c`](../lab6/code/user/find.c) |

The [`Makefile`](Makefile) adds `_sleep`, `_args`, `_mystat`, and `_find` to `UPROGS` while preserving the cloned upstream build settings. Lab 1, Lab 3, and Lab 5 are Linux/Bash exercises and do not modify xv6.

Build from this directory with `gmake` on macOS or `make` in the course Linux VM. Use `gmake qemu`/`make qemu` to boot. The corresponding lab folders hold submission copies in `code/`, editable materials in `report_files/`, and `report.pdf` at the lab root when a report exists.

## Verified locally

On 25 October 2026, `gmake -j4` built the kernel and all user programs with `riscv64-elf-gcc`. `gmake qemu` booted the same tree. In the xv6 shell, `sleep 3` returned normally, `sleep` printed its usage error, `args one two` showed three arguments, `mystat README . console` printed file metadata, and `find . r2` found three paths after creating the handout test tree. `find a b` returned `a/b`, and `mystat` reported an error for a nonexistent path. These checks do not replace the screenshots and personal analysis required in the lab reports.
