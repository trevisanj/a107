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
    version='20.02.23.0',
    license='GNU GPLv3',
    platforms='any',
    description='A multi-purpose API in Python',
    author='Julio Trevisan',
    author_email='juliotrevisan@gmail.com',
    url='https://github.com/trevisanj/a107',
    keywords= ['debugging', 'introspection', 'file', 'search',
               'conversion', 'datetime', 'config', 'text', 'cryptography'
               ],
    install_requires=["colored", "numpy"],
    python_requires = '>=3',
    scripts=scripts
)
