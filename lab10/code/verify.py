"""Verify retained xv6 transcripts; run from any directory after run_qemu.py."""
from pathlib import Path
import re

lab = Path(__file__).resolve().parent.parent
root = lab.parent / 'xv6-riscv'
out = lab / 'report_files/output'
results = []

def check(ok, label):
    if not ok:
        raise AssertionError(label)
    results.append('PASS: ' + label)

def text(name):
    return (out / (name + '.txt')).read_text()

def calls(name):
    return re.findall(r'(\d+): syscall (\w+) -> (-?\d+)', text(name))

check('baseline-boot-ok' in text('baseline'), 'initial xv6 tree boots')
check('unknown sys call 23' in text('checkpoint1') and 'trace: failed' in text('checkpoint1'),
      'Part 1 reaches the kernel with syscall 23')
read = calls('read')
check([(n, int(v)) for _, n, v in read] == [('read', 1023), ('read', 965), ('read', 453), ('read', 0)],
      'required read sequence matches handout exactly')
check((root / 'README').stat().st_size == 2441 and sum(int(v) for _, _, v in read) == 2441,
      'read byte counts sum to the unchanged 2441-byte README')
check([n for _, n, _ in calls('all')] == ['trace', 'exec', 'open', 'read', 'read', 'read', 'read', 'close'],
      'all-call mask produces expected syscall names in order')
check([int(v) for _, _, v in calls('all')] == [0, 3, 3, 1023, 965, 453, 0, 0],
      'all-call mask returns expected results')
forks = calls('fork')
check(len(forks) > 20 and all(n == 'fork' for _, n, _ in forks), 'fork mask filters out other calls')
check(len({pid for pid, _, _ in forks}) >= 3, 'fork tracing reaches multiple descendant processes')
check(any(v == '-1' for _, _, v in forks), 'fork resource exhaustion is printed as signed -1')
check('ALL TESTS PASSED' in text('fork'), 'forkforkfork completes successfully')
check([(n, int(v)) for _, n, v in calls('write')] == [('write', 2), ('write', 1)],
      'echo hi performs two traced writes (2 bytes then 1 byte)')
check(re.search(r'hi\d+: syscall write -> 2\n\n\d+: syscall write -> 1', text('write')) is not None,
      'write tracing appears between hi and its newline')
check([(n, int(v)) for _, n, v in calls('open-close')] == [('open', 3), ('close', 0)],
      'mask 2129920 selects only open and close')
check(not calls('zero') and 'quiet' in text('zero'), 'zero mask disables tracing')
check(not calls('plain') and 'untraced' in text('plain'), 'later untraced command does not inherit another process mask')
check('usage: trace mask command [args...]' in text('usage'), 'missing arguments produce usage message')
# xv6 fprintf writes one character per call, so all-call tracing splits the message.
missing_message = re.sub(r'\d+: syscall \w+ -> -?\d+\n', '', text('missing'))
check('trace: exec nosuchprog failed' in missing_message and ('exec', '-1') in [(n, v) for _, n, v in calls('missing')],
      'failed exec is traced with -1 and reported to the user')
lifecycle = text('lifecycle')
parent = re.search(r'tracetest: parent (\d+)', lifecycle).group(1)
child = re.search(r'tracetest: child (\d+) disabled', lifecycle).group(1)
check(calls('lifecycle') == [(parent, 'getpid', parent), (child, 'getpid', child), (parent, 'getpid', parent)]
      and 'tracetest: PASS' in lifecycle,
      'fork inherits mask; child and parent can disable tracing independently')
regression = text('regression')
check('ALL TESTS PASSED' in regression and 'FAILED' not in regression and not calls('regression'),
      'complete quick usertests suite passes without leaked tracing')
for filename in sorted(out.glob('*.txt')):
    if filename.name != 'verification.txt':
        check('panic:' not in filename.read_text(), 'no kernel panic in ' + filename.name)
# Compare submission copies with the actual tested integrated sources.
for name in ['Makefile', 'kernel/proc.c', 'kernel/proc.h', 'kernel/syscall.c',
             'kernel/syscall.h', 'kernel/sysproc.c', 'user/user.h', 'user/usys.pl',
             'user/trace.c', 'user/tracetest.c']:
    check((lab / 'code' / name).read_bytes() == (root / name).read_bytes(),
          'submission source matches tested tree: ' + name)
results.append('OBSERVED: ' + str(len(re.findall(r'^test ', regression, re.M))) + ' tests in usertests -q')
results.append('OBSERVED: fork traces from PIDs ' + ', '.join(sorted({pid for pid, _, _ in forks}, key=int)))
(out / 'verification.txt').write_text('\n'.join(results) + '\n')
print('\n'.join(results))
