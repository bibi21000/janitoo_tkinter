#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
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

import Tkinter as tk
import tkFont as tkFont
import ttk as ttk

class DialogClose(tk.Toplevel):

    def __init__(self, parent, title = None):
        tk.Toplevel.__init__(self, parent)
        self.transient(parent)
        if title:
            self.title(title)
        self.parent = parent
        body = tk.Frame(self)
        self.initial_focus = self.body(body)
        body.pack(padx=5, pady=5)
        self.buttonbox()
        self.grab_set()
        if not self.initial_focus:
            self.initial_focus = self
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.geometry("+%d+%d" % (parent.winfo_rootx()+50,
                                  parent.winfo_rooty()+50))
        #~ self.geometry("+%d+%d" % (parent.winfo_screenwidth()+50,
                                  #~ parent.winfo_screenheight()-50))
        self.initial_focus.focus_set()
        self.wait_window(self)
    #
    # construction hooks

    def body(self, master):
        # create dialog body.  return widget that should have
        # initial focus.  this method should be overridden
        pass

    def buttonbox(self):
        # add standard button box. override if you don't want the
        # standard buttons
        box = tk.Frame(self)
        sb = tk.Button(box, text="Send", width=10, command=self.send, default="active")
        sb.pack(side="left", padx=5, pady=5)
        sr = tk.Button(box, text="Refresh", width=10, command=self.refresh, default="active")
        sr.pack(side="left", padx=5, pady=5)
        sc = tk.Button(box, text="Close", width=10, command=self.close, default="active")
        sc.pack(side="left", padx=5, pady=5)
        box.pack()

    def send(self, event=None):
        """
        """
        pass

    def refresh(self, event=None):
        """
        """
        pass

    def close(self, event=None):
        # put focus back to the parent window
        self.parent.focus_set()
        self.destroy()
