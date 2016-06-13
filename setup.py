#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
janitoo-flask
--------------

"""
from os import name as os_name
from setuptools import setup, find_packages
from platform import system as platform_system
import glob
import os
import sys
from _version import janitoo_version

def get_data_files(res, rsrc, src, pattern):
    for root, dirs, fils in os.walk(src):
        if src == root:
            sub = []
            for fil in fils:
                sub.append(os.path.join(root,fil))
            res.append((rsrc, sub))
            for dire in dirs:
                get_data_files(res, os.path.join(rsrc, dire), os.path.join(root, dire), pattern)
    return res

data_files = []
get_data_files(data_files, 'docs','src/docs/','*')

def get_package_data(res, pkgdir, src, pattern):
    for root, dirs, fils in os.walk(os.path.join(pkgdir, src)):
        #~ print os.path.join(pkgdir, src), root, dirs, fils
        if os.path.join(pkgdir, src) == root:
            sub = []
            for fil in fils:
                sub.append(os.path.join(src,fil))
            res.extend(sub)
            for dire in dirs:
                get_package_data(res, pkgdir, os.path.join(src, dire), pattern)
    return res

package_data = []
get_package_data(package_data, 'src', 'images','*')

setup(
    name='janitoo_tkinter',
    version=janitoo_version,
    url='http://github.com/bibi21000/janitoo_tkinter/',
    author='Sébastien GALLET aka bibi2100 <bibi21000@gmail.com>',
    author_email='bibi21000@gmail.com',
    license = """
        This file is part of Janitoo.

        Janitoo is free software: you can redistribute it and/or modify
        it under the terms of the GNU General Public License as published by
        the Free Software Foundation, either version 3 of the License, or
        (at your option) any later version.

        Janitoo is distributed in the hope that it will be useful,
        but WITHOUT ANY WARRANTY; without even the implied warranty of
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
        GNU General Public License for more details.

        You should have received a copy of the GNU General Public License
        along with Janitoo. If not, see <http://www.gnu.org/licenses/>.
    """,
    description="The tkinter extension to build apps for janitoo",
    long_description=__doc__,
    packages = find_packages('src', exclude=["scripts", "docs", "config"]),
    scripts=['src/scripts/jnt_tkui'],
    zip_safe=False,
    keywords = "core,ui",
    package_dir = { '': 'src' },
    platforms='any',
    include_package_data=True,
    data_files = data_files,
    package_data={
            'janitoo_tkinter': package_data,
        },
    install_requires=[
        'janitoo',
        'janitoo_factory',
        'pyttk',
        'Pillow',
    ],
    dependency_links = [
      'https://github.com/bibi21000/janitoo/archive/master.zip#egg=janitoo',
      'https://github.com/bibi21000/janitoo_factory/archive/master.zip#egg=janitoo_factory',
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    tests_require=['janitoo_nosetests'],
)
