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

from pkg_resources import iter_entry_points

from janitoo.server import JNTControllerManager
from janitoo.utils import HADD, HADD_SEP


class Controller(JNTControllerManager):
    """ The controller
    """

    def __init__(self, network):
        """The constructor"""
        JNTControllerManager.__init__(self)
        self.network = network

    def add_more_values(self, **kwargs):
        """Start the controller
        """
        value_factory = {}
        for entrypoint in iter_entry_points(group = 'janitoo.values'):
            value_factory[entrypoint.name] = entrypoint.load()

        uuid="count_user_values"
        value = value_factory['sensor_string'](options=self._controller.options, uuid=uuid,
            node_uuid=self._controller.uuid,
            genre=0x01,
            help='The number of user values in the network',
            label='#user values',
            units='#',
            get_data_cb=self.get_count_user_values,
        )
        self._controller.add_value(uuid, value)
        poll_value = value.create_poll_value(default=15)
        self._controller.add_value(poll_value.uuid, poll_value)
        self.add_poll(value, timeout=10)

        uuid="count_config_values"
        value = value_factory['sensor_string'](options=self._controller.options, uuid=uuid,
            node_uuid=self._controller.uuid,
            genre=0x01,
            help='The number of config values in the network',
            label='#config values',
            units='#',
            get_data_cb=self.get_count_config_values,
        )
        self._controller.add_value(uuid, value)
        poll_value = value.create_poll_value(default=15)
        self._controller.add_value(poll_value.uuid, poll_value)
        self.add_poll(value, timeout=10)

        uuid="count_basic_values"
        value = value_factory['sensor_string'](options=self._controller.options, uuid=uuid,
            node_uuid=self._controller.uuid,
            genre=0x01,
            help='The number of basic values in the network',
            label='#basic values',
            units='#',
            get_data_cb=self.get_count_basic_values,
        )
        self._controller.add_value(uuid, value)
        poll_value = value.create_poll_value(default=15)
        self._controller.add_value(poll_value.uuid, poll_value)
        self.add_poll(value, timeout=10)

    def get_count_user_values(self, node_uuid, index):
        """Return the number of user values
        """
        return "%s:%s:%s"%self.network.users_count

    def get_count_config_values(self, node_uuid, index):
        """Return the number of onfig values
        """
        return "%s:%s:%s"%self.network.configs_count

    def get_count_basic_values(self, node_uuid, index):
        """Return the number of basic values
        """
        return "%s:%s:%s"%self.network.basics_count


