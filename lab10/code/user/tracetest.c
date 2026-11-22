// Regression test: inherit a mask, then change it independently in the child.
#include "kernel/types.h"
#include "kernel/stat.h"
#include "kernel/syscall.h"
#include "user/user.h"

int
main(void)
{
  int parent = getpid();
  printf("tracetest: parent %d\n", parent);
  if (trace(1 << SYS_getpid) < 0)
    exit(1);
  getpid();
  int child = fork();
  if (child < 0)
    exit(1);
  if (child == 0) {
    int self = getpid(); // Must be traced through the inherited mask.
    if (trace(0) < 0)
      exit(1);
    getpid();           // Must not be traced after disabling.
    printf("tracetest: child %d disabled\n", self);
    exit(0);
  }
  int status = -1;
  if (wait(&status) != child || status != 0)
    exit(1);
  getpid();             // Child disabling must not change the parent's mask.
  if (trace(0) < 0)
    exit(1);
  getpid();             // Must not be traced after disabling.
  printf("tracetest: PASS\n");
  exit(0);
}
