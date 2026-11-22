"""Drive real xv6 boots, preserving raw output and failing on timeout/panic."""
from pathlib import Path
import sys
import pexpect

stage = sys.argv[1]
lab = Path(__file__).resolve().parent.parent
out = lab / 'report_files/output'
out.mkdir(parents=True, exist_ok=True)
commands = {
    'baseline': [('baseline', 'echo baseline-boot-ok')],
    'checkpoint1': [('checkpoint1', 'trace 32 grep hello README')],
    'final': [
        ('read', 'trace 32 grep hello README'),
        ('all', 'trace 2147483647 grep hello README'),
        ('fork', 'trace 2 usertests forkforkfork'),
        ('write', 'trace 65536 echo hi'),
        ('open-close', 'trace 2129920 grep hello README'),
        ('zero', 'trace 0 echo quiet'),
        ('plain', 'echo untraced'),
        ('usage', 'trace'),
        ('missing', 'trace 2147483647 nosuchprog'),
        ('lifecycle', 'tracetest'),
        ('regression', 'usertests -q'),
    ],
}[stage]
with (out / (stage + '-session.txt')).open('w') as log:
    child = pexpect.spawn('make', ['qemu', 'CPUS=3', 'TOOLPREFIX=riscv64-linux-gnu-'],
                          cwd=str(lab.parent / 'xv6-riscv'), encoding='utf-8', codec_errors='replace',
                          timeout=240, maxread=65536)
    child.logfile_read = log
    try:
        child.expect_exact('$ ')
        for name, command in commands:
            child.sendline(command)
            child.expect_exact('$ ', timeout=600 if name == 'regression' else 180)
            text = child.before.replace('\r\n', '\n')
            (out / (name + '.txt')).write_text(text)
            if 'panic:' in text:
                raise RuntimeError('kernel panic in ' + name)
            print('Captured ' + name, flush=True)
        child.send('\x01x')
        child.expect(pexpect.EOF)
    finally:
        child.close(force=True)
