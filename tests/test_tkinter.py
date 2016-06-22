# -*- coding: utf-8 -*-

"""Unittests for flask.
"""
__license__ = """
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

"""
__author__ = 'Sébastien GALLET aka bibi21000'
__email__ = 'bibi21000@gmail.com'
__copyright__ = "Copyright © 2013-2014-2015-2016 Sébastien GALLET aka bibi21000"

import sys, os
import time, datetime
import unittest

from janitoo.utils import json_dumps, json_loads
from janitoo.utils import HADD_SEP, HADD
from janitoo.utils import TOPIC_HEARTBEAT
from janitoo.utils import TOPIC_NODES, TOPIC_NODES_REPLY, TOPIC_NODES_REQUEST
from janitoo.utils import TOPIC_BROADCAST_REPLY, TOPIC_BROADCAST_REQUEST
from janitoo.utils import TOPIC_VALUES_USER, TOPIC_VALUES_CONFIG, TOPIC_VALUES_SYSTEM, TOPIC_VALUES_BASIC

from janitoo.options import JNTOptions

from janitoo_tkinter import JanitooTk

from janitoo_nosetests.tkinter import JNTTTkinter

class TestTkinter(JNTTTkinter):
    """Test tkinter
    """

    client_conf = "tests/data/janitoo_tkui.conf"

    def test_001_create_root(self):
        self.assertNotEqual(None, self.root)

    def test_021_extend_network(self):
        self.root.extend_network('janitoo_test')

    def test_022_extend_listener(self):
        self.root.extend_listener('janitoo_test')

    def test_051_start_stop_listener(self):
        try:
            self.root.start_listener()
            time.sleep(60.0)
            print("Network nodes %s"%self.root.network.nodes)
            self.assertEqual(len(self.root.network.nodes), 1)
            print("Network systems %s"%self.root.network.systems)
            self.assertEqual(len(self.root.network.systems), 1)
            print("Network basics %s"%self.root.network.basics)
            self.assertEqual(len(self.root.network.basics), 1)
            print("Network users %s"%self.root.network.users)
            self.assertEqual(len(self.root.network.users), 0)
            print("Network configs %s"%self.root.network.configs)
            self.assertEqual(len(self.root.network.configs), 1)
            print("Network commands %s"%self.root.network.commands)
            self.assertEqual(len(self.root.network.commands), 0)
        finally:
            self.root.stop_listener()
        self.assertTrue(False)
