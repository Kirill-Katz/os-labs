/* gcc -Wall -Wextra -O0 -pthread -o order order.c
 * Experiment: add -DREADY_START=1 to remove the required ordering.
 */
#include <pthread.h>
#include <string.h>
#include <unistd.h>
#include "thread_utils.h"

#ifndef READY_START
#define READY_START 0
#endif
char message[32];
sem_t ready;

static void *writer(void *arg)
{
    (void)arg;
    sleep(1);
    strcpy(message, "hello");
    printf("A: message written\n");
    sem_check(sem_post(&ready), "sem_post");
    return NULL;
}

static void *reader(void *arg)
{
    (void)arg;
    printf("B: waiting for the message...\n");
    sem_wait_checked(&ready);
    printf("B: I read \"%s\"\n", message);
    return NULL;
}

int main(void)
{
    sem_check(sem_init(&ready, 0, READY_START), "sem_init");
    pthread_t a, b;
    thread_check(pthread_create(&b, NULL, reader, NULL), "pthread_create reader");
    thread_check(pthread_create(&a, NULL, writer, NULL), "pthread_create writer");
    thread_check(pthread_join(a, NULL), "pthread_join writer");
    thread_check(pthread_join(b, NULL), "pthread_join reader");
    sem_check(sem_destroy(&ready), "sem_destroy");
    return 0;
}
