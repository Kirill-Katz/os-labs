#include "kernel/types.h"
#include "user/user.h"

int
main(int argc, char *argv[])
{
  int p2c[2], c2p[2];
  char b = 'x';

  if(pipe(p2c) < 0){
    fprintf(2, "pingpong: first pipe failed\n");
    exit(1);
  }
  if(pipe(c2p) < 0){
    fprintf(2, "pingpong: second pipe failed\n");
    close(p2c[0]);
    close(p2c[1]);
    exit(1);
  }

  int pid = fork();
  if(pid < 0){
    fprintf(2, "pingpong: fork failed\n");
    close(p2c[0]);
    close(p2c[1]);
    close(c2p[0]);
    close(c2p[1]);
    exit(1);
  }
  if(pid == 0){
    close(p2c[1]);
    close(c2p[0]);
    if(read(p2c[0], &b, 1) != 1){
      fprintf(2, "pingpong: child read failed\n");
      close(p2c[0]);
      close(c2p[1]);
      exit(1);
    }
    close(p2c[0]);
    printf("%d: received ping\n", getpid());
    if(write(c2p[1], &b, 1) != 1){
      fprintf(2, "pingpong: child write failed\n");
      close(c2p[1]);
      exit(1);
    }
    close(c2p[1]);
    exit(0);
  }

  close(p2c[0]);
  close(c2p[1]);
  if(write(p2c[1], &b, 1) != 1){
    fprintf(2, "pingpong: parent write failed\n");
    close(p2c[1]);
    close(c2p[0]);
    wait(0);
    exit(1);
  }
  close(p2c[1]);
  if(read(c2p[0], &b, 1) != 1){
    fprintf(2, "pingpong: parent read failed\n");
    close(c2p[0]);
    wait(0);
    exit(1);
  }
  close(c2p[0]);
  printf("%d: received pong\n", getpid());

  int status;
  if(wait(&status) < 0 || status != 0){
    fprintf(2, "pingpong: child failed\n");
    exit(1);
  }
  exit(0);
}
