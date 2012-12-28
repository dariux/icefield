import os
import sys
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "icefield",
    version = "0.1.0",
    author = "Darius Braziunas",
    author_email = "darius.braziunas@gmail.com",
    description = "Python Glacier client for large files",
    license = "MIT",
    keywords = "aws glacier backup restore archive python concurrent",
    url = "https://github.com/dariux/icefield",
    py_modules=['icefield'],
    long_description= read('README.md'),
    install_requires=["aaargh", "boto"],
    entry_points={'console_scripts': ["icefield = icefield:main"]},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: System :: Archiving :: Backup",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
    ],
    scripts=["icefield.py"],
    zip_safe=False,
)
