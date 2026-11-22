#ifndef THREAD_UTILS_H
#define THREAD_UTILS_H

#include <errno.h>
#include <semaphore.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* pthread functions return an error number instead of setting errno. */
static inline void thread_check(int error, const char *operation)
{
    if (error != 0) {
        fprintf(stderr, "%s: %s\n", operation, strerror(error));
        exit(EXIT_FAILURE);
    }
}

static inline void sem_check(int result, const char *operation)
{
    if (result == -1) {
        perror(operation);
        exit(EXIT_FAILURE);
    }
}

/* A signal may interrupt sem_wait; never enter without acquiring a permit. */
static inline void sem_wait_checked(sem_t *sem)
{
    int result;
    do {
        result = sem_wait(sem);
    } while (result == -1 && errno == EINTR);
    sem_check(result, "sem_wait");
}

#endif
