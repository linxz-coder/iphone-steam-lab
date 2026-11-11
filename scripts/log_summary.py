#!/usr/bin/env python3
"""Read a Madeira log locally; output only allowlisted diagnostic fields, never raw lines."""
import argparse
import json
from pathlib import Path
import re


def summarize(text):
    result = {'jit_pool_ready': 'JIT pool ready' in text,
              'debugger_detached': 'Debugger detached.' in text,
              'online_authenticated': 'session-authenticated-online=1' in text,
              'game_window_observed': 'end reason=game-window' in text,
              'safe_exit_observed': 'quit-upload done' in text and 'closing Madeira' in text,
              'launch_client_error': None, 'cloud': {}}
    for line in text.splitlines():
        error = re.search(r'launch-client-error=(\d+)\b', line)
        if error:
            result['launch_client_error'] = int(error[1])
        app = re.search(r'\[steam-cloud\] app=(\d+)\b', line)
        if app and 'cloud-files=' in line:
            fields = {}
            for name in ['cloud-files', 'same', 'differ', 'missing-local', 'local-only', 'unmapped', 'download', 'upload', 'ask']:
                match = re.search(r'(?<![\w-])' + name + r'=(\d+)\b', line)
                if match:
                    fields[name] = int(match[1])
            result['cloud'][app[1]] = fields
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('log', type=Path)
    args = parser.parse_args()
    print(json.dumps(summarize(args.log.read_text(errors='replace')), indent=2))


if __name__ == '__main__':
    main()
