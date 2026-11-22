// Small deterministic sequence for tracing the three new syscall names.
#include "kernel/types.h"
#include "user/user.h"

int
main(void)
{
  if (sem_init(4, 2) < 0 || sem_down(4) < 0 || sem_down(4) < 0 ||
      sem_up(4) < 0 || sem_down(4) < 0)
    exit(1);
  printf("semprobe: PASS\n");
  exit(0);
}
