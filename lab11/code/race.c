/* Intentionally incorrect: the unsynchronized counter demonstrates a data race.
 * Build without optimization: gcc -Wall -Wextra -O0 -pthread -o race race.c
 */
#include <pthread.h>
#include "thread_utils.h"

#define N 1000000
long counter = 0;

static void *add(void *arg)
{
    (void)arg;
    for (int i = 0; i < N; i++)
        counter++; /* Deliberately unprotected: undefined behavior in C. */
    return NULL;
}

int main(void)
{
    pthread_t a, b;
    thread_check(pthread_create(&a, NULL, add, NULL), "pthread_create a");
    thread_check(pthread_create(&b, NULL, add, NULL), "pthread_create b");
    thread_check(pthread_join(a, NULL), "pthread_join a");
    thread_check(pthread_join(b, NULL), "pthread_join b");
    printf("counter = %ld (expected %d)\n", counter, 2 * N);
    return 0;
}
