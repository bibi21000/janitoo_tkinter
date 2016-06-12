# -*- coding: utf-8 -*-

"""The listener.

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

import logging
logger = logging.getLogger(__name__)

import sys
import threading
from pkg_resources import iter_entry_points

from janitoo.options import JNTOptions
from janitoo.utils import HADD, HADD_SEP, CADD, json_dumps, json_loads
from janitoo.dhcp import HeartbeatMessage, check_heartbeats, CacheManager
from janitoo_tkinter.network import Network
from janitoo_tkinter.controller import Controller

##############################################################
#Check that we are in sync with the official command classes
#Must be implemented for non-regression
from janitoo.classes import COMMAND_DESC

COMMAND_DHCPD = 0x1000
COMMAND_CONTROLLER = 0x1050
COMMAND_DISCOVERY = 0x5000

assert(COMMAND_DESC[COMMAND_DISCOVERY] == 'COMMAND_DISCOVERY')
assert(COMMAND_DESC[COMMAND_CONTROLLER] == 'COMMAND_CONTROLLER')
assert(COMMAND_DESC[COMMAND_DHCPD] == 'COMMAND_DHCPD')
##############################################################

listener = None

class ListenerThread(threading.Thread, Controller):
    """ The listener Tread
    """

    def __init__(self, options):
        """The constructor"""
        #~ print "*"*25, "init the listener"
        threading.Thread.__init__(self)
        self._stopevent = threading.Event( )
        self.section="tkinter"
        self.mqttc = None
        self.options = JNTOptions(options)
        self.hadds = {}
        self.network = None
        self.create_network()
        Controller.__init__(self, self.network)
        self.loop_sleep = 0.25
        loop_sleep = self.options.get_option('system','loop_sleep', self.loop_sleep)
        if loop_sleep is not None:
            self.loop_sleep = loop_sleep
        else:
            logger.debug("[%s] - Can't retrieve value of loop_sleep. Use default value instead (%s)", self.__class__.__name__, self.loop_sleep)
        self.extend_from_entry_points('janitoo_flask')

    def __del__(self):
        """
        """
        try:
            self.stop()
        except Exception:
            logger.debug("[%s] - Catched exception", self.__class__.__name__)

    def create_network(self):
        """Create the listener on first call
        """
        self.network = Network(self._stopevent, self.options, is_primary=False, is_secondary=True, do_heartbeat_dispatch=False)

    def boot(self):
        """configure the HADD address
        """
        #~ print("*"*25, "boot the listener")
        default_hadd = HADD%(9998,0)
        hadd = self.options.get_option('webapp','hadd', default_hadd)
        if default_hadd is None:
            logger.debug("[%s] - Can't retrieve value of hadd. Use default value instead (%s)", self.__class__.__name__, default_hadd)
        self.hadds = { 0 : hadd,
                     }
        #~ print "*"*25, "booting"

    def run(self):
        """The running method
        """
        #~ print "*"*25, "start the listener"
        logger.info("Start listener")
        self.boot()
        self.network.boot(self.hadds)
        Controller.start_controller(self, self.section, self.options, cmd_classes=[COMMAND_DHCPD], hadd=self.hadds[0], name="Webapp Server",
            product_name="Webapp Server", product_type="Webapp Server")
        self._stopevent.wait(1.0)
        Controller.start_controller_timer(self)
        while not self._stopevent.isSet():
            self._stopevent.wait(self.loop_sleep)
        if self.network is not None:
            self.network.stop()

    def stop(self):
        """Stop the tread
        """
        #~ print("*"*25, "stop the listener")
        Controller.stop_controller_timer(self)
        Controller.stop_controller(self)
        logger.info("Stop listener")
        self._stopevent.set()
        if self.network is not None:
            #~ print("*"*25, "stop the network")
            self.network.stop()
        for i in range(100):
            if self.network is None or self.network.is_stopped:
                break
            else:
                self._stopevent.wait(0.1)
        self.network = None
        #~ print("*"*25, "network is stopped")

    def extend_from_entry_points(self, group):
        """"Extend the listener with methods found in entrypoints
        """
        for entrypoint in iter_entry_points(group = '%s.listener'%group):
            logger.info('Extend listener with %s', entrypoint.module_name )
            extend = entrypoint.load()
            extend( self )

