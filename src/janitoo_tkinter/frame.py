#!/usr/bin/python
# -*- coding: utf-8 -*-

"""The ozwave management tools.

What we should do :

* show the nodes and update informations :
* show value class and update them : there is many level : User, Config, ...
* group associations : add a node to a group of a node
* controller we launch a command on the controller and listen to a topic to get message.
* reset operation : remove all nodes and reload the driver.
* we may also manage the scenes.

REQ vs SUB or REP feat PUB :

Openzwave use notifications to prevent us from update on the zwave network.
It's really easy to transform notifications in topics.
But what should we publish and how :

* Network : the state and the node count.
* Nodes : informations (name, location, ...), command_classes, values, ...

The simple way to make this data available is to publish them. Under
an admin section for example. Most of the time we don't want this data
to be available unless we are using the admin interface.
We should implement a mechanism to make available and diasble it.
One more time; the PUB/SUB seems to be the simplest way to do it.
When starting the Admin interface, we publish a topic :
usr.ozwave.admin.active = 1
So that the WQdget will activate its admin interface. It will disable it
when receiving usr.ozwave.admin.active = 0.


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
import Tkinter as tk
import tkFont as tkFont
import traceback

import ttk
from ttk import Frame, Style, Progressbar, Separator, Notebook
from ttk import Checkbutton, Button, LabelFrame
from ttk import Label, Entry

from janitoo_tkinter.tree import TreeListBox

class FrameNetwork(ttk.Frame):
    '''
    '''
    def __init__(self, parent, columns=['topic','value'], displaycolumns = ['value'], *args, **kw):
        name = kw.pop('name', 'Network')
        ttk.Frame.__init__(self, parent, name=name, *args, **kw)

        helv24 = tkFont.Font(family='Helvetica', size=24, weight='bold')
        helv14 = tkFont.Font(family='Helvetica', size=14, weight='bold', slant='italic')

        network_state_label = Label(self, justify="left", anchor="w", \
            text="Network : ", font=helv14)
        network_state_label.grid(row=0, column=0, sticky='new', pady=2, padx=2, \
            in_=self)

        self.network_state_var = tk.StringVar()
        network_state = Label(self, justify="left", anchor="w", \
            textvariable=self.network_state_var, font=helv14)
        network_state.grid(row=0, column=1, sticky='new', pady=2, padx=2, \
            in_=self)

        network_nodes_label = Label(self, justify="left", anchor="w", \
            text="Nodes : ", font=helv14)
        network_nodes_label.grid(row=1, column=0, sticky='new', pady=2, padx=2, \
            in_=self)

        self.network_nodes_var = tk.IntVar()
        network_nodes = Label(self, justify="left", anchor="w", \
            textvariable=self.network_nodes_var, font=helv14)
        network_nodes.grid(row=1, column=1, sticky='new', pady=2, padx=2, \
            in_=self)


class FrameNodes(ttk.Frame):
    '''
    '''
    def __init__(self, notebook, columns=['topic','value'], displaycolumns = ['value'], *args, **kw):
        name = kw.get('name', 'Nodes')
        ttk.Frame.__init__(self, notebook, name=Name, *args, **kw)
        self.tree_view = TreeListBox(self, columns=['topic', 'value'], displaycolumns=['value'])
        self.tree_view.grid(row=0, column=0, columnspan=3, sticky='nsew', pady=5, padx=5, in_=self)
        self.frame_trace.rowconfigure(0, weight=1)
        self.frame_trace.rowconfigure(1, weight=0)
        self.frame_trace.rowconfigure(2, weight=0)
        self.frame_trace.columnconfigure((0), weight=1, uniform=1)
        self.notebook.add(self.frame_trace, text='Trace', underline=0, padding=2)

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

class FrameRoot(Frame):

    def __init__(self, parent):
        Frame.__init__(self)

        self.notebook = Notebook(self, name='notebook')

        self.frame_network = FrameNetwork(self, name='main')
        self.frame_network.grid(row=1, column=0, columnspan=3, sticky='nsew', pady=5, padx=5, in_=self)

        #~ self.notebook.add(self.frame_main, text='Main', underline=0, padding=2)

        self.notebook.grid(row=2, column=0, columnspan=3, sticky='nsew', pady=5, padx=5, in_=self)

        self.rowconfigure((0,1), weight=0)
        self.rowconfigure(2, weight=1)
        self.columnconfigure((0,1,2), weight=1, uniform=1)
        self.pack(expand=1, fill="both")

        #~ self.notebook.enable_traversal()
        #~ self.status = tkMon(self, self.subscriber)
        #~ self.notebook.enable_traversal()
        #~ self.error.grid(row=0, column=0, columnspan=3, sticky='new', pady=5, padx=5, in_=self)
        #~ self.warning.grid(row=1, column=0, columnspan=3, sticky='new', pady=5, padx=5, in_=self)
        #~ self.notebook.grid(row=2, column=0, columnspan=3, sticky='nsew', pady=5, padx=5, in_=self)
        #~ self.status.grid(row=0, column=3, rowspan=3, sticky='ne', pady=5, padx=5, in_=self)
        #~ self.rowconfigure((0,1), weight=0)
        #~ self.rowconfigure(2, weight=1)
        #~ self.columnconfigure((0,1,2), weight=1, uniform=1)
        #~ self.pack(expand=1, fill="both")

    def _create_widgets(self):
#        if self.isapp:
#            SeeDismissPanel(self)
        self._create_demo_panel()

