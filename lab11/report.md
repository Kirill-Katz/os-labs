# Lab 11 — The Race and the Semaphore

## Aim and environment

Demonstrate a shared-counter race, fix it with a mutex and a binary semaphore, then use a semaphore for signaling and limited-capacity admission. All four required parts are complete; `atomic.c` is the optional comparison.

The programs ran on Ubuntu 24.04.5 LTS (aarch64, glibc 2.39), using GCC 13.3.0. Every build used `-std=c11 -Wall -Wextra -Werror -O0 -pthread`, explicitly without optimization. Each configuration ran three times: 27 executions total. Raw output, GNU time measurements and machine-readable results are in `report_files/output/`.

The five required C sources use the shared `code/thread_utils.h` for pthread error handling and interrupted semaphore waits; submit that header with them. The intentional race remains unprotected. Compile-time definitions create the requested variants without leaving the submitted defaults broken:

- `sem.c`: default `SEM_START=1`; altered `-DSEM_START=2`.
- `order.c`: default `READY_START=0`; altered `-DREADY_START=1`.
- `parking.c`: default `PLACES=3`; altered `-DPLACES=1`.

## Part 1 — See the race

Recorded totals:

```text
counter = 1027667 (expected 2000000)
counter = 1029921 (expected 2000000)
counter = 1062160 (expected 2000000)
```

### Observe 1: counter++ looks like one step. Write the three steps the CPU really does.

Conceptually: load the shared counter into a register; add one to the register; store the register back to the shared counter. The ordinary C increment is not an atomic read-modify-write operation.

### Observe 2: Describe, with those steps, how two threads can lose one addition.

If the counter is 7, A can load 7 and B can also load 7 before either stores. Both compute 8. A stores 8, then B stores 8. Two attempted increments leave 8 instead of 9: one addition is lost.

### Observe 3: Why is the result different at every run?

Scheduling, preemption and overlapping loads/stores change which updates collide. The three recorded values differed. More precisely, the unsynchronized accesses form a C data race and therefore have undefined behavior. Neither different values on every run nor a result below 2,000,000 is universally guaranteed; an accidentally correct total does not prove safety. `-O0` makes the teaching example easier to observe but does not make it defined.

## Part 2 — Mutex and semaphore

Both corrected programs returned exactly 2,000,000 in all three runs. The mutex surrounds the full increment. The semaphore does the same with one initial permit, using wait before the critical section and post afterward.

### Observe 1: Run mutex and sem three times each. Is the answer always 2,000,000?

Yes, in all six recorded runs. With successful synchronization, only one thread updates the counter at a time; main joins both threads before printing.

```text
mutex: 2000000, 2000000, 2000000
sem:   2000000, 2000000, 2000000
```

### Observe 2: What would happen in sem.c with sem_init(&s, 0, 2)? Try it and explain.

The actual altered-start totals were:

```text
counter = 1791203 (expected 2000000)
counter = 1709203 (expected 2000000)
counter = 1844541 (expected 2000000)
```

Two permits allow both incrementing threads into the critical section simultaneously. The semaphore's internal count is synchronized, but the counter increment is not mutually exclusive, so lost updates return. This altered program again has a data race; these particular numbers are observations, not guaranteed outputs.

### Observe 3: Why is the locked version slower?

Each of two million increments now performs lock/unlock or wait/post operations. Contended synchronization and shared-cache-line transfers add overhead, and competing threads can block and wake. The unsafe race does not pay those costs but gives an invalid answer. These timings compare the submitted implementations, including their error-check helpers, not isolated primitive latency.

Measured end-to-end wall time in seconds (Python monotonic clock around each GNU time invocation; includes process startup and measurement overhead):

| Program | Run 1 | Run 2 | Run 3 | Median |
| --- | ---: | ---: | ---: | ---: |
| race | 0.004462 | 0.004463 | 0.004460 | 0.004462 |
| mutex | 0.055737 | 0.056001 | 0.058797 | 0.056001 |
| sem (1) | 0.131739 | 0.172545 | 0.142064 | 0.142064 |
| atomic (optional) | 0.049935 | 0.036728 | 0.031808 | 0.036728 |

Separate GNU time real/user/system results are retained in the `.time` files and `timings.csv`. Its coarse elapsed display printed 0.00 s for the race; that does not mean zero runtime. The observed median order was race < atomic < mutex < semaphore, but exact values and relative timing order are not universal. Summed user CPU time can exceed real time when two threads run on different CPUs.

A binary semaphore is useful as a lock here but is not identical to a mutex: it has no mutex-style ownership rule, and posting too often can raise its count above one.

## Part 3 — A semaphore as a signal

With initial value zero, all three runs produced:

```text
B: waiting for the message...
A: message written
B: I read "hello"
```

The writer fills `message` before posting. The reader waits before reading it. The synchronization orders and publishes the data; the one-second sleep only simulates work.

### Observe 1: Change the start value to 1, compile, run. What does B read now, and why?

All three altered-start runs produced:

```text
B: waiting for the message...
B: I read ""
A: message written
```

The initial permit lets B proceed before A posts. Here B read the initially empty global array, which is zero-initialized, while A was sleeping. The broken variant no longer guarantees that reading the message is ordered after writing it; other schedules can behave differently, and a sleep is not a synchronization mechanism.

### Observe 2: Put it back to 0. In one sentence: what does a semaphore that starts at 0 mean?

There is no permission to proceed yet: a waiter must wait until another thread posts a signal (or consume a signal already posted before it reached wait).

The submitted default is restored to zero through `READY_START=0`; the altered version is a separate binary.

## Part 4 — A semaphore as a counter: parking

One recorded default-capacity run:

```text
car 1 enters (inside: 1)
car 3 enters (inside: 2)
car 2 enters (inside: 3)
car 2 leaves (inside: 2)
car 4 enters (inside: 3)
car 1 leaves (inside: 2)
car 5 enters (inside: 3)
car 3 leaves (inside: 2)
car 6 enters (inside: 3)
car 4 leaves (inside: 2)
car 5 leaves (inside: 1)
car 6 leaves (inside: 0)
```

### Observe 1: What is the largest value of inside you see? Which line of code guarantees it?

The largest recorded value was **3**, in each of three default-capacity runs. `sem_wait(&places)` (called through `sem_wait_checked`) before admission, together with `sem_init(&places, 0, PLACES)` and one balanced post after each departure, enforces the limit. Only three permits exist. The mutex protects updates to `inside` and the associated print; it does not limit the number of parked cars because it is released while they sleep.

### Observe 2: Set PLACES to 1. What does the semaphore become?

A binary semaphore acting as a one-at-a-time admission lock for the parking interval. All three altered-capacity runs had maximum occupancy one. Six cars still entered and left, and final occupancy was zero. Runtime was about six seconds instead of two: six sequential one-second stays instead of roughly two waves of three cars. This does not add mutex ownership semantics to the semaphore or promise FIFO admission.

## Optional atomic counter

`atomic_fetch_add` updates an `atomic_long` as an indivisible read-modify-write at the C memory-model level. All three runs reached 2,000,000 without an explicit mutex or semaphore. It was faster than the locked variants by median on this machine, but C does not promise one hardware instruction or lock-free implementation for every atomic type and platform. Atomics solve this single-counter operation; they do not automatically protect a multi-variable critical section.

## Verification and conclusion

All **389 assertions across 27 executions** passed. Checks cover successful execution, exact corrected totals, observed race failures, signal ordering, and every parking event. The parking verifier tracks car IDs, requires each car to enter and leave exactly once, checks every reported occupancy against the active set, enforces capacity, and requires final occupancy zero. It does not assume a fixed arrival order or enforce timing thresholds. The broken variants are evaluated as observations, not correctness guarantees.

A semaphore's initial count determines its role: one for mutual exclusion, zero for a readiness signal, or a resource count for bounded admission. A mutex protects a critical section; synchronization also establishes ordering and visibility. The experiments demonstrate why correctness must be established before comparing speed.
