# Lab 8 — Process calls and pipes inside xv6

- **Report:** [report.pdf](report.pdf) and the required [notes.md](notes.md).
- **Report source and assignment:** [report_files/report.tex](report_files/report.tex) and [lab_description.docx](lab_description.docx).
- **Code:** [code/user/run.c](code/user/run.c), [code/user/pingpong.c](code/user/pingpong.c), and [code/Makefile](code/Makefile).

The programs are integrated in [xv6-riscv](../xv6-riscv/). Build the image with `make -C ../xv6-riscv fs.img` and boot from that directory with `make qemu`. The final `run.c` executes `echo`; the report records the requested temporary `ls` and failed-`exec` tests.
