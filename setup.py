import sys
if sys.version_info[0] < 3:
    print("Python version detected:\n*****\n{0!s}\n*****\nCannot run, must be using Python 3".format(sys.version))
    sys.exit()

from setuptools import setup, find_packages
from glob import glob


def find_scripts(pkgs):
    ret = []
    for pkgname in pkgs:
        ret.extend(glob(pkgname + '/scripts/*.py'))
    return ret


pkgs = find_packages()
scripts = find_scripts(pkgs)


setup(
    name='a107',
    packages=find_packages(),
    include_package_data=True,
    version='18.10.17.0',
    license='GNU GPLv3',
    platforms='any',
    description='A multi-purpose API in Python',
    author='Julio Trevisan',
    author_email='juliotrevisan@gmail.com',
    url='https://github.com/trevisanj/a107',
    keywords= ['debugging', 'introspection', 'file', 'search',
               'conversion', 'datetime', 'config', 'text',
               ],
    install_requires=[],
    scripts=scripts
)
