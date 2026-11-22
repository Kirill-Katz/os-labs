/* Submitted default: both threads acquire A then B (fixed).
 * Original bug: -DOPPOSITE_ORDER=1
 * Original bug without sleeps: -DOPPOSITE_ORDER=1 -DDELAY_SECONDS=0
 * Run broken versions with: timeout 5 ./deadlock_original
 */
#include <pthread.h>
#include <unistd.h>
#include "thread_utils.h"

#ifndef OPPOSITE_ORDER
#define OPPOSITE_ORDER 0
#endif
#ifndef DELAY_SECONDS
#define DELAY_SECONDS 1
#endif
pthread_mutex_t A = PTHREAD_MUTEX_INITIALIZER;
pthread_mutex_t B = PTHREAD_MUTEX_INITIALIZER;

static void *one(void *arg)
{
    (void)arg;
    thread_check(pthread_mutex_lock(&A), "one lock A");
    printf("one: I have A, I want B\n");
#if DELAY_SECONDS > 0
    sleep(DELAY_SECONDS);
#endif
    thread_check(pthread_mutex_lock(&B), "one lock B");
    printf("one: I have both\n");
    thread_check(pthread_mutex_unlock(&B), "one unlock B");
    thread_check(pthread_mutex_unlock(&A), "one unlock A");
    return NULL;
}

static void *two(void *arg)
{
    (void)arg;
#if OPPOSITE_ORDER
    thread_check(pthread_mutex_lock(&B), "two lock B");
    printf("two: I have B, I want A\n");
#else
    thread_check(pthread_mutex_lock(&A), "two lock A");
    printf("two: I have A, I want B\n");
#endif
#if DELAY_SECONDS > 0
    sleep(DELAY_SECONDS);
#endif
#if OPPOSITE_ORDER
    thread_check(pthread_mutex_lock(&A), "two lock A");
#else
    thread_check(pthread_mutex_lock(&B), "two lock B");
#endif
    printf("two: I have both\n");
#if OPPOSITE_ORDER
    thread_check(pthread_mutex_unlock(&A), "two unlock A");
    thread_check(pthread_mutex_unlock(&B), "two unlock B");
#else
    thread_check(pthread_mutex_unlock(&B), "two unlock B");
    thread_check(pthread_mutex_unlock(&A), "two unlock A");
#endif
    return NULL;
}

int main(void)
{
    setvbuf(stdout, NULL, _IOLBF, 0);
    pthread_t t1, t2;
    thread_check(pthread_create(&t1, NULL, one, NULL), "create one");
    thread_check(pthread_create(&t2, NULL, two, NULL), "create two");
    thread_check(pthread_join(t1, NULL), "join one");
    thread_check(pthread_join(t2, NULL), "join two");
    printf("done\n");
    thread_check(pthread_mutex_destroy(&A), "destroy A");
    thread_check(pthread_mutex_destroy(&B), "destroy B");
    return 0;
}
