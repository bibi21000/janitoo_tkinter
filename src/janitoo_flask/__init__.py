# -*- coding: utf-8 -*-

"""janitoo flask extension.

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

    Original copyright :
    Copyright (c) 2013 Roger Light <roger@atchoo.org>

    All rights reserved. This program and the accompanying materials
    are made available under the terms of the Eclipse Distribution License v1.0
    which accompanies this distribution.

    The Eclipse Distribution License is available at
    http://www.eclipse.org/org/documents/edl-v10.php.

    Contributors:
     - Roger Light - initial implementation

    This example shows how you can use the MQTT client in a class.

"""
__author__ = 'Sébastien GALLET aka bibi21000'
__email__ = 'bibi21000@gmail.com'
__copyright__ = "Copyright © 2013-2014 Sébastien GALLET aka bibi21000"

from gevent import monkey
monkey.patch_all()

import logging
logger = logging.getLogger(__name__)

from flask_bower import Bower
from flask_cache import Cache

from logging.config import fileConfig as logging_fileConfig
from flask import appcontext_pushed
from flask import current_app
from jinja2 import Markup
import signal, sys
import os, tempfile, errno
import threading

from pkg_resources import iter_entry_points

from janitoo_flask.listener import ListenerThread

#~ print "================================================================================================= I'ts import !!!"

"""
A Flask extension to build a webapp for janitoo
"""

# Find the stack on which we want to store the database connection.
# Starting with Flask 0.9, the _app_ctx_stack is the correct one,
# before that we need to use the _request_ctx_stack.
try:
    from flask import _app_ctx_stack as stack
except ImportError:
    from flask import _request_ctx_stack as stack

class FlaskJanitoo(object):

    def __init__(self, app=None, options=None, db=None):
        self._app = app
        self._db = db
        self.options = options
        if self.options is not None and 'conf_file' in self.options and self.options['conf_file'] is not None:
            logging_fileConfig(self.options['conf_file'])
        self._listener = None
        self._listener_lock = None
        self._sleep = 1
        self.menu_left = []
        # Bower
        self.bower = Bower()
        # Caching
        self.cache = Cache()

    def init_app(self, app, options, db=None):
        """
        """
        if app is not None:
            self._app = app
        if options is not None:
            self.options = options
        if db is not None:
            self._db = db
        if self.options is not None and 'conf_file' in self.options and self.options['conf_file'] is not None:
            logging_fileConfig(self.options['conf_file'])

        # Flask-Cache
        self.cache.init_app(self._app)
        # Flask-Bower
        self.bower.init_app(self._app)

        self._event_manager = EventManager(self._app)
        self._app.jinja_env.globals["emit_event"] = self._event_manager.template_emit
        if not hasattr(self._app, 'extensions'):
            self._app.extensions = {}
        self._app.extensions['options'] = self.options
        self._app.extensions['bower'] = self.bower
        self._app.extensions['cache'] = self.cache
        self._app.extensions['janitoo'] = self
        try:
            self._sleep = int(self._app.config['FLASKJANITOO_SLEEP'])
            if self._sleep <= 0 :
                self._sleep = 1
        except KeyError:
            self._sleep = 1
        except ValueError:
            self._sleep = 1
        # Use the newstyle teardown_appcontext if it's available,
        # otherwise fall back to the request context
        if hasattr(self._app, 'teardown_appcontext'):
            self._app.teardown_appcontext(self.teardown)
        else:
            self._app.teardown_request(self.teardown)
        signal.signal(signal.SIGTERM, self.signal_term_handler)
        signal.signal(signal.SIGINT, self.signal_term_handler)
        self._listener_lock = threading.Lock()

        self.create_listener()

    def create_listener(self):
        """Create the listener on first call
        """
        self._listener = ListenerThread(self._app, self.options)

    @property
    def listener(self):
        """Start the listener on first call
        """
        #~ print "============================================================> get listener"
        self.start_listener()
        return self._listener

    def start_listener(self):
        """Start the listener on first call
        """
        try:
            self._listener_lock.acquire()
            if not self._listener.is_alive():
                self._listener.start()
        finally:
            self._listener_lock.release()

    def extend_blueprints(self, group):
        """
        """
        for entrypoint in iter_entry_points(group = '%s.blueprint'%'janitoo_manager'):
            logger.info('Add blueprint from %s', entrypoint.module_name )
            bprint, url = entrypoint.load()()
            self._app.register_blueprint(bprint, url_prefix=url)
        for entrypoint in iter_entry_points(group = '%s.menu_left'%group):
            logger.info('Extend menu_left with %s', entrypoint.module_name )
            self.menu_left.append(entrypoint.load()())
        self._app.template_context_processors[None].append(lambda : dict(jnt_menu_left=self.menu_left))

    def extend_network(self, group):
        """"Extend the network with methods found in entrypoints
        """
        if self._listener and self._listener.network:
            self._listener.network.extend_from_entry_points(group)
        else:
            raise RuntimeError("Can't extend an uninitialized network")

    def extend_listener(self, group):
        """"Extend the network with methods found in entrypoints
        """
        if self._listener:
            self._listener.extend_from_entry_points(group)
        else:
            raise RuntimeError("Can't extend an uninitialized listener")

    def signal_term_handler(self, signal, frame):
        """
        """
        logger.info("[ %s ] - Received signal %s", self.__class__.__name__, signal)
        if self._listener.is_alive():
            self._listener.stop()
            try:
                print self._listener
                self._listener.join()
            except AssertionError:
                logger.exception("Catched exception : ")
            except RuntimeError:
                logger.exception("Catched exception : ")
        sys.exit(0)

    def connect(self):
        return sqlite3.connect(current_app.config['SQLITE3_DATABASE'])

    #~ @property
    #~ def backend(self):
        #~ ctx = stack.top
        #~ if ctx is not None:
            #~ if not hasattr(ctx, 'tinyflow_backend'):
                #~ ctx.tinyflow_backend = self._backend
            #~ return ctx.tinyflow_backend
#~
    #~ @property
    #~ def thread(self):
        #~ ctx = stack.top
        #~ if ctx is not None:
            #~ if not hasattr(ctx, 'tinyflow_server'):
                #~ ctx.tinyflow_server = self._server
            #~ return ctx.tinyflow_server
#~
    def teardown(self, exception):
        ctx = stack.top
        #~ if hasattr(ctx, 'tinyflow_backend'):
            #~ ctx.tinyflow_backend.teardown(exception)
            #~ ctx.tinyflow_backend = None
        #~ if hasattr(ctx, 'tinyflow_server'):
            #~ if ctx.tinyflow_server.is_alive():
                #~ ctx.tinyflow_server.stop()
                #~ ctx.tinyflow_server.join()
            #~ ctx.tinyflow_server = None
        #~ self._flows = None

#https://github.com/sh4nks/flask-plugins/blob/master/flask_plugins/__init__.py

def connect_event(event, callback, position='after'):
    """Connect a callback to an event.  Per default the callback is
    appended to the end of the handlers but handlers can ask for a higher
    privilege by setting `position` to ``'before'``.
    Example usage::
        def on_before_metadata_assembled(metadata):
            metadata.append('<!-- IM IN UR METADATA -->')
        # And in your setup() method do this:
            connect_event('before-metadata-assembled',
                           on_before_metadata_assembled)
    """
    current_app.plugin_manager._event_manager.connect(event, callback, position)


def emit_event(event, *args, **kwargs):
    """Emit a event and return a list of event results.  Each called
    function contributes one item to the returned list.
    This is equivalent to the following call to :func:`iter_listeners`::
        result = []
        for listener in iter_listeners(event):
            result.append(listener(*args, **kwargs))
    """
    return [x(*args, **kwargs) for x in
            current_app.plugin_manager._event_manager.iter(event)]


def iter_listeners(event):
    """Return an iterator for all the listeners for the event provided."""
    return current_app.plugin_manager._event_manager.iter(event)


class EventManager(object):
    """Helper class that handles event listeners and event emitting.
    This is *not* a public interface. Always use the `emit_event` or
    `connect_event` or the `iter_listeners` functions to access it.
    """

    def __init__(self, app):
        self.app = app
        self._listeners = {}
        self._last_listener = 0

    def connect(self, event, callback, position='after'):
        """Connect a callback to an event."""
        assert position in ('before', 'after'), 'invalid position'
        listener_id = self._last_listener
        event = intern_method(event)
        if event not in self._listeners:
            self._listeners[event] = deque([callback])
        elif position == 'after':
            self._listeners[event].append(callback)
        elif position == 'before':
            self._listeners[event].appendleft(callback)
        self._last_listener += 1
        return listener_id

    def remove(self, event, callback):
        """Remove a callback again."""
        try:
            self._listeners[event].remove(callback)
        except (KeyError, ValueError):
            pass

    def iter(self, event):
        """Return an iterator for all listeners of a given name."""
        if event not in self._listeners:
            return iter(())
        return iter(self._listeners[event])

    def template_emit(self, event, *args, **kwargs):
        """Emits events for the template context."""
        results = []
        for f in self.iter(event):
            rv = f(*args, **kwargs)
            if rv is not None:
                results.append(rv)
        return Markup(TemplateEventResult(results))

class TemplateEventResult(list):
    """A list subclass for results returned by the event listener that
    concatenates the results if converted to string, otherwise it works
    exactly like any other list.
    """

    def __init__(self, items):
        list.__init__(self, items)

    def __unicode__(self):
        return u''.join(map(str, self))

    def __str__(self):
        if sys.version_info[0] >= 3:
            return self.__unicode__()
        else:
            return self.__unicode__().encode('utf-8')
