### Part 1
The kernel boots:

![[Pasted image 20260928172140.png]]

### Part 2
The commands work:
![[Pasted image 20260928172216.png]]
1.
- greap
- sh
- rm
- cat

2. ![[Pasted image 20260928172617.png]]
The two OS features for pipe to work are: processes and some kind of standard output for them to communicate.

3. The xv6 shell is much more simple, because it provides less features than the linux one.
### Part 3
1. The syscalls it uses are:
- read - read from a file descriptor
- fprint - prints to the standard output
- exit - exists the program with a status
- open - opens a file
- close - closes a file
2. sys_read is implemented on line 69 of the file kernel/sysfile.c
3. The code in the kernel runs in ring 0 while the code for the user is running in ring 3

### Part 4
The implemented sleep function in the userspace works correctly
![[Pasted image 20260928173801.png]]
