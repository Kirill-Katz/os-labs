/* gcc -Wall -Wextra -O0 -pthread -o mutex mutex.c */
#include <pthread.h>
#include "thread_utils.h"

#define N 1000000
long counter = 0;
pthread_mutex_t lock = PTHREAD_MUTEX_INITIALIZER;

static void *add(void *arg)
{
    (void)arg;
    for (int i = 0; i < N; i++) {
        thread_check(pthread_mutex_lock(&lock), "pthread_mutex_lock");
        counter++;
        thread_check(pthread_mutex_unlock(&lock), "pthread_mutex_unlock");
    }
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
    thread_check(pthread_mutex_destroy(&lock), "pthread_mutex_destroy");
    return 0;
}
