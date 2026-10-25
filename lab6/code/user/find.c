#include "kernel/types.h"
#include "kernel/stat.h"
#include "kernel/fs.h"
#include "user/user.h"
#include "kernel/fcntl.h"

static int
walk(char *path, char *target)
{
  char buf[512];
  char name[DIRSIZ + 1];
  struct dirent de;
  struct stat st;
  int fd;
  int failed = 0;
  int len = strlen(path);

  if(stat(path, &st) < 0){
    fprintf(2, "find: cannot stat %s\n", path);
    return 1;
  }
  if(st.type != T_DIR){
    fprintf(2, "find: not a directory: %s\n", path);
    return 1;
  }
  if((fd = open(path, O_RDONLY)) < 0){
    fprintf(2, "find: cannot open %s\n", path);
    return 1;
  }
  if(len + 1 + DIRSIZ + 1 > (int)sizeof(buf)){
    fprintf(2, "find: path too long: %s\n", path);
    close(fd);
    return 1;
  }
  strcpy(buf, path);
  char *end = buf + len;
  if(len == 0 || buf[len - 1] != '/')
    *end++ = '/';

  while(read(fd, &de, sizeof(de)) == sizeof(de)){
    if(de.inum == 0)
      continue;
    memmove(name, de.name, DIRSIZ);
    name[DIRSIZ] = 0;
    if(strcmp(name, ".") == 0 || strcmp(name, "..") == 0)
      continue;
    strcpy(end, name);
    if(stat(buf, &st) < 0){
      fprintf(2, "find: cannot stat %s\n", buf);
      failed = 1;
      continue;
    }
    if(strcmp(name, target) == 0)
      printf("%s\n", buf);
    if(st.type == T_DIR && walk(buf, target) != 0)
      failed = 1;
  }
  close(fd);
  return failed;
}

int
main(int argc, char *argv[])
{
  if(argc != 3){
    fprintf(2, "usage: find <dir> <name>\n");
    exit(1);
  }
  exit(walk(argv[1], argv[2]));
}
