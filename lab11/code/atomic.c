/* Optional comparison: gcc -std=c11 -Wall -Wextra -O0 -pthread -o atomic atomic.c */
#include <pthread.h>
#include <stdatomic.h>
#include "thread_utils.h"

#define N 1000000
atomic_long counter = 0;

static void *add(void *arg)
{
    (void)arg;
    for (int i = 0; i < N; i++)
        atomic_fetch_add(&counter, 1);
    return NULL;
}

int main(void)
{
    pthread_t a, b;
    thread_check(pthread_create(&a, NULL, add, NULL), "pthread_create a");
    thread_check(pthread_create(&b, NULL, add, NULL), "pthread_create b");
    thread_check(pthread_join(a, NULL), "pthread_join a");
    thread_check(pthread_join(b, NULL), "pthread_join b");
    printf("counter = %ld (expected %d)\n", atomic_load(&counter), 2 * N);
    return 0;
}
