import sys
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

source, output = map(Path, sys.argv[1:3])
with ZipFile(output, 'w', ZIP_DEFLATED) as archive:
    for file in source.rglob('*'):
        if file.is_file():
            archive.write(file, file.relative_to(source).as_posix())
