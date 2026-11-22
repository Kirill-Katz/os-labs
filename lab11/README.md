# Lab 11 — The Race and the Semaphore

- **Submission report:** [report.pdf](report.pdf)
- **Required Markdown report and all Observe answers:** [report.md](report.md)
- **Required programs and companion header:** [code/](code/)
- **Editable LaTeX report and handout:** [report_files/](report_files/)
- **Original results and timing evidence:** [report_files/output/](report_files/output/)

All four required parts are complete. `atomic.c` is the optional atomic-counter comparison. The actual experiment used Ubuntu 24.04.5 LTS (aarch64, glibc 2.39), with GCC 13.3.0, no optimization, and POSIX threads.

## Build on Ubuntu

```sh
sudo apt update
sudo apt install build-essential python3 time
mkdir -p /tmp/os-lab11
# From the repository root:
for name in race mutex sem order parking atomic; do
  gcc -std=c11 -Wall -Wextra -Werror -O0 -pthread \
    -o "/tmp/os-lab11/$name" "lab11/code/$name.c"
done
```

**Keep `thread_utils.h` alongside the C sources** if copying them to a separate submission directory. It checks pthread return codes, handles semaphore errors, and retries interrupted waits. The handout's five required `.c` files are all present; the header and optional `.c` file are additional submission files.

Run the programs:

```sh
/tmp/os-lab11/race
/tmp/os-lab11/mutex
/tmp/os-lab11/sem
/tmp/os-lab11/order
/tmp/os-lab11/parking
/tmp/os-lab11/atomic
/usr/bin/time /tmp/os-lab11/race
/usr/bin/time /tmp/os-lab11/mutex
/usr/bin/time /tmp/os-lab11/sem
```

Repeat each counter at least three times. `race.c` deliberately contains a C data race: a correct-looking total on one run is not proof of safety. The correct versions join both workers before printing and should return 2,000,000 when all operations succeed. `-O0` is explicit and required for these teaching experiments; it does not make a data race defined behavior.

## Requested variations

The submitted defaults stay at `SEM_START=1`, `READY_START=0`, and `PLACES=3`. Compile separate altered binaries:

```sh
gcc -std=c11 -Wall -Wextra -Werror -O0 -pthread -DSEM_START=2 \
  -o /tmp/os-lab11/sem_two lab11/code/sem.c
gcc -std=c11 -Wall -Wextra -Werror -O0 -pthread -DREADY_START=1 \
  -o /tmp/os-lab11/order_one lab11/code/order.c
gcc -std=c11 -Wall -Wextra -Werror -O0 -pthread -DPLACES=1 \
  -o /tmp/os-lab11/parking_one lab11/code/parking.c
/tmp/os-lab11/sem_two
/tmp/os-lab11/order_one
/tmp/os-lab11/parking_one
```

The two-permit counter loses mutual exclusion. The initially available signal permit removes the required writer-before-reader ordering; all recorded altered runs read the initially empty global buffer. One parking permit admits only one car at a time. Car order can differ; the semaphore is not a FIFO fairness guarantee or a mutex with an owner.

## Automated runs and evidence

From the repository root on Ubuntu:

```sh
python3 lab11/code/run.py
python3 lab11/code/verify.py
```

The runner compiles all nine configurations, runs each three times, uses a 30-second timeout per execution, and retains raw stdout, stderr, GNU time records, a CSV, and machine-readable `runs.json`. If all first three unsafe-counter runs happen to return 2,000,000, it retries that configuration up to 20 runs rather than fabricating a wrong value. This session needed no retries: **27 executions, 389 passing assertions**.

The verifier checks results and event invariants, not arbitrary runtime limits or fixed scheduling. It tracks each parking car, validates every occupancy against the active set, enforces capacity and final emptiness, and requires every car to enter and leave once. It treats broken configurations as observed experiments rather than universally predictable behavior. The original logs and supporting environment tooling are preserved.

Rerunning overwrites the recorded results and timings. If rebuilding the report from a new experiment, also refresh the LaTeX and Markdown timing tables from `timings.csv`/`runs.json`, update the quoted observations, and review all numbers against the new output. The PDF's other trace listings read directly from their saved output files.

The high-resolution wall measurements include the external time wrapper and process startup. GNU time's real/user/system output is stored separately. The observations compare complete teaching implementations, including error checks, not pure synchronization primitive costs; exact values and timing rankings are not portable.

## Rebuild the PDF

With `pdflatex`, Latin Modern, microtype, needspace, booktabs, amsmath and listings installed:

```sh
cd lab11/report_files
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=.. report.tex
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=.. report.tex
rm -f ../report.aux ../report.log ../report.out ../report.toc
```

The title page and section structure follow the preceding labs. The required Markdown report remains a standalone deliverable. The assignment asks for submission through the course Git repository; a local commit does not itself push to that repository.
