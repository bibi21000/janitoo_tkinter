#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
"""

__license__ = """
    This file is part of HABus.

    HABus is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    HABus is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with HABus.  If not, see <http://www.gnu.org/licenses/>.
"""
__copyright__ = "2013 : (c) Sébastien GALLET aka bibi21000"
__author__ = 'Sébastien GALLET aka bibi21000'
__email__ = 'bibi21000@gmail.com'

#import tkinter as tk
#import tkinter.Font as tkFont
#import tkinter.ttk as ttk
#import Tkinter
#~ import Tkinter as tk
import tkFont as tkFont
import ttk as ttk
import traceback

class TreeListBox(ttk.Frame):
    '''
    '''
    def __init__(self, master, columns=['topic','value'], displaycolumns = ['value'], *args, **kw):
        ttk.Frame.__init__(self, master, *args, **kw)
        self.tree = None
        self.displaycolumns = displaycolumns
        self.columns = columns
        self._setup_widgets(columns, displaycolumns)
        #self._build_tree()

    def _setup_widgets(self, columns, displaycolumns):
        self.tree = ttk.Treeview(self, columns=columns, displaycolumns=displaycolumns)
        vsb = ttk.Scrollbar(orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=lambda f, l: self.autoscroll(vsb, f, l),
            xscrollcommand=lambda f, l:self.autoscroll(hsb, f, l))
        self.tree.grid(column=0, row=0, sticky='nsew', in_=self)
        vsb.grid(column=1, row=0, sticky='ns', in_=self)
        hsb.grid(column=0, row=1, sticky='ew', in_=self)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        #self.pack(fill='both', expand=1)
        for col in columns:
            self.tree.heading(col, text=col.title(),
                command=lambda c=col: self.sortby(self.tree, c, 0))
        for col in displaycolumns:
            self.tree.column(col, stretch=0, width=350)

    def mqtt_callback(self, client, userdata, message):
        """Called when a message has been received on a topic that the client subscribes to.

        :param client: the Client instance that is calling the callback.
        :type client: paho.mqtt.client.Client
        :param userdata: user data of any type and can be set when creating a new client instance or with user_data_set(userdata).
        :type userdata: all
        :param message: The message variable is a MQTTMessage that describes all of the message parameters.
        :type message: paho.mqtt.client.MQTTMessage

        """
        pass

    def clear(self):
        """
        """
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.item_count = 0

#    def _on_topic_update(self, topic, value) :
    def add_item(self, key, items) :
        self.item_count += 1
        indexes = key.split(".")
        #print indexes
        length = len(indexes) - 1
        current_item = ''
        #print "current_item %s" % current_item
        i = 0
        for index in indexes :
            #print "index = %s" % index
            found = False
            for item in self.tree.get_children(current_item):
                text = self.tree.item(item, 'text')
                if text == index :
                    current_item = item
                    found = True
                    #print "current_item = %s" % current_item
            if i != length :
                ptype='node'
            else :
                ptype='value'
            if found == False :
                #print "add %s" % index
                if ptype == 'node':
                    current_item = self.tree.insert(current_item, 0, text=index, values=[index])
                    #print "add new node %s" % [index]
                elif ptype == 'value':
                    iid = self.tree.insert(current_item, 0, text=index, values=[index] + items)
                    #self.tree.insert(iid, 0, text=index, values=[index] + items)
                    #print "add new value %s" % ([index] + items)
            else :
                if ptype == 'value':
                    self.tree.insert(current_item, 0, text=index, values=[index] + items)
                    #print "add another value %s" % ([index] + items)
            i += 1

    def check_item_size(self, key, items) :
        """
        """
        for col in headers:
            # adjust the column's width to the header string
            self.tree.column(col,
                width=tkFont.Font().measure(col.title()))

    def set_item(self, key, col, items) :
        """
        """
        current_item = ''
        found = False
        for item in self.tree.get_children(''):
            print "current_item = %s" % item
            value = self.tree.item(item, 'values')
            print value
            print key
            if value[0] == key :
                current_item = item
                found = True
                #break
        print "Found %s" % found
        if found == False :
            self.add_item(key, items)
        else :
            self.tree.set(current_item, col, items[0])

    def _build_tree(self):
        car_header = ['key', 'value']
        car_list = [
            ('Hyundai', 'brakes') ,
            ('Honda', 'light') ,
            ('Lexus', 'battery') ,
            ('Benz', 'wiper') ,
            ('Ford', 'tire') ,
            ('Chevy', 'air') ,
            ('Chrysler', 'piston') ,
            ('Toyota', 'brake pedal') ,
            ('BMW', 'seat')
            ]
        print "init tree"
        for item in car_list:
            self.tree.insert('', 'end', values=item)
            # adjust column's width if necessary to fit each value
            for ix, val in enumerate(item):
                col_w = tkFont.Font().measure(val)
                if self.tree.column(car_header[ix],width=None)<col_w:
                    self.tree.column(car_header[ix], width=col_w)

    def sortby(self, tree, col, descending):
        """sort tree contents when a column header is clicked on"""
        # grab values to sort
        data = [(tree.set(child, col), child) \
            for child in tree.get_children('')]
        # if the data to be sorted is numeric change to float
        #data =  change_numeric(data)
        # now sort the data in place
        data.sort(reverse=descending)
        for ix, item in enumerate(data):
            tree.move(item[1], '', ix)
        # switch the heading so it will sort in the opposite direction
        tree.heading(col, command=lambda col=col: self.sortby(tree, col, \
            int(not descending)))

    def autoscroll(self, sbar, first, last):
        """Hide and show scrollbar as needed."""
        first, last = float(first), float(last)
        if first <= 0 and last >= 1:
            sbar.grid_remove()
        else:
            sbar.grid()
        sbar.set(first, last)
