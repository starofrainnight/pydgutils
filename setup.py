#!/usr/bin/env python

from pydgutils_bootstrap import use_pip
use_pip()

import sys
import shutil
import os
from setuptools import setup, find_packages

package_name = "pydgutils"

our_packages = find_packages()

long_description = (
    open("README.rst", "r").read() + "\n" + open("CHANGES.rst", "r").read())

install_requires = []

# Only require 3to2 package on python2
if sys.version_info[0] <= 2:
    install_requires.append("3to2")

# The 'build' folder sometimes will not update! So we need to remove them all !
shutil.rmtree(os.path.join(os.curdir, 'build'), ignore_errors=True)

setup(
    name=package_name,
    version='0.0.15',
    author="Hong-She Liang",
    author_email="starofrainnight@gmail.com",
    url="https://github.com/starofrainnight/%s" % package_name,
    description=
    "A library use for downgrade sources to python2 syntax during setup",
    long_description=long_description,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Software Development :: Libraries",
    ],
    install_requires=install_requires,
    packages=our_packages,
)
