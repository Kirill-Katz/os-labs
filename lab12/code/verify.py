"""Validate output as event sequences, not a particular thread schedule."""
from pathlib import Path
from collections import deque
import json
import re

lab = Path(__file__).resolve().parent.parent
out = lab / 'report_files/output'
records = json.loads((out / 'runs.json').read_text())
checks = []
observations = []

def check(ok, message):
    if not ok:
        raise AssertionError(message)
    checks.append('PASS: ' + message)

def runs(name, count):
    group = [r for r in records if r['program'] == name]
    check(len(group) == count, f'{name}: {count} executions recorded')
    return group

for r in records:
    prefix = out / f"{r['program']}-{r['run']}"
    check(prefix.with_suffix('.stdout').read_text() == r['stdout']
          and prefix.with_suffix('.stderr').read_text() == r['stderr'] == '',
          f"{r['program']} #{r['run']}: raw output matches record, no error diagnostics")

for name, count in [('prodcons', 3), ('prodcons_bad', 1)]:
    for r in runs(name, count):
        queue = deque()
        put_items, taken_items = [], []
        peak = 0
        for line in r['stdout'].splitlines():
            match = re.fullmatch(r'\s*(put|take) (\d+)\s+\(in buffer: (\d+)\)', line)
            check(match is not None, 'valid buffer event: ' + line.strip())
            action, item, occupancy = match.groups()
            item, occupancy = int(item), int(occupancy)
            if action == 'put':
                queue.append(item)
                put_items.append(item)
            else:
                check(bool(queue) and queue.popleft() == item, 'consumer removes oldest item')
                taken_items.append(item)
            check(0 <= occupancy <= 4 and occupancy == len(queue), 'occupancy matches bounded FIFO state')
            peak = max(peak, occupancy)
        if name == 'prodcons':
            check(r['returncode'] == 0 and not queue and put_items == taken_items == list(range(1, 9)),
                  f"prodcons #{r['run']}: exactly items 1..8 produced/consumed in order, final buffer empty")
        else:
            check(r['returncode'] == 124 and peak == 4 and len(taken_items) < 8,
                  'wrong producer lock order reaches capacity and times out without completion')
        observations.append(f"{name} #{r['run']}: peak buffer occupancy {peak}")

for name in ['condvar', 'condvar_if']:
    for r in runs(name, 3):
        lines = r['stdout'].splitlines()
        check(r['returncode'] == 0 and lines.count('A: message written') == 1
              and lines.count('B: I read "hello"') == 1
              and lines.index('A: message written') < lines.index('B: I read "hello"')
              and all(line in ['B: not ready, I sleep', 'A: message written', 'B: I read "hello"'] for line in lines),
              f"{name} #{r['run']}: this run reads hello after writer announcement")

for r in runs('readers', 3):
    active_readers, seen_readers, finished_readers = set(), set(), set()
    active_writer = None
    seen_writers, finished_writers = set(), set()
    value, peak = 0, 0
    for line in r['stdout'].splitlines():
        match = re.fullmatch(r'reader (\d+) reads (\d+) \(readers inside: (\d+)\)', line)
        if match:
            reader, observed, count = map(int, match.groups())
            check(reader in [1, 2, 3] and reader not in seen_readers and active_writer is None,
                  'reader enters once, with no writer active')
            active_readers.add(reader)
            seen_readers.add(reader)
            check(count == len(active_readers) and observed == value, 'reader sees protected data and accurate occupancy')
            peak = max(peak, count)
            continue
        match = re.fullmatch(r'reader (\d+) leaves \(readers inside: (\d+)\)', line)
        if match:
            reader, count = map(int, match.groups())
            check(reader in active_readers, 'reader leaves after entry')
            active_readers.remove(reader)
            finished_readers.add(reader)
            check(count == len(active_readers), 'reader departure occupancy is accurate')
            continue
        match = re.fullmatch(r'writer (\d+) writes (\d+) \(alone\)', line)
        if match:
            writer, observed = map(int, match.groups())
            check(writer in [1, 2] and writer not in seen_writers and not active_readers and active_writer is None,
                  'writer enters once, with no readers or writer active')
            seen_writers.add(writer)
            active_writer = writer
            value += 10
            check(observed == value, 'writer adds exactly ten')
            continue
        match = re.fullmatch(r'writer (\d+) leaves', line)
        if match:
            writer = int(match.group(1))
            check(active_writer == writer, 'writer leaves after exclusive interval')
            active_writer = None
            finished_writers.add(writer)
            continue
        check(line == 'final value: 20; readers remaining: 0' and not active_readers and active_writer is None,
              'valid final readers/writers summary')
    check(r['returncode'] == 0 and seen_readers == finished_readers == {1, 2, 3}
          and seen_writers == finished_writers == {1, 2} and value == 20
          and 'final value: 20; readers remaining: 0' in r['stdout'],
          f"readers #{r['run']}: all participants finish with value 20")
    observations.append(f"readers #{r['run']}: peak overlapping reader count {peak}")

for r in runs('deadlock_fixed', 3):
    lines = r['stdout'].splitlines()
    check(r['returncode'] == 0 and len(lines) == 5 and lines[-1] == 'done',
          f"fixed deadlock #{r['run']}: completes and joins both threads")
    for name in ['one', 'two']:
        check(lines.count(f'{name}: I have A, I want B') == 1 and lines.count(f'{name}: I have both') == 1
              and lines.index(f'{name}: I have A, I want B') < lines.index(f'{name}: I have both'),
              name + ': fixed acquisition order and both-lock completion logged')

original = runs('deadlock_original', 1)[0]
check(original['returncode'] == 124
      and set(original['stdout'].splitlines()) == {'one: I have A, I want B', 'two: I have B, I want A'},
      'original sleeping version reaches opposite first-lock ownership and timeout 124')
no_sleep = runs('deadlock_nosleep', 10)
for r in no_sleep:
    check(r['returncode'] in [0, 124] and (('done\n' in r['stdout']) == (r['returncode'] == 0)),
          f"no-sleep original #{r['run']}: completion or timeout recorded honestly")
observations.append(f"Original without sleeps: {sum(r['returncode'] == 0 for r in no_sleep)} completed, "
                    f"{sum(r['returncode'] == 124 for r in no_sleep)} timed out")
(out / 'observations.txt').write_text('\n'.join(observations) + '\n')
(out / 'verification.txt').write_text('\n'.join(checks) + '\n')
print(f'All {len(checks)} assertions passed across {len(records)} executions.')
print('\n'.join(observations))
