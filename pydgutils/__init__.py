'''
@date 2013-5-10

@author Hong-She Liang <starofrainnight@gmail.com>
'''

import os
import os.path
import shutil
import sys
import fnmatch
import re
import filecmp
import fnmatch
from .version import __version__

_PROCESSED_DIR = "build/downgraded_src"
_SOURCE_DIR = "src"


def _samefile(file1, file2):
    if sys.platform == 'win32':
        # it is a way more complicated, the following does not deal
        # with hard links on Windows
        # for better discussion see
        # http://stackoverflow.com/q/8892831/164233
        return os.path.normcase(os.path.normpath(file1)) == \
            os.path.normcase(os.path.normpath(file2))
    else:
        return os.path.samefile(file1, file2)


def __copy_tree(src_dir, dest_dir):
    """
    The shutil.copytree() or distutils.dir_util.copy_tree() will happen to report
    error list below if we invoke it again and again ( at least in python 2.7.4 ):

    IOError: [Errno 2] No such file or directory: ...

    So we have to write our's copy_tree() for that purpose.
    """

    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
        shutil.copystat(src_dir, dest_dir)

    for entry in os.listdir(src_dir):
        from_path = os.path.join(src_dir, entry)
        to_path = os.path.join(dest_dir, entry)
        if os.path.isdir(from_path):
            __copy_tree(from_path, to_path)
        else:
            shutil.copy2(from_path, to_path)


def remove_temporary_directories(base_dir):
    # The 'build' folder sometimes will not update! So we need to remove them
    # all !
    leave_dir = os.path.realpath(
        os.path.normpath(os.path.join(base_dir, _PROCESSED_DIR)))
    root_dir = os.path.join(base_dir, "build")
    if not os.path.exists(root_dir):
        return

    files = os.listdir(root_dir)
    is_leave_dir_existed = os.path.exists(leave_dir)
    for afile in files:
        afile_path = os.path.realpath(
            os.path.normpath(os.path.join(root_dir, afile)))
        if os.path.isdir(afile_path):
            if ((not is_leave_dir_existed)
                    or (not _samefile(afile_path, leave_dir))):
                shutil.rmtree(afile_path, ignore_errors=True)
        else:
            os.remove(afile_path)


def downgrade_files(files):
    # Check and prepare 3to2 module.
    try:
        from lib3to2.main import main as lib3to2_main
    except ImportError:
        try:
            from pip import main as pipmain
        except:
            from pip._internal import main as pipmain

        pipmain(['install', '3to2'])

        from lib3to2.main import main as lib3to2_main

    if len(files) > 0:
        options = [
            "-f",
            "all",
            # FIXME: It will trigger AssertionError: Sanity check failed: 0xFFFFFFFF
            # "-f", "int",
            "-f",
            "collections",
            "-f",
            "memoryview",
            "-f",
            "printfunction",
            "-f",
            "unittest",
            "-w",
            "-n",
            "--no-diffs",
        ]
        options += files

        lib3to2_main("lib3to2.fixes", options)


def is_path_in_filters(apath, filters):
    for afilter in filters:
        if fnmatch.fnmatch(apath, afilter):
            return True
    return False


def process(base_dir=os.curdir):
    """
    A special method for convert all source files to compatible with current
    python version during installation time (Only do convert behavior on
    python2).

    All sources of your project must be wrote in python3 syntax.

    The source directory layout must like this :

    base_dir --+
               |
               +-- src (All sources must be placed into this directory)
               |
               +-- build --+
               |           |
               |           +-- downgraded_src (Processed sources are placed into
               |               this directory)
               |
               +-- setup.py
               |
               ...

    @return Preprocessed source directory
    """
    source_path = os.path.join(base_dir, _SOURCE_DIR)
    destination_path = os.path.join(base_dir, _PROCESSED_DIR)

    if not os.path.exists(source_path):
        raise NotADirectoryError("Path not found : '%s'!" % source_path)

    remove_temporary_directories(base_dir)

    # Remove all unused directories
    directories = []
    directory_patterns = ['__pycache__', '*.egg-info']
    for root, dirs, files in os.walk(destination_path):
        for adir in dirs:
            for pattern in directory_patterns:
                if fnmatch.fnmatch(adir, pattern):
                    directories.append(os.path.join(root, adir))
                    break

    for adir in directories:
        shutil.rmtree(adir, ignore_errors=True)

    if sys.version_info[0] >= 3:
        # We wrote program implicated by version 3, if python version
        # large or equal than 3, we need not change the sources.
        return source_path

    # Remove old preprocessed sources.
    if not os.path.exists(destination_path):
        __copy_tree(source_path, destination_path)
        downgrade_files([destination_path])
    else:
        # Remove all files that only in right side
        # Copy all files that only in left side to right side, then
        # 3to2 on these files

        files = []
        dirs = []

        cmp_result = filecmp.dircmp(source_path, destination_path)
        dirs.append(cmp_result)

        dir_filters = ["__pycache__"]

        while len(dirs) > 0:

            # Get the last one compare result
            cmp_result = dirs[-1]
            del dirs[-1]

            # Append all sub-dirs compare results, so that we could
            # continue our loop.
            dirs.extend(list(cmp_result.subdirs.values()))

            # Remove all files that only in right side
            for file_name in cmp_result.right_only:
                file_path = os.path.join(cmp_result.right, file_name)
                if os.path.isdir(file_path):
                    shutil.rmtree(file_path, ignore_errors=True)
                    continue

                # Only parse files.
                try:
                    os.remove(file_path)
                except:
                    pass

            # Copy all files that only in left side to right side or
            # different files, then 3to2 on these files
            for file_name in (cmp_result.left_only + cmp_result.diff_files):
                left_file_path = os.path.join(cmp_result.left, file_name)
                right_file_path = os.path.join(cmp_result.right, file_name)

                if os.path.isdir(left_file_path):
                    __copy_tree(left_file_path, right_file_path)
                    if not is_path_in_filters(
                            os.path.basename(right_file_path), dir_filters):
                        files.append(right_file_path)
                    continue

                if not fnmatch.fnmatch(file_name, "*.py"):
                    continue

                left_file_mtime = os.stat(left_file_path).st_mtime
                right_file_mtime = 0

                if os.path.exists(right_file_path):
                    right_file_mtime = os.stat(right_file_path).st_mtime

                if left_file_mtime > right_file_mtime:
                    try:
                        os.remove(right_file_path)
                    except:
                        pass

                    shutil.copy2(left_file_path, right_file_path)
                    files.append(right_file_path)

        if len(files) > 0:
            downgrade_files(files)

    return destination_path


def process_packages(base_dir=os.curdir):
    """
    Search local packages and downgrade it if needs, then return founded
    packages and source directory.
    """
    from setuptools import find_packages

    source_dir = process(base_dir)
    packages = find_packages(where=source_dir)
    return (packages, source_dir)


def process_requirements():
    """
    Simple function to get all requirements from ./requirements.txt, so we need
    not wrote them twice!
    """

    from pip.req import parse_requirements

    # parse_requirements() returns generator of pip.req.InstallRequirement
    # objects
    requirements = parse_requirements("./requirements.txt", session=False)
    requirements = [str(ir.req) for ir in requirements]

    return requirements
