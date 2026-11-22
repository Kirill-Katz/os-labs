"""Compile and run every experiment without optimization; retain actual evidence."""
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
flags = ['-std=c11', '-Wall', '-Wextra', '-Werror', '-O0', '-pthread']
variants = {
    'race': ('race.c', []),
    'mutex': ('mutex.c', []),
    'sem': ('sem.c', []),
    'sem_two': ('sem.c', ['-DSEM_START=2']),
    'order': ('order.c', []),
    'order_one': ('order.c', ['-DREADY_START=1']),
    'parking': ('parking.c', []),
    'parking_one': ('parking.c', ['-DPLACES=1']),
    'atomic': ('atomic.c', []),
}
with (out / 'environment.txt').open('w') as log:
    log.write(Path('/etc/os-release').read_text())
    log.write('\n' + platform.platform() + '\n')
    log.write('CPU affinity: ' + str(sorted(os.sched_getaffinity(0))) + '\n')
    for command in [['gcc', '--version'], ['/usr/bin/time', '--version'], ['getconf', '_NPROCESSORS_ONLN']]:
        log.write('\n$ ' + ' '.join(command) + '\n')
        log.flush()
        subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=True)

with (out / 'build.txt').open('w') as log:
    for name, (source, definitions) in variants.items():
        command = ['gcc', *flags, *definitions, '-o', str(bin_dir / name), str(code / source)]
        log.write('$ ' + ' '.join(command) + '\n')
        log.flush()
        subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=True)

records = []

def run(name, index):
    prefix = out / f'{name}-{index}'
    command = ['/usr/bin/time', '-f', 'real_s=%e user_s=%U system_s=%S',
               '-o', str(prefix.with_suffix('.time')), str(bin_dir / name)]
    start = time.perf_counter()
    result = subprocess.run(command, text=True, capture_output=True, timeout=30)
    wall = time.perf_counter() - start
    prefix.with_suffix('.stdout').write_text(result.stdout)
    prefix.with_suffix('.stderr').write_text(result.stderr)
    record = {'program': name, 'run': index, 'returncode': result.returncode,
              'wall_seconds': wall, 'stdout': result.stdout, 'stderr': result.stderr,
              'time': prefix.with_suffix('.time').read_text().strip()}
    records.append(record)
    (out / 'runs.json').write_text(json.dumps(records, indent=2) + '\n')
    if result.returncode != 0 or result.stderr:
        raise RuntimeError(f'{name} run {index} failed: {result}')
    print(f'{name} run {index}: {wall:.6f} s', flush=True)

for name in variants:
    for index in range(1, 4):
        run(name, index)
    # A data race can accidentally give the right number. Retry, never fake a loss.
    if name in ('race', 'sem_two'):
        index = 3
        while all('counter = 2000000 ' in r['stdout'] for r in records if r['program'] == name) and index < 20:
            index += 1
            run(name, index)

summary = ['program,run,wall_seconds,gnu_time']
for record in records:
    summary.append(f"{record['program']},{record['run']},{record['wall_seconds']:.6f},{record['time']}")
(out / 'timings.csv').write_text('\n'.join(summary) + '\n')
for name in variants:
    output = []
    for r in records:
        if r['program'] == name:
            output.append(f"$ ./{name}  # run {r['run']}\n{r['stdout']}")
    (out / (name + '.txt')).write_text('\n'.join(output))
subprocess.run(['python3', str(code / 'verify.py')], check=True)
