"""Build all configurations and retain real output, including bounded hangs."""
from pathlib import Path
import json
import os
import platform
import subprocess
import time

lab = Path(__file__).resolve().parent.parent
code = lab / 'code'
out = lab / 'report_files/output'
bin_dir = out / 'bin'
bin_dir.mkdir(parents=True, exist_ok=True)
variants = {
    'prodcons': ('prodcons.c', []),
    'prodcons_bad': ('prodcons.c', ['-DBAD_LOCK_ORDER=1']),
    'condvar': ('condvar.c', []),
    'condvar_if': ('condvar.c', ['-DUSE_IF=1']),
    'readers': ('readers.c', []),
    'deadlock_fixed': ('deadlock.c', []),
    'deadlock_original': ('deadlock.c', ['-DOPPOSITE_ORDER=1']),
    'deadlock_nosleep': ('deadlock.c', ['-DOPPOSITE_ORDER=1', '-DDELAY_SECONDS=0']),
}
with (out / 'environment.txt').open('w') as log:
    log.write(Path('/etc/os-release').read_text())
    log.write('\n' + platform.platform() + '\n')
    log.write('CPU affinity: ' + str(sorted(os.sched_getaffinity(0))) + '\n')
    for command in [['gcc', '--version'], ['timeout', '--version']]:
        log.write('\n$ ' + ' '.join(command) + '\n')
        log.flush()
        subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=True)
with (out / 'build.txt').open('w') as log:
    for name, (source, definitions) in variants.items():
        command = ['gcc', '-std=c11', '-Wall', '-Wextra', '-Werror', '-O0', '-pthread',
                   *definitions, '-o', str(bin_dir / name), str(code / source)]
        log.write('$ ' + ' '.join(command) + '\n')
        log.flush()
        subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=True)

records = []
for name in variants:
    repetitions = 10 if name == 'deadlock_nosleep' else (1 if name in ['prodcons_bad', 'deadlock_original'] else 3)
    for index in range(1, repetitions + 1):
        command = ['timeout', '--kill-after=1s', '5s', str(bin_dir / name)]
        start = time.perf_counter()
        result = subprocess.run(command, capture_output=True, text=True, timeout=8)
        elapsed = time.perf_counter() - start
        prefix = out / f'{name}-{index}'
        prefix.with_suffix('.stdout').write_text(result.stdout)
        prefix.with_suffix('.stderr').write_text(result.stderr)
        record = {'program': name, 'run': index, 'command': command,
                  'returncode': result.returncode, 'wall_seconds': elapsed,
                  'stdout': result.stdout, 'stderr': result.stderr}
        records.append(record)
        (out / 'runs.json').write_text(json.dumps(records, indent=2) + '\n')
        print(f'{name} #{index}: exit {result.returncode}, {elapsed:.6f} seconds', flush=True)
        allowed = (0, 124) if name in ['prodcons_bad', 'deadlock_original', 'deadlock_nosleep'] else (0,)
        if result.returncode not in allowed or result.stderr:
            raise RuntimeError(f'Unexpected result: {record}')

for name in variants:
    sections = []
    for r in records:
        if r['program'] == name:
            sections.append(f"$ timeout 5 ./{name}  # run {r['run']}\n{r['stdout']}exit code: {r['returncode']}\n")
    (out / (name + '.txt')).write_text('\n'.join(sections))
(out / 'outcomes.csv').write_text('program,run,exit_code,wall_seconds\n' + '\n'.join(
    f"{r['program']},{r['run']},{r['returncode']},{r['wall_seconds']:.6f}" for r in records) + '\n')
subprocess.run(['python3', str(code / 'verify.py')], check=True)
