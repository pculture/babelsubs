#!/usr/bin/env python

from distutils.core import setup


setup(
    name="babelsubs",
    version="0.1.0",
    description="A simple library to convert from any subtitle format to any format",
    author="Participatory Culture Foundation",
    author_email="dev+babel@pculture.org",
    url="https://github.com/pculture/babelsubs",
    license='LICENSE.txt',
    packages=['babelsubs'],
    setup_requires=['nose>=1.0'],
    install_requires=[
        'lxml==2.3',
        'html5lib==0.95',
        'wsgiref==0.1.2',
        
    ],
    dependency_links=[
        'https://github.com/jsocol/bleachmastertarball/master#egg=bleach-dev'
    ]

)
