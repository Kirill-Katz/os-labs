# Lab 9 — Watching System Calls with strace

- **Submission:** [report.pdf](report.pdf)
- **Observe answers:** [report.md](report.md)
- **Source and supporting scripts:** [code/](code/)
- **Editable report and assignment:** [report_files/](report_files/)
- **Original execution evidence:** [report_files/output/](report_files/output/)

The experiments ran on Ubuntu 24.04.5 LTS (aarch64), using GCC 13.3.0 and strace 6.8. The supplied handout has only two pages: Part 3 appears in the overview but has no detailed instructions. The report explicitly labels its write-counting experiment as a supplement.

## Run the core exercise on Ubuntu

Install the tools:

```sh
sudo apt update
sudo apt install gcc libc6-dev strace
```

From the repository root:

```sh
gcc -std=c11 -Wall -Wextra -Werror -O0 -g \
  -o /tmp/syscalls lab9/code/syscalls.c
mkdir -p /tmp/lab9-run
cd /tmp/lab9-run
/tmp/syscalls
strace -f -e trace=openat,read,write,close ls -l
strace -e trace=openat,write,read,close /tmp/syscalls
strace -c -e trace=write /tmp/syscalls
```

The program creates or truncates `note.txt` in its current working directory. Use a disposable directory as above to avoid overwriting an existing file.

To capture output like the recorded file-I/O experiment:

```sh
strace -e trace=openat,write,read,close -o syscalls.trace \
  /tmp/syscalls > syscalls.stdout
strace -c -e trace=write -o write.summary \
  /tmp/syscalls > count.stdout
```

Redirecting stdout to a regular file makes libc buffer the diagnostics; this explains the recorded two-write result. Terminal line buffering can produce a different call count. Counts also depend on architecture, library versions, configuration, and directory contents.

## Verification

The retained execution evidence includes 15 passing assertions: expected program output and file bytes, ordered file calls, independent write-count agreement, truncation, and representative open/write failures. Original logs and supporting execution tooling are retained unchanged. The supporting automated runner uses `/work` as its working root; the commands above are the standalone Ubuntu instructions.

The program checks errors, retries interrupted reads/writes, and handles short writes. It performs one bounded read of the tiny local file, following the handout; it is not a general file copier.

## Rebuild the PDF

With LaTeX (`pdflatex`, Latin Modern, microtype, needspace, listings, booktabs) installed:

```sh
cd lab9/report_files
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=.. report.tex
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=.. report.tex
rm -f ../report.aux ../report.log ../report.out ../report.toc
```

Run from `report_files/` so relative trace inputs resolve. The title page follows Labs 7 and 8.
