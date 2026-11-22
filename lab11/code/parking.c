/* gcc -Wall -Wextra -O0 -pthread -o parking parking.c
 * Experiment: add -DPLACES=1 for one-at-a-time parking.
 */
#include <pthread.h>
#include <unistd.h>
#include "thread_utils.h"

#ifndef PLACES
#define PLACES 3
#endif
#define CARS 6
sem_t places;
pthread_mutex_t lock = PTHREAD_MUTEX_INITIALIZER;
int inside = 0;

static void *car(void *arg)
{
    int id = *(int *)arg;
    sem_wait_checked(&places);
    thread_check(pthread_mutex_lock(&lock), "pthread_mutex_lock");
    inside++;
    printf("car %d enters (inside: %d)\n", id, inside);
    thread_check(pthread_mutex_unlock(&lock), "pthread_mutex_unlock");

    sleep(1);

    thread_check(pthread_mutex_lock(&lock), "pthread_mutex_lock");
    inside--;
    printf("car %d leaves (inside: %d)\n", id, inside);
    thread_check(pthread_mutex_unlock(&lock), "pthread_mutex_unlock");
    sem_check(sem_post(&places), "sem_post");
    return NULL;
}

int main(void)
{
    sem_check(sem_init(&places, 0, PLACES), "sem_init");
    pthread_t threads[CARS];
    int ids[CARS];
    for (int i = 0; i < CARS; i++) {
        ids[i] = i + 1;
        thread_check(pthread_create(&threads[i], NULL, car, &ids[i]),
                     "pthread_create car");
    }
    for (int i = 0; i < CARS; i++)
        thread_check(pthread_join(threads[i], NULL), "pthread_join car");
    sem_check(sem_destroy(&places), "sem_destroy");
    thread_check(pthread_mutex_destroy(&lock), "pthread_mutex_destroy");
    return 0;
}
