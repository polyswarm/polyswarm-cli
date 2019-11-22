import os
import shutil
import tempfile
from contextlib import contextmanager


@contextmanager
def TemporaryDirectory():
    """The day we drop python 2.7 support we can use python 3 version of this"""
    name = tempfile.mkdtemp()
    try:
        yield name
    finally:
        shutil.rmtree(name)


@contextmanager
def temp_dir(files_dict):
    with TemporaryDirectory() as tmp_dir:
        files = []
        for file_name, file_content in files_dict.items():
            file_path = os.path.join(tmp_dir, file_name)
            mode = 'w' if isinstance(file_content, str) else 'wb'
            with open(file_path, mode=mode) as f:
                f.write(file_content)
            files.append(file_path)
        yield tmp_dir, files