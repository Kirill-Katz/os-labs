/* gcc -std=c11 -Wall -Wextra -Werror -O0 -pthread -o prodcons prodcons.c
 * Broken experiment only: -DBAD_LOCK_ORDER=1
 */
#define _DEFAULT_SOURCE
#include <pthread.h>
#include <unistd.h>
#include "thread_utils.h"

#define SIZE 4
#define ITEMS 8
#ifndef BAD_LOCK_ORDER
#define BAD_LOCK_ORDER 0
#endif
int buf[SIZE];
int in = 0, out = 0, count = 0;
sem_t empty, full;
pthread_mutex_t lock = PTHREAD_MUTEX_INITIALIZER;

static void *producer(void *arg)
{
    (void)arg;
    for (int item = 1; item <= ITEMS; item++) {
#if BAD_LOCK_ORDER
        thread_check(pthread_mutex_lock(&lock), "producer lock");
        sem_wait_checked(&empty); /* Deliberately wrong: can wait holding lock. */
#else
        sem_wait_checked(&empty);
        thread_check(pthread_mutex_lock(&lock), "producer lock");
#endif
        buf[in] = item;
        in = (in + 1) % SIZE;
        count++;
        printf("put %d    (in buffer: %d)\n", item, count);
        thread_check(pthread_mutex_unlock(&lock), "producer unlock");
        sem_check(sem_post(&full), "post full");
    }
    return NULL;
}

static void *consumer(void *arg)
{
    (void)arg;
    for (int k = 0; k < ITEMS; k++) {
        sem_wait_checked(&full);
        thread_check(pthread_mutex_lock(&lock), "consumer lock");
        int item = buf[out];
        out = (out + 1) % SIZE;
        count--;
        printf("            take %d   (in buffer: %d)\n", item, count);
        thread_check(pthread_mutex_unlock(&lock), "consumer unlock");
        sem_check(sem_post(&empty), "post empty");
        usleep(300000);
    }
    return NULL;
}

int main(void)
{
    /* Preserve the last complete event even if a broken run is timed out. */
    setvbuf(stdout, NULL, _IOLBF, 0);
    sem_check(sem_init(&empty, 0, SIZE), "init empty");
    sem_check(sem_init(&full, 0, 0), "init full");
    pthread_t p, c;
    thread_check(pthread_create(&c, NULL, consumer, NULL), "create consumer");
    thread_check(pthread_create(&p, NULL, producer, NULL), "create producer");
    thread_check(pthread_join(p, NULL), "join producer");
    thread_check(pthread_join(c, NULL), "join consumer");
    sem_check(sem_destroy(&empty), "destroy empty");
    sem_check(sem_destroy(&full), "destroy full");
    thread_check(pthread_mutex_destroy(&lock), "destroy lock");
    return 0;
}
