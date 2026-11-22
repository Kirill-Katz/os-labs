/* gcc -Wall -Wextra -O0 -pthread -o sem sem.c
 * Experiment: add -DSEM_START=2 to permit two simultaneous increments.
 */
#include <pthread.h>
#include "thread_utils.h"

#define N 1000000
#ifndef SEM_START
#define SEM_START 1
#endif
long counter = 0;
sem_t s;

static void *add(void *arg)
{
    (void)arg;
    for (int i = 0; i < N; i++) {
        sem_wait_checked(&s);
        counter++;
        sem_check(sem_post(&s), "sem_post");
    }
    return NULL;
}

int main(void)
{
    sem_check(sem_init(&s, 0, SEM_START), "sem_init");
    pthread_t a, b;
    thread_check(pthread_create(&a, NULL, add, NULL), "pthread_create a");
    thread_check(pthread_create(&b, NULL, add, NULL), "pthread_create b");
    thread_check(pthread_join(a, NULL), "pthread_join a");
    thread_check(pthread_join(b, NULL), "pthread_join b");
    printf("counter = %ld (expected %d)\n", counter, 2 * N);
    sem_check(sem_destroy(&s), "sem_destroy");
    return 0;
}
