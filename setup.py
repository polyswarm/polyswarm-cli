#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import find_packages, setup

# The README.md will be used as the content for the PyPi package details page on the Python Package Index.
with open('README.md', 'r') as readme:
    long_description = readme.read()


setup(
    name='polyswarm',
    version='3.6.0',
    description='CLI for using the PolySwarm Customer APIs',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='PolySwarm Developers',
    author_email='info@polyswarm.io',
    url='https://github.com/polyswarm/polyswarm-cli',
    license='MIT',
    python_requires='>=3.7,<4',
    install_requires=[
        'polyswarm-api~=3.7.0.dev',
        'click~=7.1',
        'colorama~=0.4.6',
        'click-log~=0.4.0',
        'pygments~=2.17.2',
    ],
    extras_require={
        'yara': ['yara-python==3.11.0'],
    },
    include_package_data=True,
    packages=find_packages('src'),
    package_dir={'': 'src'},
    entry_points={
        'console_scripts': [
            'polyswarm=polyswarm.__main__:polyswarm_cli',
        ],
    },
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
)
