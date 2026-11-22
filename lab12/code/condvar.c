/* gcc -std=c11 -Wall -Wextra -Werror -O0 -pthread -o condvar condvar.c
 * Teaching variation only: -DUSE_IF=1 (not a correct general wait pattern).
 */
#include <pthread.h>
#include <unistd.h>
#include "thread_utils.h"

#ifndef USE_IF
#define USE_IF 0
#endif
char message[32];
int ready = 0;
pthread_mutex_t lock = PTHREAD_MUTEX_INITIALIZER;
pthread_cond_t changed = PTHREAD_COND_INITIALIZER;

static void *writer(void *arg)
{
    (void)arg;
    sleep(1);
    thread_check(pthread_mutex_lock(&lock), "writer lock");
    strcpy(message, "hello");
    ready = 1;
    printf("A: message written\n");
    thread_check(pthread_cond_signal(&changed), "signal changed");
    thread_check(pthread_mutex_unlock(&lock), "writer unlock");
    return NULL;
}

static void *reader(void *arg)
{
    (void)arg;
    thread_check(pthread_mutex_lock(&lock), "reader lock");
#if USE_IF
    if (!ready) {
#else
    while (!ready) {
#endif
        printf("B: not ready, I sleep\n");
        thread_check(pthread_cond_wait(&changed, &lock), "wait changed");
    }
    printf("B: I read \"%s\"\n", message);
    thread_check(pthread_mutex_unlock(&lock), "reader unlock");
    return NULL;
}

int main(void)
{
    setvbuf(stdout, NULL, _IOLBF, 0);
    pthread_t a, b;
    thread_check(pthread_create(&b, NULL, reader, NULL), "create reader");
    thread_check(pthread_create(&a, NULL, writer, NULL), "create writer");
    thread_check(pthread_join(a, NULL), "join writer");
    thread_check(pthread_join(b, NULL), "join reader");
    thread_check(pthread_cond_destroy(&changed), "destroy changed");
    thread_check(pthread_mutex_destroy(&lock), "destroy lock");
    return 0;
}
