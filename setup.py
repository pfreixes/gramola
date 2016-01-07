#!/usr/bin/env python

from setuptools import setup
#from distutils.core import setup
 
setup(
    name='Gramola',
    version='0.0.1a0',
    packages=['gramola', ],
    license='BSD',
    description='Gramola is a console port of Grafana_ that uses sparklines_ to render time series data points.',
    long_description=open('README.rst').read(),
    author='Pau Freixes',
    author_email='pfreixes@gmail.com',
    entry_points={
        'console_scripts': [
            'gramola = gramola.commands:gramola',
        ]
    }
)
