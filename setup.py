#!/usr/bin/env python
from setuptools import setup, find_packages

setup(name='MyTile',
      version='0.1',
      description='Tiles windows',
      author='Jonas Pfannschmidt',
      author_email='jonas.pfannschmidt@gmail.com',
      packages=['mytile'],
      install_requires=[
          'docopt',
          'sarge'
      ],
      entry_points={
          'console_scripts': ['mytile = mytile:main']
      }
     )
