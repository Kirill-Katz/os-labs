"""Boot xv6 and retain actual lab checkpoints and final command output."""
from pathlib import Path
import sys
import pexpect

lab = Path(__file__).resolve().parent.parent
out = lab / 'report_files/output'
out.mkdir(parents=True, exist_ok=True)
stage = sys.argv[1]
commands = {
    'baseline': [('baseline', 'echo lab13-baseline-ok')],
    'checkpoint1': [('checkpoint1', 'semtest')],
    'final': [
        ('semtest-1', 'semtest'), ('semtest-2', 'semtest'), ('semtest-3', 'semtest'),
        ('mix-1', 'mix'), ('mix-2', 'mix'),
        ('mix-lock-1', 'mix lock'), ('mix-lock-2', 'mix lock'), ('mix-lock-3', 'mix lock'),
        ('semcheck', 'semcheck'),
        ('semsleep', 'semsleep'),
        ('trace-semaphores', 'trace 117440512 semprobe'),
        ('trace-read', 'trace 32 grep hello README'),
        ('regression', 'usertests -q'),
    ],
}[stage]
with (out / (stage + '-session.txt')).open('w') as log:
    child = pexpect.spawn('make', ['qemu', 'CPUS=3', 'TOOLPREFIX=riscv64-linux-gnu-'],
                          cwd=str(lab.parent / 'xv6-riscv'), encoding='utf-8',
                          codec_errors='replace', timeout=180, maxread=65536)
    child.logfile_read = log
    try:
        child.expect_exact('$ ')
        for name, command in commands:
            child.sendline(command)
            if name == 'semsleep':
                child.expect_exact('semsleep: child waiting; inspect with Ctrl-P')
                before = child.before + 'semsleep: child waiting; inspect with Ctrl-P'
                child.send('\x10')
                child.expect_exact('$ ')
                text = before + child.before
            else:
                child.expect_exact('$ ', timeout=600 if name == 'regression' else 180)
                text = child.before
            text = text.replace('\r\n', '\n')
            (out / (name + '.txt')).write_text(text)
            if 'panic:' in text:
                raise RuntimeError('kernel panic in ' + name)
            print('Captured ' + name, flush=True)
        child.send('\x01x')
        child.expect(pexpect.EOF)
    finally:
        child.close(force=True)
