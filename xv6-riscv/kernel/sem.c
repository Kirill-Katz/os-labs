// Lab 13: eight global counting semaphores, shared by all processes.
#include "types.h"
#include "riscv.h"
#include "defs.h"
#include "param.h"
#include "spinlock.h"
#include "proc.h"

#define NSEM 8
#define SEM_MAX 0x7fffffff

struct sem {
  struct spinlock lock;
  int value;
};
static struct sem sems[NSEM];

void
seminit(void)
{
  for (int i = 0; i < NSEM; i++) {
    initlock(&sems[i].lock, "semaphore");
    sems[i].value = 0;
  }
}

uint64
sys_sem_init(void)
{
  int id, value;
  argint(0, &id);
  argint(1, &value);
  if (id < 0 || id >= NSEM || value < 0)
    return -1;
  acquire(&sems[id].lock);
  sems[id].value = value;
  release(&sems[id].lock);
  return 0;
}

uint64
sys_sem_down(void)
{
  int id;
  argint(0, &id);
  if (id < 0 || id >= NSEM)
    return -1;
  struct sem *s = &sems[id];

  acquire(&s->lock);
  while (s->value == 0) {
    sleep_prepare(s);
    release(&s->lock);
    sleep_killable(); // Same two-phase wait, with kill checked atomically.
    acquire(&s->lock);
    if (killed(myproc())) {
      release(&s->lock);
      return -1;
    }
  }
  s->value--;
  release(&s->lock);
  return 0;
}

uint64
sys_sem_up(void)
{
  int id;
  argint(0, &id);
  if (id < 0 || id >= NSEM)
    return -1;
  struct sem *s = &sems[id];

  acquire(&s->lock);
  if (s->value == SEM_MAX) {
    release(&s->lock);
    return -1; // Do not overflow the signed counter.
  }
  s->value++;
  wakeup(s);
  release(&s->lock);
  return 0;
}
