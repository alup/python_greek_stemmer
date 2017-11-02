#!/usr/bin/env python

from os import path
from codecs import open

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='greek_stemmer',
    version='0.1.1',
    description='Python Greek stemmer.',
    long_description=long_description,
    author='Andreas Loupasakis',
    author_email='alup@skroutz.gr',
    url='https://github.com/alup/python_greek_stemmer',
    packages=['greek_stemmer'],
    package_data={'': ['LICENSE']},
    include_package_data=True,
    install_requires=['PyYAML', 'future'],
    license='MIT',
    zip_safe=False,
    classifiers=(
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5'
    ),
    keywords='stemmer greek nlp',
    extras_require={
        'test': ['pytest'],
    },
)
