# Zhenpeng Zhou <zhenp3ngzhou cir{a} gmail dot com>
# Fri Nov 17 2017


from distutils.core import setup
setup(
  name = 'sifreader',
  packages = ['sifreader'],
  version = '0.1',
  install_requires=['numpy'],
  description = 'A library to read Andor SIF file',
  author = 'Zhenpeng Zhou',
  author_email = 'zhenp3ngzhou@gmail.com',
  url = 'https://github.com/lightingghost/sifreader',
  download_url = 'https://github.com/lightingghost/sifreader/archive/0.1.tar.gz',
  keywords = ['SIF', 'Andor', 'Image', 'reader'],
  classifiers = [],
)
