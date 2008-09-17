#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name = 'moxie',
    version = '8.10',

    packages = find_packages(),
    package_data = {
        'moxie': ['templates/*', 'static/*'],
    },

    install_requires = [
        'flup',
        'Mako',
        'Markdown >= 1.7',
        'mutagen >= 1.14',
        'selector',
        'static',
        'WebOb',
    ],
    dependency_links = [
        # mutagen
        "http://code.google.com/p/quodlibet/downloads/list",
    ],

    entry_points = {
        'console_scripts': [
            'moxie-test = moxie.deploy:local',
        ]
    },

    test_suite = 'nose.collector',
)
