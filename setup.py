#!/usr/bin/env python
from setuptools import setup

with open('README.rst') as f:
    readme = f.read()

setup(name="chippy",
      version="0.1.0",
      author="Benjamin Moran",
      author_email="benmoran56@gmail.com",
      description="A pure Python module for creating various chiptune style waveforms",
      license="MIT",
      keywords="audio synthesizer chiptune",
      url="https://github.com/benmoran56/chippy",
      packages=['chippy'],
      long_description=readme,
      classifiers=["Topic :: Utilities",
                   "Development Status :: 4 - Beta",
                   "License :: OSI Approved :: MIT License",
                   "Operating System :: OS Independent",
                   "Programming Language :: Python",
                   "Programming Language :: Python :: 3"],
      )
