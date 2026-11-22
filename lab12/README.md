# Lab 12 — Producer, Consumer and the Other Tools

- **Formatted report:** [report.pdf](report.pdf)
- **Required report and all twelve Observe answers:** [report.md](report.md)
- **Four required C programs and companion header:** [code/](code/)
- **LaTeX source and original assignment:** [report_files/](report_files/)
- **Original outputs, exit codes and verification:** [report_files/output/](report_files/output/)

All four required parts are complete. The programs ran on Ubuntu 24.04.5 LTS (aarch64), using GCC 13.3.0 and POSIX threads. The correct versions are submitted as the defaults, including the **fixed** `deadlock.c`.

## Build and run on Ubuntu

```sh
sudo apt update
sudo apt install build-essential python3 coreutils
mkdir -p /tmp/os-lab12
# From the repository root:
for name in prodcons condvar readers deadlock; do
  gcc -std=c11 -Wall -Wextra -Werror -O0 -pthread \
    -o "/tmp/os-lab12/$name" "lab12/code/$name.c"
done
/tmp/os-lab12/prodcons
/tmp/os-lab12/condvar
/tmp/os-lab12/readers
timeout 5 /tmp/os-lab12/deadlock
echo "exit code: $?"
```

Keep **`thread_utils.h` alongside the C sources** when copying them. It correctly handles pthread return codes and retries interrupted semaphore waits. The sources line-buffer stdout so the final printed events survive deliberate timeout termination. All normal runs join their workers and destroy the synchronization objects.

## Required altered configurations

From the repository root:

```sh
gcc -std=c11 -Wall -Wextra -Werror -O0 -pthread -DBAD_LOCK_ORDER=1 \
  -o /tmp/os-lab12/prodcons_bad lab12/code/prodcons.c
gcc -std=c11 -Wall -Wextra -Werror -O0 -pthread -DUSE_IF=1 \
  -o /tmp/os-lab12/condvar_if lab12/code/condvar.c
gcc -std=c11 -Wall -Wextra -Werror -O0 -pthread -DOPPOSITE_ORDER=1 \
  -o /tmp/os-lab12/deadlock_original lab12/code/deadlock.c
gcc -std=c11 -Wall -Wextra -Werror -O0 -pthread \
  -DOPPOSITE_ORDER=1 -DDELAY_SECONDS=0 \
  -o /tmp/os-lab12/deadlock_nosleep lab12/code/deadlock.c

timeout 5 /tmp/os-lab12/prodcons_bad; echo "exit code: $?"
/tmp/os-lab12/condvar_if
timeout 5 /tmp/os-lab12/deadlock_original; echo "exit code: $?"
for i in $(seq 1 10); do
  timeout 5 /tmp/os-lab12/deadlock_nosleep
  echo "run $i, exit code: $?"
done
```

Do not run deliberately broken versions without a timeout or another way to stop them. Exit **124** means the timeout expired; it is expected for the captured broken producer and original sleeping deadlock. It is not an expected outcome for the submitted defaults. The two original sleep calls are compiled out entirely in the no-sleep variant, rather than replaced by `sleep(0)`.

## Implementation notes

- **Producer/consumer:** `empty`/`full` enforce resource availability; the mutex protects the buffer and indices. Wait for a permit before locking the mutex. The altered ordering can block while holding the mutex needed by the consumer to produce a free slot.
- **Condition variable:** `ready` is the remembered predicate. Wait atomically releases the mutex and reacquires it before return; the default uses `while` to recheck the predicate. Three successful `if` runs do not establish that a one-time test is generally safe.
- **Readers/writers:** the first reader takes `room`, the last releases it, and writers acquire that same permit. The count's printed snapshot stays under `rlock`, fixing an unprotected read in the handout. Added departure records make reader/writer interval checks possible. Reading intervals still occur outside `rlock`, so readers overlap. This is reader preference, not a starvation-free algorithm.
- **Deadlock:** the default acquires A then B in both workers and releases B then A. The second worker's message is corrected to say it holds A. Original opposite-order behavior remains available only as an explicit experimental build.

## Automated evidence and verification

From the repository root on Ubuntu:

```sh
python3 lab12/code/run.py
python3 lab12/code/verify.py
```

The runner builds eight configurations and runs **27 executions**: three per default program, three `if` variants, one broken-producer run, one original sleeping deadlock, and ten no-sleep original runs. Each process is bounded by GNU `timeout` (five seconds, with a one-second forced-kill fallback); an outer subprocess timeout catches supervision failures. Running the script overwrites experiment results and may take around a minute or more, depending on how many no-sleep runs hang.

The retained session passed **253 assertions**. The verifier reconstructs FIFO state, reader/writer active intervals, and values without assuming a particular schedule. It checks raw output against `runs.json`, validates normal completion or the intended timeout outcomes, and records peak occupancy/concurrency in `observations.txt`. The no-sleep experiment produced **5 successes and 5 timeouts**; these are ten observations, not an estimated universal failure rate.

Raw output and original environment tooling are retained. `runs.json` and `outcomes.csv` contain actual exit codes and monotonic end-to-end elapsed times, including timeout-wrapper/process startup overhead. No arbitrary performance threshold is used to prove correctness. Expected ownership messages plus the locking code explain the deadlock; timeout by itself would not identify the cause of a hang.

If rerunning, update the report's quoted observations and no-sleep table against the new evidence before rebuilding. Source defaults remain correct throughout; there is no need to edit and restore them manually.

## Rebuild the PDF

With `pdflatex`, Latin Modern, microtype, needspace, booktabs, amsmath and listings installed:

```sh
cd lab12/report_files
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=.. report.tex
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=.. report.tex
rm -f ../report.aux ../report.log ../report.out ../report.toc
```

The title page, table of contents, experiment sections, complete Observe Q&A, and conclusion follow previous laboratory reports. The handout requests a push to the course repository; a local commit does not perform that push.
