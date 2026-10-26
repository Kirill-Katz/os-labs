#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>

/* Do the same as the shell command: ls /etc | wc -l. */
int
main(void)
{
    int p[2];
    if (pipe(p) < 0) {
        perror("pipe");
        return 1;
    }

    pid_t ls_pid = fork();
    if (ls_pid < 0) {
        perror("fork ls");
        close(p[0]);
        close(p[1]);
        return 1;
    }
    if (ls_pid == 0) {
        close(STDOUT_FILENO);
        if (dup(p[1]) != STDOUT_FILENO) {
            perror("dup ls");
            exit(1);
        }
        close(p[0]);
        close(p[1]);
        execlp("ls", "ls", "/etc", (char *)NULL);
        perror("exec ls");
        exit(127);
    }

    pid_t wc_pid = fork();
    if (wc_pid < 0) {
        perror("fork wc");
        close(p[0]);
        close(p[1]);
        waitpid(ls_pid, NULL, 0);
        return 1;
    }
    if (wc_pid == 0) {
        close(STDIN_FILENO);
        if (dup(p[0]) != STDIN_FILENO) {
            perror("dup wc");
            exit(1);
        }
        close(p[0]);
        close(p[1]);
        execlp("wc", "wc", "-l", (char *)NULL);
        perror("exec wc");
        exit(127);
    }

    close(p[0]);
    close(p[1]);

    int ls_status, wc_status;
    if (waitpid(ls_pid, &ls_status, 0) < 0 ||
        waitpid(wc_pid, &wc_status, 0) < 0) {
        perror("waitpid");
        return 1;
    }
    return WIFEXITED(ls_status) && WEXITSTATUS(ls_status) == 0 &&
           WIFEXITED(wc_status) && WEXITSTATUS(wc_status) == 0 ? 0 : 1;
}
