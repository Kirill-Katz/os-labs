// Focused Lab 13 regression tests. Only the parent prints successful results.
#include "kernel/types.h"
#include "user/user.h"

static void
check(int ok, char *message)
{
  if (!ok) {
    fprintf(2, "semcheck: FAIL: %s\n", message);
    exit(1);
  }
}

static void
joinok(void)
{
  int status = -99;
  check(wait(&status) >= 0 && status == 0, "child exit status");
}

int
main(void)
{
  for (int id = -1; id <= 8; id += 9) {
    check(sem_init(id, 0) == -1, "invalid init ID");
    check(sem_down(id) == -1, "invalid down ID");
    check(sem_up(id) == -1, "invalid up ID");
  }
  check(sem_init(0, -1) == -1, "negative initial value");
  for (int id = 0; id < 8; id++) {
    check(sem_init(id, 0) == 0, "initialize valid ID");
    check(sem_up(id) == 0 && sem_down(id) == 0, "valid ID token round trip");
  }
  printf("semcheck: IDs and initial values PASS\n");

  check(sem_init(7, 0x7fffffff) == 0, "maximum count");
  check(sem_up(7) == -1, "reject count overflow");
  check(sem_down(7) == 0 && sem_up(7) == 0, "maximum count preserved");
  check(sem_init(7, 0) == 0, "restore count");
  printf("semcheck: count overflow guard PASS\n");

  int ready[2], done[2];
  char byte = 'x';
  check(pipe(ready) == 0 && pipe(done) == 0, "pipes");
  check(sem_init(4, 0) == 0, "multiwaiter init");
  for (int i = 0; i < 6; i++) {
    int pid = fork();
    check(pid >= 0, "multiwaiter fork");
    if (pid == 0) {
      close(ready[0]);
      close(done[0]);
      check(write(ready[1], &byte, 1) == 1, "announce waiter");
      check(sem_down(4) == 0, "wait for permit");
      check(write(done[1], &byte, 1) == 1, "announce completion");
      close(ready[1]);
      close(done[1]);
      exit(0);
    }
  }
  close(ready[1]);
  close(done[1]);
  for (int i = 0; i < 6; i++)
    check(read(ready[0], &byte, 1) == 1, "all waiters started");
  pause(3);
  for (int i = 0; i < 6; i++) {
    check(sem_up(4) == 0, "release a permit");
    check(read(done[0], &byte, 1) == 1, "one waiter completes");
  }
  close(ready[0]);
  close(done[0]);
  for (int i = 0; i < 6; i++)
    joinok();
  printf("semcheck: six waiters and six posts PASS\n");

  check(sem_init(4, 1) == 0 && sem_init(5, 0) == 0, "stress init");
  int pid = fork();
  check(pid >= 0, "stress fork");
  if (pid == 0) {
    for (int i = 0; i < 1000; i++)
      check(sem_down(5) == 0 && sem_up(4) == 0, "child handoff");
    exit(0);
  }
  for (int i = 0; i < 1000; i++)
    check(sem_down(4) == 0 && sem_up(5) == 0, "parent handoff");
  joinok();
  printf("semcheck: 1000 ping-pong handoffs PASS\n");

  for (int i = 0; i < 20; i++) {
    check(pipe(ready) == 0 && sem_init(6, 0) == 0, "kill init");
    pid = fork();
    check(pid >= 0, "kill fork");
    if (pid == 0) {
      close(ready[0]);
      check(write(ready[1], &byte, 1) == 1, "announce kill waiter");
      close(ready[1]);
      sem_down(6);
      exit(2); // A non-killed success on an empty semaphore is an error.
    }
    close(ready[1]);
    check(read(ready[0], &byte, 1) == 1, "kill waiter started");
    close(ready[0]);
    if (i & 1)
      pause(1); // Alternate immediate kills and already-blocked waiters.
    check(kill(pid) == 0, "kill waiter");
    int status = 0;
    check(wait(&status) == pid && status == -1, "killed waiter reaped");
  }
  printf("semcheck: 20 immediate/blocked waiter kills PASS\n");
  printf("semcheck: ALL TESTS PASSED\n");
  exit(0);
}
