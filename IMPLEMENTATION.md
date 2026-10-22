# Implementation files by completed lab

| Lab | Files | Purpose |
| --- | --- | --- |
| 1 | [`os-lab1/commands.sh`](os-lab1/commands.sh) | Reconstructs the interactive Linux commands documented in the report. Lab 1 did not have a C program. |
| 2 | [`os-lab2/user/sleep.c`](os-lab2/user/sleep.c) | The xv6 user program printed in the report. Add `$U/_sleep` to the xv6 `UPROGS` list when building it. |
| 3 | [`os-lab3/generate_access_log.sh`](os-lab3/generate_access_log.sh), [`os-lab3/oneliners.sh`](os-lab3/oneliners.sh), [`os-lab3/report.sh`](os-lab3/report.sh) | Generates the sample log, answers the text-filter questions, and summarizes failures. Run the generator from the lab directory. |
| 4 | [`os-lab4/sleep.c`](os-lab4/sleep.c), [`os-lab4/args.c`](os-lab4/args.c), [`os-lab4/args_linux.c`](os-lab4/args_linux.c), [`os-lab4/Makefile`](os-lab4/Makefile), [`os-lab4/lab4_run_guest.sh`](os-lab4/lab4_run_guest.sh) | xv6 and Linux programs, xv6 build configuration, and the guest command runner. The `user/` copies are the xv6 placement; `resources/sh.c` is the inspected xv6 shell source. |
| 5 | [`os-lab5/run_lab5_guest.sh`](os-lab5/run_lab5_guest.sh) | Runs the filesystem and permission experiments that produced `lab5-results.txt`. Lab 5 did not have a C program. |

Lab 6 has an assignment description but no completed report or implementation yet.
