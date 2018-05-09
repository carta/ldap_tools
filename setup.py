#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Note: To use the 'upload' functionality of this file, you must:
#   $ pip install twine

import io
import re
from glob import glob
from os.path import basename
from os.path import dirname
from os.path import join
from os.path import splitext

from setuptools import find_packages
from setuptools import setup


def read(*names, **kwargs):
    return io.open(
        join(dirname(__file__), *names),
        encoding=kwargs.get('encoding', 'utf8')).read()


setup(
    name='ldap_tools',
    version='0.7.11',
    license='MIT',
    description=(
        'A set of tools to make managing LDAP users, groups, and keys easier'),
    long_description='{}\n{}'.format(
        re.compile('^.. start-badges.*^.. end-badges', re.M | re.S).sub(
            '', read('README.rst')),  # Remove badges from long_description
        re.sub(':[a-z]+:`~?(.*?)`', r'``\1``', read('CHANGELOG.rst'))),
    author='Ali Tayarani',
    author_email='ali.tayarani@carta.com',
    url='https://github.com/carta/ldap_tools',
    packages=find_packages('src'),
    package_dir={'': 'src'},  # src/ is the root of the package
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha', 'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English', 'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX :: Linux', 'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Topic :: System :: Systems Administration :: Authentication/Directory :: LDAP',
        'Topic :: Utilities'
    ],
    keywords=[],
    install_requires=['ldap3', 'click', 'sshpubkeys', 'pyyaml'],
    entry_points={
        'console_scripts': ['ldaptools=ldap_tools.commands:main']
    })
