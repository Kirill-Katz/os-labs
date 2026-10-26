# Lab 7 — Processes, redirection, and a pipe

- **Report:** [report.pdf](report.pdf) and the required [report.md](report.md).
- **Report source and assignment:** [report_files/report.tex](report_files/report.tex) and [lab_description.docx](lab_description.docx).
- **Code:** [code/](code/) with `run.c`, `zombie.c`, `redirect.c`, and `pipeline.c`.

These are POSIX programs for the host OS, not xv6 user programs. The source files are also mirrored in [xv6-riscv/lab7-linux](../xv6-riscv/lab7-linux/) without adding them to xv6's `UPROGS`.

Build each program from `code/` with `gcc -std=c11 -Wall -Wextra -Werror -o NAME NAME.c`. Run `redirect` in a temporary directory if you do not want it to create `out.txt` in `code/`. The report records the outputs and answers for all four required parts.
