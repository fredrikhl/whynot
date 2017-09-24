#!/usr/bin/env python
# encoding: utf-8
from setuptools import setup, find_packages

setup(
    name='whynot',
    author='Fredrik Larsen',
    author_email='fredrik.h.larsen@gmail.com',
    # url='https://github.com/fredrikhl/whynot',
    description="Simple port of MATLAB's 'why' function.",
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    entry_points={
        'console_scripts': ['whynot = whynot.__main__:main', ],
    },
    data_files=[
        ('usr/share', ['data/example.cfg', ]),
    ],
    # license='GPL',
    packages=find_packages(),
)
