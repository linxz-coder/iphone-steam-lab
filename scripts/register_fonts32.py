#!/usr/bin/env python3
"""Copy existing YaHei/SimSun registrations to Wine's 32-bit key in a NEW file."""
import argparse
from pathlib import Path
import re

SOURCE = r'[Software\\Microsoft\\Windows NT\\CurrentVersion\\Fonts]'
TARGET = r'[Software\\Wow6432Node\\Microsoft\\Windows NT\\CurrentVersion\\Fonts]'


def update(text):
    sections = re.split(r'(?=^\[)', text, flags=re.M)
    sources = [s for s in sections if s.startswith(SOURCE)]
    targets = [i for i, s in enumerate(sections) if s.startswith(TARGET)]
    if len(sources) != 1 or len(targets) != 1:
        raise ValueError('Expected exactly one 64-bit and one 32-bit Wine Fonts section')
    entries = [line for line in sources[0].splitlines()
               if line.startswith('"') and any(name in line.lower() for name in ('msyh.ttc', 'simsun.ttc'))]
    if not entries:
        raise ValueError('No existing YaHei/SimSun registrations; obtain and register licensed fonts first')
    index = targets[0]
    existing = {line.split('=', 1)[0]: line for line in sections[index].splitlines() if line.startswith('"') and '=' in line}
    added = []
    for line in entries:
        key = line.split('=', 1)[0]
        if key in existing and existing[key] != line:
            raise ValueError(f'Conflicting 32-bit font registration: {key}')
        if key not in existing:
            added.append(line)
            existing[key] = line
    if added:
        sections[index] = sections[index].rstrip() + '\n' + '\n'.join(added) + '\n\n'
    return ''.join(sections), len(added)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        result, count = update(args.source.read_text())
        with args.output.open('x') as file:
            file.write(result)
    except (OSError, ValueError) as error:
        parser.exit(1, f'{error}\n')
    print(f'Added {count} registrations; source file was not modified')


if __name__ == '__main__':
    main()
