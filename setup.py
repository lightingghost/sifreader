# Zhenpeng Zhou <zhenp3ngzhou cir{a} gmail dot com>
# Fri Nov 17 2017


from setuptools import setup

setup(
  name = 'sifreader',
  packages = ['sifreader'],
  version = '0.2',
  install_requires=['numpy'],
  description = 'A library to read Andor SIF file',
  author = 'Zhenpeng Zhou and Daniel R. Stephan',
  author_email = 'zhenp3ngzhou@gmail.com',
  url = 'https://github.com/lightingghost/sifreader',
  download_url = 'https://github.com/lightingghost/sifreader/archive/0.2.tar.gz',
  keywords = ['SIF', 'Andor', 'Image', 'reader'],
  classifiers = [],
)
