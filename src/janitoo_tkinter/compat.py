# -*- coding: utf-8 -*-
"""
    janitoo.compat
    ~~~~~~~~~~~~~~

"""

_license__ = """
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


from six import PY2, PY3, text_type, string_types

if PY2:
    import tkFont as tkFont
    import ttk as ttk
    import Tkinter as tk

else:

    import tkinter.font as tkFont
    import tkinter.ttk as ttk
    import tkinter as tk
