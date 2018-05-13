# Zhenpeng Zhou <zhenp3ngzhou cir{a} gmail dot com>
# Fri Nov 17 2017
import os

from setuptools import setup

CURRENT_DIR = os.path.dirname(__file__)
with open(os.path.join(CURRENT_DIR, 'readme.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
  name = 'sifreader',
  packages = ['sifreader'],
  version = '0.2.1',
  install_requires = ['numpy'],
  description = 'A library to read Andor SIF file',
  long_description = long_description,
  author = 'Zhenpeng Zhou and Daniel R. Stephan',
  author_email = 'zhenp3ngzhou@gmail.com',
  url = 'https://github.com/lightingghost/sifreader',
  download_url = 'https://github.com/lightingghost/sifreader/archive/0.2.1.tar.gz',
  keywords = ['SIF', 'Andor', 'Image', 'reader'],
  classifiers = ['Development Status :: 3 - Alpha'],
)
