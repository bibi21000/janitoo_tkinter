# -*- coding: utf-8 -*-
"""
    The options

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
__copyright__ = "Copyright © 2013-2014-2015 Sébastien GALLET aka bibi21000"

from gevent import monkey
monkey.patch_all()

import logging
logger = logging.getLogger("janitoo.flask")

import os
import ConfigParser
import socket

from janitoo.options import JNTOptions

class Config(object):
    """Load options from a common config file
    """

    # Get the app root path
    #            <_basedir>
    # ../../ -->  flaskbb/flaskbb/configs/base.py
    _basedir = os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(
                            os.path.dirname(__file__)))))

    DEBUG = False
    TESTING = False

    # Logs
    # If SEND_LOGS is set to True, the admins (see the mail configuration) will
    # recieve the error logs per email.
    #~ SEND_LOGS = False

    # The filename for the info and error logs. The logfiles are stored at
    # flaskbb/logs
    #~ INFO_LOG = "info.log"
    #~ ERROR_LOG = "error.log"

    # Default Database
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + _basedir + '/' + \
                              'janitoo_flask.sqlite'

    # This will print all SQL statements
    SQLALCHEMY_ECHO = False

    # Security
    # This is the secret key that is used for session signing.
    # You can generate a secure key with os.urandom(24)
    SECRET_KEY = 'secret key'

    # Protection against form post fraud
    WTF_CSRF_ENABLED = True
    WTF_CSRF_SECRET_KEY = "reallyhardtoguess"

    # Caching
    CACHE_TYPE = "filesystem"
    CACHE_DEFAULT_TIMEOUT = 5
    CACHE_DEFAULT_SQL_TIMEOUT = 20
    CACHE_DIR = os.path.join(_basedir, "flask_cache_store")
    CACHE_THRESHOLD = 500

    # Auth
    LOGIN_VIEW = "auth.login"
    REAUTH_VIEW = "auth.reauth"
    LOGIN_MESSAGE_CATEGORY = "error"

    ## Captcha
    RECAPTCHA_ENABLED = False
    RECAPTCHA_USE_SSL = False
    RECAPTCHA_PUBLIC_KEY = "your_public_recaptcha_key"
    RECAPTCHA_PRIVATE_KEY = "your_private_recaptcha_key"
    RECAPTCHA_OPTIONS = {"theme": "white"}

    ## Mail
    MAIL_SERVER = "localhost"
    MAIL_PORT = 25
    MAIL_USE_SSL = False
    MAIL_USE_TLS = False
    MAIL_USERNAME = "noreply@example.org"
    MAIL_PASSWORD = ""
    MAIL_DEFAULT_SENDER = ("Default Sender", "noreply@example.org")
    # Where to logger should send the emails to
    ADMINS = ["admin@example.org"]

    # URL Prefixes
    USER_URL_PREFIX = "/user"
    AUTH_URL_PREFIX = "/auth"
    ADMIN_URL_PREFIX = "/admin"

class OptionsConfig(Config):
    """Load options from a common config file
    """
    def __init__(self, conf_file):
        """Update Flask default data from janitoo option file
        """
        Config.__init__(self)
        if not os.path.isfile(conf_file):
            raise RuntimeError("Can't find %s" %conf_file )
        self.options = JNTOptions({"conf_file":conf_file})
        self.options.load()
        if 'hostname' not in self.options.data or self.options.data['hostname'] is None:
            self.options.data['hostname'] = socket.gethostname()
        system = self.options.data
        webapp = self.options.get_options('webapp')
        database = self.options.get_options('database')
        try:
            flask = self.options.get_options('flask')
        except ConfigParser.NoSectionError:
            flask = {}
        self.SQLALCHEMY_DATABASE_URI = database['sqlalchemy.url']
        if 'host' in webapp and 'port' in webapp:
            self.SERVER_NAME = "%s:%s"%(webapp['host'], webapp['port'])
        if 'cache_dir' in system:
            self.CACHE_DIR = so.path.join(system['cache_dir'], 'flask_cache_store')

        print self.options.data
