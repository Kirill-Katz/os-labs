"""Check actual trace evidence and retain normal/failure-path regression tests."""
from pathlib import Path
import re
import subprocess
import tempfile

out = Path('/work/report_files/output')
expected = ('open returned descriptor 3\n'
            'write sent 14 bytes\n'
            'read got 14 bytes: hello, kernel\n')
checks = []

def check(condition, label):
    if not condition:
        raise AssertionError(label)
    checks.append('PASS: ' + label)

for name in ('syscalls.stdout', 'syscalls-traced.stdout', 'count.stdout'):
    check((out / name).read_text() == expected, name + ' matches expected output')
check((out / 'note.txt').read_bytes() == b'hello, kernel\n', 'note.txt contains exactly 14 expected bytes')
trace = (out / 'syscalls.trace').read_text()
patterns = [
    r'openat\(AT_FDCWD, "note.txt", O_WRONLY\|O_CREAT\|O_TRUNC, 0644\)\s+= 3',
    r'write\(3, "hello, kernel\\n", 14\)\s+= 14',
    r'close\(3\)\s+= 0',
    r'openat\(AT_FDCWD, "note.txt", O_RDONLY\)\s+= 3',
    r'read\(3, "hello, kernel\\n", 63\)\s+= 14',
    r'close\(3\)\s+= 0',
]
pos = 0
for pattern in patterns:
    match = re.search(pattern, trace[pos:])
    check(match is not None, 'ordered syscall: ' + pattern)
    pos += match.end()
writes = re.findall(r'^write\((\d+),.*?\)\s+= (\d+)$', (out / 'write.trace').read_text(), re.M)
check(writes == [('3', '14'), ('1', str(len(expected)))], 'two writes: 14 bytes to file, buffered diagnostics to stdout')
check(re.search(r'\s2\s+write\s*$', (out / 'write.summary').read_text(), re.M) is not None,
      'strace -c independently counts two write calls')

with tempfile.TemporaryDirectory() as directory:
    root = Path(directory)
    note = root / 'note.txt'
    # O_TRUNC must discard an old, longer file.
    note.write_text('old data' * 100)
    result = subprocess.run([str(out / 'syscalls')], cwd=root, capture_output=True)
    check(result.returncode == 0 and note.read_bytes() == b'hello, kernel\n', 'O_TRUNC replaces longer existing contents')
    note.unlink()
    note.mkdir()
    result = subprocess.run([str(out / 'syscalls')], cwd=root, capture_output=True)
    check(result.returncode == 1 and b'open for writing' in result.stderr, 'open failure exits cleanly (note.txt is a directory)')
    note.rmdir()
    note.symlink_to('/dev/full')
    result = subprocess.run([str(out / 'syscalls')], cwd=root, capture_output=True)
    check(result.returncode == 1 and b'write:' in result.stderr, 'write failure exits cleanly (/dev/full)')

filtered = (out / 'ls.trace').read_text()
ls_calls = len(re.findall(r'^(?:\d+\s+)?(?:openat|read|write|close)\(', filtered, re.M))
checks.append(f'OBSERVED: {ls_calls} calls in filtered ls trace')
checks.append(f'OBSERVED: {len(writes)} write calls in syscalls')
(out / 'verification.txt').write_text('\n'.join(checks) + '\n')
print('\n'.join(checks))
