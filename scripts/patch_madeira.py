#!/usr/bin/env python3
"""Reproduce the tested Madeira 0.2.0 VA-floor edit; never modify the input IPA."""
import argparse
import hashlib
import json
from pathlib import Path
import plistlib
import shutil
import zipfile

EXE = 'Payload/Madeira.app/Madeira'
INFO = 'Payload/Madeira.app/Info.plist'
ORIGINAL = '33962cb2919c6ef0cdc6ef036e90eabdd79be3902f3284d1c603c894fa97205f'
PATCHED = '4360a867fe5126d9ebfc1917e38ae1d339e1ee484a9fe2460faf897f481fa84e'
OFFSET = 0xA50E3C


def prepare(source):
    with zipfile.ZipFile(source) as archive:
        if len(archive.namelist()) != len(set(archive.namelist())):
            raise ValueError('IPA contains duplicate entries')
        original = archive.read(EXE)
        info = plistlib.loads(archive.read(INFO))
    if hashlib.sha256(original).hexdigest() != ORIGINAL:
        raise ValueError('Wrong Madeira executable SHA-256; this patch only supports the tested 0.2.0 build')
    if (info.get('CFBundleIdentifier'), info.get('CFBundleShortVersionString')) != ('com.willfaust.madeora', '0.2.0'):
        raise ValueError('Unexpected bundle or version')
    if original[OFFSET - 8:OFFSET + 8].hex() != 'a8ab00d02900a05209fd06f909000014':
        raise ValueError('Instruction context does not match')
    patched = bytearray(original)
    patched[OFFSET:OFFSET + 4] = bytes.fromhex('1f2003d5')
    if hashlib.sha256(patched).hexdigest() != PATCHED:
        raise ValueError('Patched executable failed the reference hash check')
    info['MadeiraBuild'] = '0.2.0-local-va-floor-test1'
    return patched, plistlib.dumps(info, fmt=plistlib.FMT_BINARY)


def build(source, output):
    patched, info = prepare(source)
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive creation: an existing package, symlink or source can never be overwritten.
    with output.open('xb') as file:
        try:
            with zipfile.ZipFile(source) as src, zipfile.ZipFile(file, 'w', allowZip64=True) as dst:
                for entry in src.infolist():
                    if entry.filename == EXE:
                        dst.writestr(entry, patched)
                    elif entry.filename == INFO:
                        dst.writestr(entry, info)
                    else:
                        with src.open(entry) as reader, dst.open(entry, 'w', force_zip64=True) as writer:
                            shutil.copyfileobj(reader, writer, 8 * 1024 * 1024)
            file.flush()
            with zipfile.ZipFile(output) as check:
                if check.testzip() is not None or hashlib.sha256(check.read(EXE)).hexdigest() != PATCHED:
                    raise ValueError('Output IPA verification failed')
        except BaseException:
            output.unlink(missing_ok=True)
            raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--check', action='store_true')
    mode.add_argument('--output', type=Path)
    args = parser.parse_args()
    try:
        if args.check:
            prepare(args.source)
        else:
            build(args.source, args.output)
    except (ValueError, OSError, KeyError, zipfile.BadZipFile) as error:
        parser.exit(1, f'{error}\n')
    print(json.dumps({'status': 'compatible' if args.check else 'built',
                      'executable_sha256': PATCHED, 'requires_resigning': True}))


if __name__ == '__main__':
    main()
