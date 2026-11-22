/* Reader-preference solution; it does not promise writer starvation freedom.
 * gcc -std=c11 -Wall -Wextra -Werror -O0 -pthread -o readers readers.c
 */
#define _DEFAULT_SOURCE
#include <pthread.h>
#include <unistd.h>
#include "thread_utils.h"

#define READERS 3
#define WRITERS 2
int value = 0;
int readers = 0;
sem_t rlock, room;

static void *reader(void *arg)
{
    int id = *(int *)arg;
    sem_wait_checked(&rlock);
    if (++readers == 1)
        sem_wait_checked(&room);
    /* Keep this counter snapshot under rlock (unlike the handout print).
     * The reader group holds room, so value cannot be changed by a writer.
     */
    printf("reader %d reads %d (readers inside: %d)\n", id, value, readers);
    sem_check(sem_post(&rlock), "post rlock");

    usleep(200000); /* Reading interval: other readers may overlap. */

    sem_wait_checked(&rlock);
    readers--;
    printf("reader %d leaves (readers inside: %d)\n", id, readers);
    if (readers == 0)
        sem_check(sem_post(&room), "post room");
    sem_check(sem_post(&rlock), "post rlock");
    return NULL;
}

static void *writer(void *arg)
{
    int id = *(int *)arg;
    sem_wait_checked(&room);
    value += 10;
    printf("writer %d writes %d (alone)\n", id, value);
    usleep(200000);
    printf("writer %d leaves\n", id);
    sem_check(sem_post(&room), "post room");
    return NULL;
}

int main(void)
{
    setvbuf(stdout, NULL, _IOLBF, 0);
    sem_check(sem_init(&rlock, 0, 1), "init rlock");
    sem_check(sem_init(&room, 0, 1), "init room");
    pthread_t r[READERS], w[WRITERS];
    int reader_ids[READERS] = {1, 2, 3};
    int writer_ids[WRITERS] = {1, 2};
    thread_check(pthread_create(&w[0], NULL, writer, &writer_ids[0]), "create writer 1");
    for (int i = 0; i < READERS; i++)
        thread_check(pthread_create(&r[i], NULL, reader, &reader_ids[i]), "create reader");
    thread_check(pthread_create(&w[1], NULL, writer, &writer_ids[1]), "create writer 2");
    for (int i = 0; i < READERS; i++)
        thread_check(pthread_join(r[i], NULL), "join reader");
    for (int i = 0; i < WRITERS; i++)
        thread_check(pthread_join(w[i], NULL), "join writer");
    printf("final value: %d; readers remaining: %d\n", value, readers);
    sem_check(sem_destroy(&rlock), "destroy rlock");
    sem_check(sem_destroy(&room), "destroy room");
    return 0;
}
