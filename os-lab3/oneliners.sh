#!/bin/bash
# Run from the directory containing access.log.

# Q1. How many requests failed?
grep -c ' FAIL ' access.log

# Q2. How many different pages were requested, and which?
awk '{print $5}' access.log | sort -u | awk '{print; n++} END {print "Total pages:", n}'

# Q3. How many requests did each page get?
awk '{print $5}' access.log | sort | uniq -c

# Q4. Which user or users have the most failed requests, and how many?
awk '$4 == "FAIL" {n[$3]++} END {for (u in n) if (n[u] > max) max=n[u]; for (u in n) if (n[u] == max) print u, max}' access.log | sort

# Q5. How many requests did user3 make, and how many of them failed?
awk '$3 == "user3" {total++; if ($4 == "FAIL") failed++} END {print "user3:", total, "requests,", failed, "failed"}' access.log

# Q6. Print the last 3 failed requests, showing only time and user.
awk '$4 == "FAIL" {print $2, $3}' access.log | tail -3

# Q7. Which login shells appear in /etc/passwd, and how many accounts use each?
awk -F: 'NF >= 7 && $1 !~ /^#/ {print $7}' /etc/passwd | sort | uniq -c

# Q8. Why do ls /etc | wc -l and ls -l /etc | wc -l differ by one?
echo "plain: $(ls /etc | wc -l); long: $(ls -l /etc | wc -l)"
