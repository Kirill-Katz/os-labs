# Lab 12 — Producer, Consumer and the Other Tools

## Aim and environment

Combine semaphores, mutexes and condition variables to implement a bounded FIFO, coordinate message readiness, admit concurrent readers while excluding writers, and create then remove a lock-order deadlock. All four required parts are complete.

Experiments ran on Ubuntu 24.04.5 LTS (aarch64), using GCC 13.3.0 and POSIX threads. Every configuration was compiled with `-std=c11 -Wall -Wextra -Werror -O0 -pthread`. Eight configurations were executed **27 times** in total, including the ten original no-sleep deadlock runs. Raw output, exit codes and elapsed times are in `report_files/output/`.

The submitted defaults are the correct versions of `prodcons.c`, `condvar.c`, `readers.c` and `deadlock.c`. The companion `thread_utils.h` handles pthread error codes and semaphore errors, including retrying `sem_wait` after `EINTR`. Submit that header with the four C files. All worker threads are joined before synchronization objects are destroyed. Output is line buffered so events remain visible when a deliberately broken run is terminated by `timeout`.

Broken configurations are separate compile-time variants, not the submitted defaults:

- `prodcons.c -DBAD_LOCK_ORDER=1`: producer locks before waiting for an empty slot.
- `condvar.c -DUSE_IF=1`: replace the predicate loop with a one-time test.
- `deadlock.c -DOPPOSITE_ORDER=1`: original opposite lock ordering, with sleeps.
- `deadlock.c -DOPPOSITE_ORDER=1 -DDELAY_SECONDS=0`: original opposite ordering with both sleeps compiled out.

## Part 1 — Producer and consumer

The buffer holds four items. `empty` starts at 4, `full` at 0; the mutex protects the buffer, indices and occupancy. The producer waits for an empty permit **before** locking the mutex. The consumer waits for a full permit before locking. After updating the buffer, each unlocks and posts the opposite semaphore.

One actual run:

```text
put 1    (in buffer: 1)
put 2    (in buffer: 2)
put 3    (in buffer: 3)
put 4    (in buffer: 4)
            take 1   (in buffer: 3)
put 5    (in buffer: 4)
            take 2   (in buffer: 3)
put 6    (in buffer: 4)
            take 3   (in buffer: 3)
put 7    (in buffer: 4)
            take 4   (in buffer: 3)
put 8    (in buffer: 4)
            take 5   (in buffer: 3)
            take 6   (in buffer: 2)
            take 7   (in buffer: 1)
            take 8   (in buffer: 0)
```

All three correct runs produced and consumed exactly items 1–8 in FIFO order, reached maximum occupancy 4, and ended empty. The circular indices wrap with `% SIZE`. A different scheduling interleaving is valid if those invariants hold. Kernel pipes share the bounded producer/consumer idea, but their implementation need not use these exact POSIX objects.

### Observe 1: The producer is fast, yet “in buffer” never goes above 4. Which call stops it?

`sem_wait(&empty)`, called through `sem_wait_checked(&empty)`, consumes one free-slot permit. With no permit available it blocks until the consumer posts `empty`. Initialization to `SIZE=4` and balanced posts enforce the capacity; the mutex alone would not prevent overflow.

### Observe 2: Who waits at the start: the consumer or the producer? Which call makes it wait?

An initially scheduled consumer waits in `sem_wait(&full)` because `full` starts at zero. The producer initially has four empty permits. If the producer runs before the consumer reaches wait, a posted full permit may already be available; this does not change the initial empty-buffer condition.

### Observe 3: In producer(), lock the mutex BEFORE sem_wait(&empty). What happens when the buffer is full, and why?

The altered build produced:

```text
$ timeout 5 ./prodcons_bad
put 1    (in buffer: 1)
put 2    (in buffer: 2)
put 3    (in buffer: 3)
put 4    (in buffer: 4)
exit code: 124
```

The producer holds the mutex and waits for an empty slot. The consumer needs that mutex to remove an item before it can post an empty permit. Neither can make progress: producer → free-slot permit → consumer → mutex → producer. The test was stopped after five seconds; the submitted default restores wait-before-lock. The general rule is not to hold a resource needed by the thread that must satisfy your wait condition.

## Part 2 — A condition variable

The writer holds `lock` while copying `hello`, setting `ready=1`, announcing completion and signaling `changed`. The reader holds the same mutex while checking `ready`; `pthread_cond_wait` atomically releases the mutex and waits, then reacquires it before returning.

All three correct runs produced:

```text
B: not ready, I sleep
A: message written
B: I read "hello"
```

### Observe 1: In Lab 11 the semaphore remembered that the message was ready. Here, which variable remembers it?

The integer predicate `ready`, protected by `lock`. A condition-variable signal is not a stored permit. If the writer finishes before the reader starts waiting, the reader sees `ready==1` and does not sleep, even if the signal itself had no waiter.

### Observe 2: Replace while (!ready) with if (!ready), compile, run. Does it still work here?

Yes, all three altered `if` runs also printed `hello` after the writer announcement. This one-reader, one-writer schedule did not expose an unwanted wakeup. Passing these runs does not make `if` the correct general pattern; the submitted default remains `while`.

### Observe 3: Why do we write while? Give one reason a thread can wake up and still find ready == 0.

POSIX condition waits may return spuriously without the desired predicate becoming true. More generally, a signal only means “something may have changed”; with multiple consumers another thread may consume the resource before this waiter reacquires the mutex. A `while` loop rechecks the actual predicate under the lock and sleeps again if necessary. This run did not force or claim to observe a spurious wakeup.

## Part 3 — Readers and writers

The first reader acquires `room`; the last reader releases it. `rlock` protects all updates to `readers`. A writer holds `room` through its entire update and simulated work interval.

The handout prints `readers` outside `rlock`, which would race with other readers updating it. The submitted program moves that print into the protected region. It also adds reader/writer departure lines and a final summary, so the retained verifier can reconstruct whole active intervals rather than assume a printed “alone” label proves exclusivity. The short printing region does not cover the 200 ms reading interval, so readers still overlap.

One actual run:

```text
writer 1 writes 10 (alone)
writer 1 leaves
reader 1 reads 10 (readers inside: 1)
reader 2 reads 10 (readers inside: 2)
reader 3 reads 10 (readers inside: 3)
reader 2 leaves (readers inside: 2)
reader 1 leaves (readers inside: 1)
reader 3 leaves (readers inside: 0)
writer 2 writes 20 (alone)
writer 2 leaves
final value: 20; readers remaining: 0
```

All three runs observed three overlapping readers and no reader/writer or writer/writer overlap. Final value was 20 and no readers remained. Writer IDs and scheduling order are not general guarantees; two exclusive additions of 10 must produce 20.

### Observe 1: Three readers are inside at once, but a writer is always alone. Which two lines of reader() make that possible?

`if (++readers == 1) sem_wait(&room);` and `if (--readers == 0) sem_post(&room);` (through checked helpers in the submission). Only the first reader takes `room`; only the last releases it, so the reader group holds the room while individual readers overlap. Every writer must acquire that same room permit.

### Observe 2: Why does readers need its own lock, rlock? What could go wrong without it?

Increment/decrement and first/last-reader decisions must be atomic as a group. Without `rlock`, increments can be lost or two readers can both make inconsistent “first” decisions; the last-reader decision can also fail or release the room too early. That can block writers forever or admit a writer while a reader is still active. The diagnostic read of the count must be protected too.

### Observe 3: Readers keep arriving without a pause. What happens to writer 2?

This is a **reader-preference** solution. If new readers continuously join an active group so the count never reaches zero, `room` stays held and a writer may wait indefinitely: **writer starvation**. This is not a circular-wait deadlock, because readers can continue making progress. The finite test lets both writers finish; it does not demonstrate a fairness guarantee or measure starvation under an infinite workload.

## Part 4 — Build a deadlock, then remove it

### Original, with sleeps

```text
$ timeout 5 ./deadlock_original
one: I have A, I want B
two: I have B, I want A
exit code: 124
```

Neither “I have both” nor `done` appeared. Code inspection and the two ownership messages establish the cycle; the timeout bounds the experiment, rather than being the sole evidence of a deadlock.

### Fixed submission

Both workers acquire **A then B** and release **B then A**. One recorded run was:

```text
one: I have A, I want B
one: I have both
two: I have A, I want B
two: I have both
done
exit code: 0
```

The second thread's message now accurately says it holds A; the handout's fixed sample retains an outdated “I have B” message. All three fixed runs completed normally. Either worker may acquire A first in another schedule.

### Observe 1: In the stuck run, who holds which mutex, and what is each waiting for? Draw the circle.

Thread one holds A and waits for B. Thread two holds B and waits for A:

```text
one --waits for--> B --held by--> two
 ^                                  |
 |                                  v
 A <------------waits for------------+
 (A is held by one)
```

Equivalently, the wait-for graph is `one → two → one`.

### Observe 2: Remove both sleeps from the ORIGINAL version and run it ten times. Does it still always hang? Why is that worse, not better?

No. The actual exit-code sequence was:

| Run | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Exit code | 124 | 0 | 124 | 0 | 0 | 124 | 124 | 124 | 0 | 0 |

**Five completed and five timed out.** Removing the sleeps changes the timing, not the opposite lock order. A thread can sometimes acquire both locks before the other runs; other schedules still establish the cycle. This intermittent bug is worse to diagnose because successful tests can hide it. These counts describe ten particular executions, not a measured probability or a portable failure rate.

### Observe 3: In one sentence, why can taking the locks in the same order never deadlock?

For these two locks, requiring every worker to acquire A before B prevents a circular wait, because no worker can hold B while waiting to acquire A.

This is a statement about the demonstrated lock-order cycle, not a claim that a whole program with unrelated waits can never deadlock.

## Verification and conclusion

All **253 assertions across 27 executions** passed. The verifier reconstructed the FIFO and checked each occupancy and item order, checked writer-before-reader message output in the observed condition-variable runs, reconstructed reader/writer active intervals and values, checked both deliberate timeout cases and fixed completion, and retained all ten no-sleep outcomes. No fixed car/thread schedule or timing threshold is treated as a correctness guarantee. Exit 124 is expected only in the deliberately broken experiments; an unexpected timeout in a correct program fails verification.

Counting semaphores express available resources; a mutex protects the associated state. A condition variable is paired with a protected predicate, not used as a stored readiness bit. A reader-preference group can admit concurrent readers without guaranteeing writer fairness. Finally, consistent lock ordering removes a circular-wait bug; removing delays only makes it intermittent.
