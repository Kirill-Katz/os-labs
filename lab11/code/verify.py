"""Check semantic invariants in retained output, without assuming a car order."""
from pathlib import Path
import json
import re

lab = Path(__file__).resolve().parent.parent
out = lab / 'report_files/output'
records = json.loads((out / 'runs.json').read_text())
checks = []

def check(ok, description):
    if not ok:
        raise AssertionError(description)
    checks.append('PASS: ' + description)

def runs(name):
    found = [r for r in records if r['program'] == name]
    check(len(found) >= 3, name + ': at least three runs recorded')
    return found

for r in records:
    check(r['returncode'] == 0 and r['stderr'] == '', f"{r['program']} #{r['run']}: successful exit without diagnostics")
    check((out / f"{r['program']}-{r['run']}.stdout").read_text() == r['stdout'],
          f"{r['program']} #{r['run']}: raw stdout matches record")

for name in ['race', 'sem_two', 'mutex', 'sem', 'atomic']:
    group = runs(name)
    counters = []
    for r in group:
        match = re.fullmatch(r'counter = (\d+) \(expected 2000000\)\n', r['stdout'])
        check(match is not None, f"{name} #{r['run']}: expected output format")
        counters.append(int(match.group(1)))
    if name in ('race', 'sem_two'):
        # This is evidence of these runs, not a guarantee about C data races.
        check(any(n != 2000000 for n in counters), name + ': observed an incorrect result')
    else:
        check(all(n == 2000000 for n in counters), name + ': every run reached exactly 2000000')

for r in runs('order'):
    lines = r['stdout'].splitlines()
    check(sorted(lines) == sorted(['B: waiting for the message...', 'A: message written', 'B: I read "hello"'])
          and lines.index('A: message written') < lines.index('B: I read "hello"'),
          f"order #{r['run']}: read hello only after writer announcement")
for r in runs('order_one'):
    check('A: message written' in r['stdout'] and 'B: I read ' in r['stdout'],
          f"order_one #{r['run']}: altered-start experiment completed")

for name, capacity in [('parking', 3), ('parking_one', 1)]:
    for r in runs(name):
        inside = set()
        entered = set()
        left = set()
        maximum = 0
        lines = r['stdout'].splitlines()
        check(len(lines) == 12, f"{name} #{r['run']}: exactly twelve events")
        for line in lines:
            match = re.fullmatch(r'car (\d+) (enters|leaves) \(inside: (\d+)\)', line)
            check(match is not None, f"{name} #{r['run']}: valid event: {line}")
            car, event, reported = match.groups()
            car, reported = int(car), int(reported)
            check(1 <= car <= 6, 'valid car ID')
            if event == 'enters':
                check(car not in entered and car not in inside, f'car {car} enters once')
                entered.add(car)
                inside.add(car)
            else:
                check(car in inside and car not in left, f'car {car} leaves only after entering')
                inside.remove(car)
                left.add(car)
            check(reported == len(inside) and 0 <= reported <= capacity,
                  f"{name} #{r['run']}: occupancy agrees with events and capacity")
            maximum = max(maximum, reported)
        check(not inside and entered == left == set(range(1, 7)),
              f"{name} #{r['run']}: all six cars leave and occupancy returns to zero")
        checks.append(f"OBSERVED: {name} #{r['run']} maximum occupancy {maximum}")

(out / 'verification.txt').write_text('\n'.join(checks) + '\n')
print(f"All {sum(line.startswith('PASS:') for line in checks)} assertions passed across {len(records)} executions.")
