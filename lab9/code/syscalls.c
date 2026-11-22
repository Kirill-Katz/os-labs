/* Build: gcc -std=c11 -Wall -Wextra -Werror -o syscalls syscalls.c */
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>

int main(void)
{
    const char *msg = "hello, kernel\n";
    int fd = open("note.txt", O_CREAT | O_WRONLY | O_TRUNC, 0644);
    if (fd < 0) {
        perror("open for writing");
        return 1;
    }
    printf("open returned descriptor %d\n", fd);

    size_t sent = 0;
    while (sent < strlen(msg)) {
        ssize_t n = write(fd, msg + sent, strlen(msg) - sent);
        if (n < 0 && errno == EINTR)
            continue;
        if (n <= 0) {
            if (n < 0)
                perror("write");
            else
                fprintf(stderr, "write made no progress\n");
            close(fd);
            return 1;
        }
        sent += (size_t)n;
    }
    printf("write sent %zd bytes\n", (ssize_t)sent);
    if (close(fd) < 0) {
        perror("close after writing");
        return 1;
    }

    fd = open("note.txt", O_RDONLY);
    if (fd < 0) {
        perror("open for reading");
        return 1;
    }
    char buf[64];
    ssize_t n;
    do {
        n = read(fd, buf, sizeof(buf) - 1);
    } while (n < 0 && errno == EINTR);
    if (n < 0) {
        perror("read");
        close(fd);
        return 1;
    }
    buf[n] = '\0';
    printf("read got %zd bytes: %s", n, buf);
    if (close(fd) < 0) {
        perror("close after reading");
        return 1;
    }
    return 0;
}
