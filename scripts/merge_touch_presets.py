#!/usr/bin/env python3
"""Merge custom layouts into a NEW file, preserving existing layouts."""
import argparse
import json
from pathlib import Path


def merge(current, incoming):
    if current.get('version') != 1 or incoming.get('version') != 1:
        raise ValueError('Only Madeira preset format version 1 is supported')
    result = json.loads(json.dumps(current))
    existing = result['presets']
    for preset in incoming['presets']:
        matches = [p for p in existing if p['id'] == preset['id'] or p['name'] == preset['name']]
        if matches and matches != [preset]:
            raise ValueError(f'Existing layout differs: {preset["name"]}; resolve it manually')
        if not matches:
            existing.append(preset)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('current', type=Path, help='Copy of your current madeira-control-presets.json')
    parser.add_argument('--incoming', type=Path, default=Path(__file__).resolve().parents[1] / 'configs/touch-presets.json')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        result = merge(json.loads(args.current.read_text()), json.loads(args.incoming.read_text()))
        with args.output.open('x') as file:
            file.write(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    except (OSError, ValueError, KeyError) as error:
        parser.exit(1, f'{error}\n')
    print(f'Wrote {len(result["presets"])} layouts to a new file')


if __name__ == '__main__':
    main()
