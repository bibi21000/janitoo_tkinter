# -*- coding: utf-8 -*-

"""A TKinter extension to build an UI for Janitoo.

Communication between the network and tkinter :

Define Vars in network :

.. code:: python

    import Tkinter as tk

    class Network(JNTNetwork):
        def __init__(self, stop_event, options, **kwargs):
            JNTNetwork.__init__(self, stop_event, options, **kwargs)
            self.extend_from_entry_points('janitoo_tkinter')
            self.var_state = tk.StringVar()
            self.var_state_str = tk.StringVar()
            self.var_nodes_count = tk.IntVar()
            self.var_home_id = tk.StringVar()
            self.var_is_failed = tk.BooleanVar()
            self.var_is_secondary = tk.BooleanVar()
            self.var_is_primary = tk.BooleanVar()

finished in :

.. code:: bash

    Exception RuntimeError: 'main thread is not in main loop' in <bound method StringVar.__del__ of <Tkinter.StringVar instance at 0x7f7b9233ea70>> ignored
    Exception RuntimeError: 'main thread is not in main loop' in <bound method StringVar.__del__ of <Tkinter.StringVar instance at 0x7f7b9233eb90>> ignored
    Exception RuntimeError: 'main thread is not in main loop' in <bound method IntVar.__del__ of <Tkinter.IntVar instance at 0x7f7b9233ebd8>> ignored
    Exception RuntimeError: 'main thread is not in main loop' in <bound method StringVar.__del__ of <Tkinter.StringVar instance at 0x7f7b9233ec20>> ignored
    Exception RuntimeError: 'main thread is not in main loop' in <bound method BooleanVar.__del__ of <Tkinter.BooleanVar instance at 0x7f7b9233ec68>> ignored
    Exception RuntimeError: 'main thread is not in main loop' in <bound method BooleanVar.__del__ of <Tkinter.BooleanVar instance at 0x7f7b9233ecb0>> ignored
    Exception RuntimeError: 'main thread is not in main loop' in <bound method BooleanVar.__del__ of <Tkinter.BooleanVar instance at 0x7f7b9233ecf8>> ignored

==> we must define Vars in the main thread.

But it fails too if we do update from the network thread

We can do a tk recurrent function which update the networks parameters every x ms. And the same for nodes ? for values ?
Using this method, we will 1000s updates on the ui every x ms.


Using queues :

 - a queue for network updates
"""

___license__ = """
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

import logging
logger = logging.getLogger(__name__)
from logging.config import fileConfig as logging_fileConfig
import signal
import threading

import Tkinter as tk
from ttk import Frame

from pkg_resources import iter_entry_points

from janitoo_tkinter.listener import ListenerThread
from janitoo_tkinter.frame import FrameNetwork, FrameRoot

class JanitooTk(tk.Tk):

    def __init__(self, **kwargs):
        self.options = kwargs.pop('options', {})
        tk.Tk.__init__(self, **kwargs)
        if self.options is not None and 'conf_file' in self.options and self.options['conf_file'] is not None:
            logging_fileConfig(self.options['conf_file'])
        self._sleep = 0.25

        signal.signal(signal.SIGTERM, self.signal_term_handler)
        signal.signal(signal.SIGINT, self.signal_term_handler)

        self._listener_lock = threading.Lock()
        self.listener = ListenerThread(self.options, tkroot=self)
        self.network = self.listener.network
        #~ self.var_state = tk.StringVar()
        #~ self.var_state_str = tk.StringVar()
        #~ self.var_nodes_count = tk.IntVar()
        #~ self.var_home_id = tk.StringVar()
        #~ self.var_is_failed = tk.BooleanVar()
        #~ self.var_is_secondary = tk.BooleanVar()
        #~ self.var_is_primary = tk.BooleanVar()

    def __del__(self):
        """
        """
        self.network = None
        try:
            self.stop_listener()
        except Exception:
            pass

    def start_listener(self):
        """Start the listener on first call
        """
        self._listener_lock.acquire()
        try:
            if not self.listener.is_alive():
                self.listener.start()
        finally:
            self._listener_lock.release()

    def stop_listener(self):
        """Stop the listener
        """
        self._listener_lock.acquire()
        try:
            self.network = None
            self.listener.stop()
            try:
                self.listener.join()
            except RuntimeError:
                pass
        finally:
            self._listener_lock.release()

    def extend_network(self, group):
        """"Extend the network with methods found in entrypoints
        """
        if self.listener and self.listener.network:
            self.listener.network.extend_from_entry_points(group)
        else:
            raise RuntimeError("Can't extend an uninitialized network")

    def extend_listener(self, group):
        """"Extend the network with methods found in entrypoints
        """
        if self.listener:
            self.listener.extend_from_entry_points(group)
        else:
            raise RuntimeError("Can't extend an uninitialized listener")

    def signal_term_handler(self, signal, frame):
        """
        """
        logger.info("[ %s ] - Received signal %s", self.__class__.__name__, signal)
        self.stop_listener()
