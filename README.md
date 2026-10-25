# Operating Systems laboratories

Every lab uses the same layout:

```text
labN/
├── code/           # source files, scripts, and lab-specific xv6 Makefile
├── report_files/   # editable report.tex, assignment, figures, and recorded output
└── report.pdf      # the submission PDF (Labs 1–5)
```

The root `report.pdf` is the file to submit. Lab 6 does not have a report yet; no empty or invented PDF has been added.

| Lab | Report | Code | Status |
| --- | --- | --- | --- |
| 1 | [report.pdf](lab1/report.pdf) | [code/](lab1/code/) | Report and Linux command script present. The original Lab 1 handout is unavailable here. |
| 2 | [report.pdf](lab2/report.pdf) | [code/](lab2/code/) | `sleep.c` uses `pause()` and builds in the integrated xv6 tree; its older report screenshot needs replacement. |
| 3 | [report.pdf](lab3/report.pdf) | [code/](lab3/code/) | Scripts pass the requested checks; the report still lacks screenshots for Parts 2–5. |
| 4 | [report.pdf](lab4/report.pdf) | [code/](lab4/code/) | xv6 and Linux argument programs are present. |
| 5 | [report.pdf](lab5/report.pdf) | [code/](lab5/code/) | No C program was required by the local handout; recorded command output is in `report_files/`. |
| 6 | No report yet | [code/](lab6/code/) | `mystat.c` and `find.c` build and run in xv6; the report and personal evidence remain to be written. |

The [integrated xv6 tree](xv6-riscv/) contains the Lab 2, 4, and 6 programs in `user/` and its `UPROGS`. See [integration details](xv6-riscv/LAB_INTEGRATION.md). The Makefiles under individual `code/` folders are submission copies for their respective lab, intended for the root of an xv6 checkout.

## Remaining submission work

- Replace the Lab 2 screenshot with a current capture matching `pause()`.
- Add Lab 3 screenshots from the course VM for Parts 2–5.
- Create Lab 6's report with your own output/screenshots, Observe answers, and conclusions.
- The announcement names `run.c`, `redirect.c`, `pipeline.c`, `zombie.c`, and `pingpong.c`. The first four and a custom `pingpong.c` are absent from the lab submissions; the local handouts only mention `pingpong.c` as an optional Lab 2 exercise. Check the relevant course handouts before assigning them to a lab.
- Review all screenshots and prose for originality. Local files alone cannot establish whether another student's submission uses the same material.

The old Lab 1 handout was removed because it was an exact duplicate of Lab 2's handout. Git history has not been rewritten.
