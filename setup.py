#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import find_packages, setup


def parse_requirements():
    with open('requirements.txt', 'r') as f:
        return [r for r in f.read().splitlines() if not r.startswith('git')]


# The README.md will be used as the content for the PyPi package details page on the Python Package Index.
with open('README.md', 'r') as readme:
    long_description = readme.read()


setup(
    name='polyswarm',
    version='1.0.0',
    description='CLI for using the PolySwarm public and private APIs',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='PolySwarm Developers',
    author_email='info@polyswarm.io',
    url='https://github.com/polyswarm/polyswarm-cli',
    license='MIT',
    python_requires='>=2.7,<4',
    install_requires=parse_requirements(),
    include_package_data=True,
    packages=find_packages('src'),
    package_dir={'': 'src'},
    entry_points={
        'console_scripts': [
            'polyswarm=polyswarm.__main__:polyswarm',
        ],
    },
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: PyPy',
    ]
)
