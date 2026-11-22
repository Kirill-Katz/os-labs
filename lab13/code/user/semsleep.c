// Let the QEMU harness capture Ctrl-P while a child is blocked in sem_down.
#include "kernel/types.h"
#include "user/user.h"

int
main(void)
{
  int ready[2];
  if (pipe(ready) < 0 || sem_init(7, 0) < 0)
    exit(1);
  int pid = fork();
  if (pid < 0)
    exit(1);
  char byte = 'x';
  if (pid == 0) {
    close(ready[0]);
    if (write(ready[1], &byte, 1) != 1)
      exit(1);
    close(ready[1]);
    if (sem_down(7) < 0)
      exit(1);
    exit(0);
  }
  close(ready[1]);
  if (read(ready[0], &byte, 1) != 1)
    exit(1);
  close(ready[0]);
  pause(3);
  printf("semsleep: blocked child pid %d\n", pid);
  printf("semsleep: child waiting; inspect with Ctrl-P\n");
  pause(30);
  if (sem_up(7) < 0)
    exit(1);
  int status = -1;
  if (wait(&status) != pid || status != 0)
    exit(1);
  printf("semsleep: PASS\n");
  exit(0);
}
