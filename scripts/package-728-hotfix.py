"""Rebuild the v6.4.3 self-extracting archive with the fork's Windows server."""
import sys
from copy import copy
from pathlib import Path
from shutil import copyfileobj
from zipfile import ZipFile


def package(base: Path, stub: Path, server: Path, output: Path) -> None:
    server_entry = 'NapCat-QCE-Windows-x64/qce-server.exe'
    binary = server.read_bytes()
    with base.open('rb') as original, ZipFile(original) as source:
        if source.namelist().count(server_entry) != 1:
            raise ValueError('Expected one bundled server')
        with output.open('xb') as installer:
            with stub.open('rb') as launcher:
                copyfileobj(launcher, installer)
            with ZipFile(installer, 'w') as bundle:
                for entry in source.infolist():
                    if entry.filename == server_entry:
                        bundle.writestr(copy(entry), binary)
                    else:
                        with source.open(entry) as src, bundle.open(copy(entry), 'w') as dst:
                            copyfileobj(src, dst)
    with ZipFile(output) as bundle:
        if bundle.testzip() is not None or bundle.read(server_entry) != binary:
            raise ValueError('Embedded installer payload failed verification')


if __name__ == '__main__':
    package(*(Path(arg) for arg in sys.argv[1:]))
