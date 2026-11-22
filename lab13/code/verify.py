"""Check actual xv6 evidence and exact source-copy consistency."""
from pathlib import Path
import re

lab = Path(__file__).resolve().parent.parent
root = lab.parent / 'xv6-riscv'
out = lab / 'report_files/output'
checks, observations = [], []

def check(ok, message):
    if not ok:
        raise AssertionError(message)
    checks.append('PASS: ' + message)

def text(name):
    return (out / (name + '.txt')).read_text()

check('lab13-baseline-ok' in text('baseline'), 'starting xv6 tree boots')
checkpoint = text('checkpoint1')
check(re.search(r'\d+ semtest: unknown sys call 24', checkpoint) is not None
      and re.search(r'\d+ semtest: unknown sys call 25', checkpoint) is not None,
      'Part 1 stubs reach unimplemented kernel calls 24 and 25')
check(checkpoint.index('child: I ran after the parent') < checkpoint.index('parent: done, I let the child go'),
      'Part 1 child runs before the parent without working semaphores')
expected = ('semtest\nparent: done, I let the child go\nchild: I ran after the parent\n'
            'ping 1\n  pong 1\nping 2\n  pong 2\nping 3\n  pong 3\nsemtest: OK\n')
for index in range(1, 4):
    check(text(f'semtest-{index}') == expected, f'semtest #{index}: exact order and three strict ping/pong pairs')

mixed_runs = 0
for name in ['mix-1', 'mix-2', 'mix-lock-1', 'mix-lock-2', 'mix-lock-3']:
    body = text(name).split('\n', 1)[1]
    check(set(body) <= {'A', 'b', '\n'} and body.count('A') == 150 and body.count('b') == 150
          and body.count('\n') == 10, name + ': all 300 letters and ten newlines preserved')
    lines = body.splitlines()
    mixed = sum('A' in line and 'b' in line for line in lines)
    if name.startswith('mix-lock'):
        check(lines.count('A' * 30) == 5 and lines.count('b' * 30) == 5, name + ': ten whole lines, five per process')
    else:
        mixed_runs += mixed > 0
        observations.append(f'{name}: {mixed} mixed-content output lines observed')
check(mixed_runs > 0, 'unlocked runs actually exhibit mixed letters')

semcheck = text('semcheck')
for message in ['IDs and initial values PASS', 'count overflow guard PASS', 'six waiters and six posts PASS',
                '1000 ping-pong handoffs PASS', '20 immediate/blocked waiter kills PASS', 'ALL TESTS PASSED']:
    check('semcheck: ' + message in semcheck, message)
check('FAIL' not in semcheck and 'unknown sys call' not in semcheck, 'focused tests report no failure or unknown call')
snapshot = text('semsleep')
pid = re.search(r'semsleep: blocked child pid (\d+)', snapshot).group(1)
check(re.search(r'^' + pid + r' sleep\s+semsleep$', snapshot, re.M) is not None,
      'Ctrl-P captures the semaphore waiter in SLEEPING state')
check('semsleep: PASS' in snapshot, 'observed sleeper wakes, exits successfully, and is reaped')
observations.append('Blocked semaphore child PID in snapshot: ' + pid)
trace = re.findall(r'\d+: syscall (\w+) -> (-?\d+)', text('trace-semaphores'))
check(trace == [('sem_init', '0'), ('sem_down', '0'), ('sem_down', '0'), ('sem_up', '0'), ('sem_down', '0')]
      and 'semprobe: PASS' in text('trace-semaphores'), 'Lab 10 trace prints all three new syscall names and results')
read = re.findall(r'\d+: syscall read -> (\d+)', text('trace-read'))
check(read == ['1023', '965', '453', '0'] and (root / 'README').stat().st_size == 2441,
      'existing trace/read experiment remains unchanged')
regression = text('regression')
check('ALL TESTS PASSED' in regression and 'FAILED' not in regression and 'syscall ' not in regression,
      'complete quick usertests suite passes without leaked tracing')
observations.append('usertests -q test count: ' + str(len(re.findall(r'^test ', regression, re.M))))
for name in ['Makefile', 'kernel/defs.h', 'kernel/main.c', 'kernel/proc.c', 'kernel/sem.c',
             'kernel/syscall.c', 'kernel/syscall.h', 'user/user.h', 'user/usys.pl',
             'user/semtest.c', 'user/mix.c', 'user/semcheck.c', 'user/semsleep.c', 'user/semprobe.c']:
    check((root / name).read_bytes() == (lab / 'code' / name).read_bytes(), 'source copy matches tested tree: ' + name)
for path in sorted(out.glob('*.txt')):
    if path.name not in ['verification.txt', 'observations.txt', 'checkpoint1-excerpt.txt', 'regression-excerpt.txt']:
        check('panic:' not in path.read_text(), 'no kernel panic in ' + path.name)
(out / 'verification.txt').write_text('\n'.join(checks) + '\n')
(out / 'observations.txt').write_text('\n'.join(observations) + '\n')
print(f'All {len(checks)} evidence assertions passed.')
print('\n'.join(observations))
