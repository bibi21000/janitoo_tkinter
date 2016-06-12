# -*- coding: utf-8 -*-
"""The Network
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

# Set default logging handler to avoid "No handler found" warnings.
import logging
logger = logging.getLogger(__name__)

from pkg_resources import iter_entry_points

from janitoo.utils import HADD, HADD_SEP, json_loads, hadd_split
from janitoo.dhcp import HeartbeatMessage, CacheManager, JNTNetwork

import Tkinter as tk

class Network(JNTNetwork):
    """The network manager for the TKinter application
    """

    def __init__(self, stop_event, options, **kwargs):
        """
        """
        JNTNetwork.__init__(self, stop_event, options, **kwargs)
        self.extend_from_entry_points('janitoo_tkinter')
        self.var_state = tk.StringVar()
        self.var_state_str = tk.StringVar()
        self.var_nodes_count = tk.IntVar()
        self.var_home_id = tk.StringVar()
        self.var_is_failed = tk.BooleanVar()
        self.var_is_secondary = tk.BooleanVar()
        self.var_is_primary = tk.BooleanVar()

    def emit_network(self):
        """Emit a network state event
        """
        logger.debug('Network event : homeid %s (state:%s) - %d nodes were found.' % (self.home_id, self.state, self.nodes_count))
        #~ print "event received"
        self.var_state = self.state
        self.var_state_str = self.state_str
        self.var_nodes_count = self.nodes_count
        self.var_home_id = self.home_id
        self.var_is_failed = self.is_failed
        self.var_is_secondary = self.is_secondary
        self.var_is_primary = self.is_primary

        logger.debug('Network event : homeid %s (state:%s) - %d nodes were found.' % (self.home_id, self.state, self.nodes_count))
        #~ print "response sent %s" % ret

    def emit_nodes(self):
        """Emit a nodes state event
        """
        res = {}
        res.update(self.nodes)
        for key in res:
            add_ctrl, add_node = hadd_split(key)
            if add_ctrl in self.heartbeat_cache.entries and add_node in self.heartbeat_cache.entries[add_ctrl]:
                res[key]['state'] = self.heartbeat_cache.entries[add_ctrl][add_node]['state']
            else:
                res[key]['state'] = 'UNKNOWN'
        #~ self.socketio.emit('my nodes response',
            #~ {'data':res},
            #~ namespace='/janitoo')
        logger.debug(u'Nodes event :%s', self.nodes)

    def emit_node(self, nodes):
        """Emit a node state event
        nodes : a single node or a dict of nodes
        """
        #~ pass
        #~ # print " emit_node %s" %nodes
        #~ # if 'hadd' not in nodes:
            #~ # print " emit_node hadd not in nodes"
            #~ # for key in nodes:
                #~ # nodes[key]['state'] = 'online'
        #~ self.socketio.emit('my node response',
            #~ {'data':nodes},
            #~ namespace='/janitoo')
        logger.debug(u'Node event :%s', nodes)

    def extend_from_entry_points(self, group):
        """"Extend the network with methods found in entrypoints
        """
        for entrypoint in iter_entry_points(group = '%s.network'%group):
            logger.info('Extend network with %s', entrypoint.module_name )
            extend = entrypoint.load()
            extend( self )
