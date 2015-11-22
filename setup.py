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

def data_files_config(target, source, pattern):
    ret = list()
    ret.append((target, glob.glob(os.path.join(source,pattern))))
    dirs = [x for x in glob.iglob(os.path.join( source, '*')) if os.path.isdir(x) ]
    for d in dirs:
        rd = d.replace(source+os.sep, "", 1)
        ret.extend(data_files_config(os.path.join(target,rd), os.path.join(source,rd), pattern))
    return ret

data_files = data_files_config('docs','src/docs','*.rst')
data_files.extend(data_files_config('docs','src/docs','*.md'))
data_files.extend(data_files_config('docs','src/docs','*.txt'))
data_files.extend(data_files_config('docs','src/docs','*.png'))
data_files.extend(data_files_config('docs','src/docs','*.jpg'))
data_files.extend(data_files_config('docs','src/docs','*.gif'))


setup(
    name='janitoo_flask',
    version=janitoo_version,
    url='http://github.com/bibi21000/janitoo_flask/',
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
    description="The flask extension to build web apps for janitoo",
    long_description=__doc__,
    packages = find_packages('src', exclude=["scripts", "docs", "config"]),
    zip_safe=False,
    keywords = "flask,web",
    include_package_data=True,
    package_dir = { '': 'src' },
    platforms='any',
    install_requires=[
        'janitoo_db >= %s'%janitoo_version,
        'Flask >= 0.9',
        'Flask-SQLAlchemy >= 1.0',
        'Flask-Script >= 0.6',
        'gevent == 1.0.1',
        'gevent-socketio >= 0.3.6',
        'Flask-SocketIO >= 0.6.0',
    ],
    dependency_links = [
      'https://github.com/bibi21000/janitoo_db/archive/master.zip#egg=janitoo_db-%s'%"0.0.7",
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
)
