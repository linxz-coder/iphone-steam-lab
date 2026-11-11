#!/usr/bin/env python3
"""Apply a version-locked compatibility recipe to a separate copy of a game file."""
import argparse
import hashlib
import json
from pathlib import Path


def transform(original, recipe):
    if recipe['format'] != 1 or len(original) != recipe['input_bytes']:
        raise ValueError('Unsupported recipe or input size')
    if hashlib.sha256(original).hexdigest() != recipe['input_sha256']:
        raise ValueError('Input SHA-256 mismatch. Do not force this patch onto a different game build.')
    result = bytearray(original)
    end = 0
    for edit in recipe['edits']:
        offset = edit['offset']
        before, after = bytes.fromhex(edit['before']), bytes.fromhex(edit['after'])
        if offset < end or offset + len(before) > len(original) or len(before) != len(after):
            raise ValueError('Invalid or overlapping edit')
        if original[offset:offset + len(before)] != before:
            raise ValueError('Patch context mismatch')
        result[offset:offset + len(before)] = after
        end = offset + len(before)
    result.extend(bytes.fromhex(recipe.get('append', '')))
    if len(result) != recipe['output_bytes'] or hashlib.sha256(result).hexdigest() != recipe['output_sha256']:
        raise ValueError('Output verification failed')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('--recipe', type=Path, default=Path(__file__).resolve().parents[1] / 'patches/famegame2-26236662.json')
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--check', action='store_true')
    mode.add_argument('--output', type=Path)
    args = parser.parse_args()
    try:
        recipe = json.loads(args.recipe.read_text())
        result = transform(args.source.read_bytes(), recipe)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            with args.output.open('xb') as output:
                output.write(result)
    except (ValueError, OSError, KeyError) as error:
        parser.exit(1, f'{error}\n')
    print(json.dumps({'status': 'compatible' if args.check else 'built',
                      'sha256': hashlib.sha256(result).hexdigest(), 'bytes': len(result)}))


if __name__ == '__main__':
    main()
