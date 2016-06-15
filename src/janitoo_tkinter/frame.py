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

import logging
logger = logging.getLogger(__name__)

import os
import io

import pkg_resources

#import tkinter as tk
#import tkinter.Font as tkFont
#import tkinter.ttk as ttk
#import Tkinter
import Tkinter as tk
import tkFont as tkFont
import traceback

import ttk
#~ from ttk import Frame, Style, Progressbar, Separator, Notebook
#~ from ttk import Checkbutton, Button, LabelFrame
#~ from ttk import Label, Entry

from PIL import Image, ImageTk

from janitoo.options import JNTOptions

from janitoo_tkinter.tree import TreeListBox

class JntFrame(ttk.Frame):
    '''
    '''
    def __init__(self, parent, columns=['topic','value'], displaycolumns = ['value'], *args, **kw):
        name = kw.pop('name', 'network')
        self.tkroot = kw.pop('tkroot', None)
        self.options = kw.pop('options', {})
        self.section = kw.pop('section', 'tkinter')
        ttk.Frame.__init__(self, parent, name=name, *args, **kw)

    def __del__(self):
        """
        """
        try:
            self.tkroot = None
            self.options = None
            self.section = None
        except Exception:
            pass

class FrameNetwork(JntFrame):
    '''
    '''
    def __init__(self, parent, columns=['topic','value'], displaycolumns = ['value'], *args, **kw):
        name = kw.pop('name', 'network')
        JntFrame.__init__(self, parent, name=name, *args, **kw)

        helv24 = tkFont.Font(family='Helvetica', size=24, weight='bold')
        helv12 = tkFont.Font(family='Helvetica', size=12, weight='bold', slant='italic')

        #~ label_frame_network = ttk.Labelframe(self, text='Network')
        #~ label_frame_network.grid(row=0, column=0, sticky='nw', pady=2, padx=2, \
            #~ in_=self)

        network_state_label = ttk.Label(self, justify="left", anchor="w", \
            text="Network : ", font=helv12)
        network_state_label.grid(row=0, column=0, sticky='nw', pady=2, padx=2, \
            in_=self)

        network_state = ttk.Label(self, justify="left", anchor="w", \
            textvariable=self.tkroot.var_state_str, font=helv12, width = 40)
        network_state.grid(row=0, column=1, sticky='nw', pady=2, padx=2, \
            in_=self)

        network_nodes_label = ttk.Label(self, justify="left", anchor="w", \
            text="Nodes : ", font=helv12)
        network_nodes_label.grid(row=1, column=0, sticky='nw', pady=2, padx=2, \
            in_=self)

        network_nodes = ttk.Label(self, justify="left", anchor="w", \
            textvariable=self.tkroot.var_nodes_count, font=helv12)
        network_nodes.grid(row=1, column=1, sticky='nw', pady=2, padx=2, \
            in_=self)

        sep = ttk.Separator(parent, orient='vertical')
        sep.grid(row=0, rowspan=3, column=3, sticky='ns', pady=2, padx=2, \
            in_=self)
#~
        #~ label_frame_mode = ttk.Labelframe(self, text='Mode')
        #~ label_frame_mode.grid(row=0, column=1, sticky='ne', pady=2, padx=2, \
            #~ in_=self)

        network_primary = ttk.Checkbutton(self, text = "Primary", \
                onvalue = 1, offvalue = 0, variable = self.tkroot.var_is_primary)
        network_primary.state(["disabled"])
        network_primary.grid(row=0, column=4, sticky='nw', pady=2, padx=2, \
            in_=self)

        network_secondary = ttk.Checkbutton(self, text = "Secondary", \
                onvalue = 1, offvalue = 0, variable = self.tkroot.var_is_secondary)
        network_secondary.state(["disabled"])
        network_secondary.grid(row=1, column=4, sticky='nw', pady=2, padx=2, \
            in_=self)

        network_failed = ttk.Checkbutton(self, text = "Fail mode", \
                onvalue = 1, offvalue = 0, variable = self.tkroot.var_is_failed)
        network_failed.state(["disabled"])
        network_failed.grid(row=2, column=4, sticky='nw', pady=2, padx=2, \
            in_=self)

class FrameNodes(JntFrame):
    '''
    '''
    def __init__(self, notebook, columns=['topic','value'], displaycolumns = ['value'], *args, **kw):
        name = kw.pop('name', 'nodes')
        JntFrame.__init__(self, notebook, name=name, *args, **kw)
        self.tree_view = TreeListBox(self, columns=['topic', 'value'], displaycolumns=['value'])
        self.tree_view.grid(row=0, column=0, columnspan=3, sticky='nsew', pady=5, padx=5, in_=self)
        #~ self.frame_trace.rowconfigure(0, weight=1)
        #~ self.frame_trace.rowconfigure(1, weight=0)
        #~ self.frame_trace.rowconfigure(2, weight=0)
        #~ self.frame_trace.columnconfigure((0), weight=1, uniform=1)
        #~ self.notebook.add(self.frame_trace, text='Trace', underline=0, padding=2)

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


class FrameMap(JntFrame):
    '''
    '''
    def __init__(self, notebook, *args, **kw):
        name = kw.pop('name', 'map')
        JntFrame.__init__(self, notebook, name=name, *args, **kw)

        toolbar_frame = ttk.Frame(self, relief='ridge')
        self.zoom = 1

        stream = pkg_resources.resource_stream(
            __name__,
            'images/16/arrow_refresh.png',
        )
        image = Image.open(io.BytesIO(stream.read()))
        self.network_refresh_image = ImageTk.PhotoImage(image)
        network_refresh = ttk.Button(toolbar_frame, image=self.network_refresh_image, \
            compound='image', command=self.action_refresh)

        stream = pkg_resources.resource_stream(
            __name__,
            'images/16/magnifier_zoom_out.png',
        )
        image = Image.open(io.BytesIO(stream.read()))
        self.network_zoom_out_image = ImageTk.PhotoImage(image)
        network_zoom_out = ttk.Button(toolbar_frame, image=self.network_zoom_out_image, \
            compound='image', command=self.action_zoom_out)

        stream = pkg_resources.resource_stream(
            __name__,
            'images/16/magnifier_zoom_in.png',
        )
        image = Image.open(io.BytesIO(stream.read()))
        self.network_zoom_in_image = ImageTk.PhotoImage(image)
        network_zoom_in = ttk.Button(toolbar_frame, image=self.network_zoom_in_image, \
            compound='image', command=self.action_zoom_in)

        stream = pkg_resources.resource_stream(
            __name__,
            'images/16/magnifier.png',
        )
        image = Image.open(io.BytesIO(stream.read()))
        self.network_zoom_none_image = ImageTk.PhotoImage(image)
        network_zoom_none = ttk.Button(toolbar_frame, image=self.network_zoom_none_image, \
            compound='image', command=self.action_zoom_none)

        stream = pkg_resources.resource_stream(
            __name__,
            'images/16/disk.png',
        )
        image = Image.open(io.BytesIO(stream.read()))
        self.save_map_image = ImageTk.PhotoImage(image)
        save_map = ttk.Button(toolbar_frame, image=self.save_map_image, \
            compound='image', command=self.action_save_map)

        network_refresh.grid(row=0, column=0, sticky='nw', \
            in_=toolbar_frame)
        network_zoom_out.grid(row=0, column=1, sticky='nw', \
            in_=toolbar_frame)
        network_zoom_none.grid(row=0, column=2, sticky='nw', \
            in_=toolbar_frame)
        network_zoom_in.grid(row=0, column=3, sticky='nw', \
            in_=toolbar_frame)
        save_map.grid(row=0, column=4, sticky='nw', \
            in_=toolbar_frame)
        toolbar_frame.rowconfigure((0), weight=0)
        toolbar_frame.pack(side='top', fill='x', padx=2, pady=2)

        inner_frame = ttk.Frame(self, relief='ridge')

        network_canevas = tk.Canvas(inner_frame, bg="LightSteelBlue", width=2000, height=2000)

        network_vsb = ttk.Scrollbar(orient="vertical", command=network_canevas.yview)
        network_hsb = ttk.Scrollbar(orient="horizontal", command=network_canevas.xview)
        network_canevas.configure(yscrollcommand=lambda f, l: self.network_autoscroll(network_vsb, f, l),
            xscrollcommand=lambda f, l:self.network_autoscroll(network_hsb, f, l))
        self.network_node_in_move = None
        network_canevas.bind("<Button-1>", self._push_network_left)
        network_canevas.bind("<ButtonRelease-1>", self._release_network_left)
        network_canevas.bind("<Button-3>", self._network_popup)
        network_canevas.bind("<Motion>", self._move_network)
        #self.network_canevas.bind("<ButtonRelease-3>", relachementBoutonDroit)

        network_canevas.grid(row=0, column=0, sticky='nw', \
            in_=inner_frame)
        network_vsb.grid(row=0, column=1, sticky='e', \
            in_=inner_frame)
        network_hsb.grid(row=0, column=0, sticky='s', \
            in_=inner_frame)
        inner_frame.rowconfigure((0), weight=1)
        inner_frame.rowconfigure((1), weight=0)
        inner_frame.columnconfigure((0), weight=1)
        inner_frame.columnconfigure((1), weight=0)
        inner_frame.pack(side="top", fill="both", expand=True, padx=2, pady=2)

        self.nodes = tkNodes(network_canevas, self.zoom, options=self.options, section=self.section)
        self.nodes.load_map()

        self.menu_network = None
        self.tkroot.register_queue_cb('nodes', self.queue_nodes_cb)

    def __del__(self):
        """
        """
        try:
            self.tkroot.unregister_queue_cb('nodes', self.queue_nodes_cb)
            JntFrame.__del__(self)
        except Exception:
            pass

    def action_zoom_none(self):
        """
        """
        self.zoom = 1
        self.nodes.change_scale(self.zoom)
        self.nodes.redraw_all()

    def action_refresh(self):
        """
        """
        self.nodes.redraw_all()

    def action_save_map(self):
        """
        """
        self.nodes.save_map(self.tkroot)

    def action_zoom_in(self):
        """
        """
        self.zoom = 2 * self.zoom
        self.nodes.change_scale(self.zoom)
        self.nodes.redraw_all()

    def action_zoom_out(self):
        """
        """
        self.zoom = 0.5 * self.zoom
        self.nodes.change_scale(self.zoom)
        self.nodes.redraw_all()

    def network_autoscroll(self, sbar, first, last):
        """Hide and show scrollbar as needed."""
        first, last = float(first), float(last)
        if first <= 0 and last >= 1:
            sbar.grid_remove()
        else:
            sbar.grid()
        sbar.set(first, last)

    def _find_node_near(self, x, y):
        """
        """
        return self.nodes.search_by_canvas(x,y)

    def _delete_node(self, node):
        """
        """
        self.nodes.delete(node)

    def _draw_node(self, node):
        """
        """
        self.nodes.draw(node)

    def _move_network(self, event):
        """
        """
        #print "_move_network event %s" % event
        if self.network_node_in_move != None:
            self.nodes.move(self.network_node_in_move, event.x, event.y)

    def _release_network_left(self, event):
        """
        """
        self.network_node_in_move = None

    def _push_network_left(self, event):
        """
        """
        #print "_push_network_left event %s" % event
        if self.menu_network != None:
            self.menu_network.unpost()
            self.menu_network = None
        self.network_node_in_move = self._find_node_near(event.x, event.y)
        #print "_push_network_left node_in_move %s" % self.network_node_in_move

    def _network_popup(self, event):
        """
        """
        if self.menu_network != None:
            self.menu_network.unpost()
            self.menu_network = None
        found = self._find_node_near(event.x, event.y)
        self._create_popup_network(found)
        self.menu_network.post(event.x_root, event.y_root)
        logger.debug("[ %s ] - _network_popup for node %s", self.__class__.__name__, found)

    def _create_popup_network(self, node):
        """
        """
        self.menu_network = None
        self.menu_network = tk.Menu(self.master, tearoff=0)
        if node == None:
            self.menu_network.add_command(label="Add device", command=self.action_controller_add_device)
            self.menu_network.add_command(label="Remove device", command=self.action_controller_remove_device)
            self.menu_network.add_separator()
            self.menu_network.add_command(label="Replication", command=self.action_controller_replication_send)
            self.menu_network.add_command(label="Network update", command=self.action_controller_request_network_update)
        elif node == 1 :
            self.menu_network.add_command(label="Rename", command=lambda n=node : self.action_node_name(n))
            self.menu_network.add_command(label="Change location", command=lambda n=node : self.action_node_location(n))
            self.menu_network.add_separator()
            self.menu_network.add_command(label="Update neighbors", command=lambda n=node : self._action_controller_node_neigbhor_update(n))
            self.menu_network.add_command(label="Request informations", command=lambda n=node : self._action_controller_send_node_information(n))
            self.menu_network.add_separator()
            self.menu_network.add_command(label="Hard reset", command=self.action_controller_reset_hard())
            self.menu_network.add_command(label="Soft reset", command=self.action_controller_reset_soft())
        else :
            self.menu_network.add_command(label="Rename", command=lambda n=node : self.action_node_name(n))
            self.menu_network.add_command(label="Change location", command=lambda n=node : self.action_node_location(n))
            self.menu_network.add_separator()
            self.menu_network.add_command(label="Command classes", command=lambda n=node : self.action_node_command_classes(n))
            self.menu_network.add_separator()
            self.menu_network.add_command(label="Update neighbors", command=lambda n=node : self._action_controller_node_neigbhor_update(n))
            self.menu_network.add_command(label="Delete routes", command=lambda n=node : self._action_controller_delete_all_return_routes(n))
            self.menu_network.add_command(label="Request informations", command=lambda n=node : self._action_controller_send_node_information(n))

    def queue_nodes_cb(self, nodes):
        """
        """
        try :
            logger.debug("[ %s ] - queue_nodes_cb for nodes %s", self.__class__.__name__, nodes)
            for node in nodes:
                #~ print 'nodes[node]["hadd"]', nodes[node]["hadd"]
                hadd = nodes[node]["hadd"]
                nodes[node]['neighbors'] = self.tkroot.network.find_neighbors(hadd)
                if 'links' not in nodes[node]:
                    nodes[node]['links'] = []
                self.nodes.add(hadd, nodes[node])
                #~ self.nodes.add(nodes[node]["hadd"], nodes[node])
                #~ print("[ %s ] - node %s : %s"%(self.__class__.__name__, node, nodes[node]) )
            #~ print "subscriber_nodes_cb %s:%s" % (topic,value)
            #~ self.nodes_tree_view.set_item(topic, "value", value)
            #~ self.nodes_count['text'] = self.nodes_message % (self.nodes_tree_view.item_count)
            #~ node = topic.replace(NODES+'.','')
            #~ node = int(node)
            #~ if value[0] == '':
                #~ self.nodes.delete(node)
            #~ else :
                #~ data = json.loads(value[0], object_hook=as_python_object)
                #~ print "data : %s" % data
                #~ if node not in self.nodes.data :
                    #~ self.nodes.add(node,data)
                #~ else :
                    #~ self.nodes.update(node,data)
                    #~ #Update the node picture
                #~ print "subscriber_nodes_cb self.nodes.data[node]=%s" % (self.nodes.data[node])
        except :
            logger.exception("[ %s ] - queue_nodes_cb for nodes %s", self.__class__.__name__, nodes)
            #~ print 'subscriber_last_cb : topic / value : %s /%s' % (topic, value)
            #~ print traceback.format_exc()
            #~ print "continue"

class tkNodes(object):

    def __init__(self, canvas, scale, options=None, section='tkinter'):
        """
        """
        self.canvas = canvas
        self.scale=scale
        self.options=options
        self.section=section
        self.data = {}
        stream = pkg_resources.resource_stream(
            __name__,
            'images/wireless-7-128.png',
        )
        self.image_node = Image.open(io.BytesIO(stream.read()))

        stream = pkg_resources.resource_stream(
            __name__,
            'images/48/usb_storage.png',
        )
        self.image_controler =  Image.open(io.BytesIO(stream.read()))
        self.image_batteries = {}
        stream = pkg_resources.resource_stream(
            __name__,
            'images/48/battery_horizontal_empty.png',
        )
        self.image_batteries[0] = Image.open(io.BytesIO(stream.read()))
        stream = pkg_resources.resource_stream(
            __name__,
            'images/48/battery_horizontal_10percent.png',
        )
        self.image_batteries[1] = Image.open(io.BytesIO(stream.read()))
        stream = pkg_resources.resource_stream(
            __name__,
            'images/48/battery_horizontal_20percent.png',
        )
        self.image_batteries[2] = Image.open(io.BytesIO(stream.read()))
        stream = pkg_resources.resource_stream(
            __name__,
            'images/48/battery_horizontal_40percent.png',
        )
        self.image_batteries[3] = Image.open(io.BytesIO(stream.read()))
        stream = pkg_resources.resource_stream(
            __name__,
            'images/48/battery_horizontal_60percent.png',
        )
        self.image_batteries[4] = Image.open(io.BytesIO(stream.read()))
        stream = pkg_resources.resource_stream(
            __name__,
            'images/48/battery_horizontal_80percent.png',
        )
        self.image_batteries[5] = Image.open(io.BytesIO(stream.read()))
        stream = pkg_resources.resource_stream(
            __name__,
            'images/48/battery_horizontal_full.png',
        )
        self.image_batteries[6] = Image.open(io.BytesIO(stream.read()))
        stream = pkg_resources.resource_stream(
            __name__,
            'images/48/battery_horizontal_plugged_in.png',
        )
        self.image_batteries[7] = Image.open(io.BytesIO(stream.read()))
        self.image_sleeps = {}
        stream = pkg_resources.resource_stream(
            __name__,
            'images/48/sleep_off.png',
        )
        self.image_sleeps[0] = Image.open(io.BytesIO(stream.read()))
        stream = pkg_resources.resource_stream(
            __name__,
            'images/48/sleep_on.png',
        )
        self.image_sleeps[1] = Image.open(io.BytesIO(stream.read()))
        self.label_dx = 0
        self.label_dy = 0
        self.controler_dx = -30
        self.controler_dy = 30
        self.battery_dx = -25
        self.battery_dy = -60
        self.sleep_dx = 35
        self.sleep_dy = -50
        self.label_size = 20

    def save_map(self, tkroot):
        """
        """
        self.options.set_option(self.section, 'geometry', '%sx%s'%(tkroot.winfo_width(),tkroot.winfo_height()))
        self.options.set_option('map', 'scale', self.scale, create=True)
        for key in self.data.keys():
            self.options.set_option('map__%s'%key, 'posx', self.data[key]['posx'], create=True)
            self.options.set_option('map__%s'%key, 'posy', self.data[key]['posy'], create=True)

    def load_map(self):
        """
        """
        self.scale = float(self.options.get_option('map', 'scale', 1))
        for key in self.options.get_sections():
            if key.startswith('map__'):
                hadd = key[5:]
                if hadd not in self.data:
                    self.data[hadd] = {}
                self.data[hadd]['posx'] = int(self.options.get_option(key, 'posx', 100))
                self.data[hadd]['posy'] = int(self.options.get_option(key, 'posy', 100))
        self.change_scale(self.scale)

    def change_scale(self, scale):
        """
        """
        self.scale = scale
        iw, ih = self.image_node.size
        size = int(iw * self.scale), int(ih * self.scale)
        self.imagetk_node = ImageTk.PhotoImage(self.image_node.resize(size))
        iw, ih = self.image_controler.size
        size = int(iw * self.scale), int(ih * self.scale)
        self.imagetk_controler = ImageTk.PhotoImage(self.image_controler.resize(size))
        self.imagetk_batteries = {}
        for image in self.image_batteries:
            iw, ih = self.image_batteries[image].size
            size = int(iw * self.scale), int(ih * self.scale)
            self.imagetk_batteries[image] = ImageTk.PhotoImage(self.image_batteries[image].resize(size))
        self.imagetk_sleeps = {}
        for image in self.image_sleeps:
            iw, ih = self.image_sleeps[image].size
            size = int(iw * self.scale), int(ih * self.scale)
            self.imagetk_sleeps[image] = ImageTk.PhotoImage(self.image_sleeps[image].resize(size))
        #~ for node in self.data :
            #~ self.clean_canvas(node)
            #~ self.draw(node)
        self.redraw_all()

    def delete(self, node):
        """
        """
        self.clean_canvas(node)
        for link in self.data[node]['neighbors'] :
            if link in self.data:
                if node in self.data[link]['links']:
                    del(self.data[link]['links'][node])
        del(self.data[node])

    def clean_canvas(self, node):
        """
        """
        self.canvas.delete(self.data[node]['image_id'])
        self.canvas.delete(self.data[node]['label_id'])
        if 'ctrl_id' in self.data[node] :
            self.canvas.delete(self.data[node]['ctrl_id'])
        if 'battery_id' in self.data[node] :
            self.canvas.delete(self.data[node]['battery_id'])
        if 'sleep_id' in self.data[node] :
            self.canvas.delete(self.data[node]['sleep_id'])
        for link in self.data[node]['links'] :
            self.canvas.delete(self.data[node]['links'][link])
            for link in self.data[node]['links'] :
                self.canvas.delete(self.data[node]['links'][link])
                self.data[node]['links'][link] = None
                if link in self.data :
                    self.data[link]['links'][node] = None

    def move(self, node, x, y):
        """
        """
        self.data[node]['posx'] = x
        self.data[node]['posy'] = y
        for link in self.data[node]['links'] :
            x1, y1 = self.get_coord(link)
            #print "links = %s" % (self.data[node]['links'])
            #print "linkid = %s" % (self.data[node]['links'][link])
            #print "x1,y1 = %s.%s" % (x1, y1)
            if self.data[node]['links'][link] != None and x1 != None:
                self.canvas.coords(self.data[node]['links'][link], x, y, x1, y1)
        self.canvas.coords(self.data[node]['image_id'], x , y)
        self.canvas.coords(self.data[node]['label_id'], \
                x + self.label_dx*self.scale - self.data[node]['label_width'] / 2 , \
                y + self.label_dy*self.scale)
        if 'ctrl_id' in self.data[node] :
            self.canvas.coords(self.data[node]['ctrl_id'], \
                x + self.controler_dx*self.scale , \
                y + self.controler_dy*self.scale)
        if 'battery_id' in self.data[node] :
            self.canvas.coords(self.data[node]['battery_id'], \
                x + self.battery_dx*self.scale , \
                y + self.battery_dy*self.scale)
        if 'sleep_id' in self.data[node] :
            self.canvas.coords(self.data[node]['sleep_id'], \
                x + self.sleep_dx*self.scale , \
                y + self.sleep_dy*self.scale)

    def get_coord(self, node):
        """
        """
        if node in self.data :
            return self.data[node]['posx'], self.data[node]['posy']
        else :
            return None, None

    def add(self, node, data):
        """
        """
        if node not in self.data:
            self.data[node] = {}
            self.data[node]['posx'] = 100
            self.data[node]['posy'] = 100
        self.data[node].update(data)
        self.data[node]['links'] = {}
        self.draw(node)

    def update(self, node, data):
        """
        """
        redraw = False
        for field in data :
            if field == 'name' and self.data[node][field] != data[field]:
                redraw = True
            elif field == 'battery' and self.data[node][field] != data[field]:
                redraw = True
            elif field == 'neighbors' :
                for link in data[field]:
                    if link not in self.data[node]['links']:
                        redraw = True
            self.data[node][field] = data[field]
        if redraw:
            self.clean_canvas(node)
            self.draw(node)

    def redraw_all(self):
        """
        """
        #~ print "redraw_all"
        imgs = self.canvas.find_all()
        for img in imgs:
            self.canvas.delete(img)
        for node in self.data:
            if 'links' in self.data[node]:
                for link in self.data[node]['links']:
                    self.data[node]['links'][link] = None
                    if link in self.data :
                        self.data[link]['links'][node] = None
        for node in self.data:
            self.draw(node)

    def draw(self, node):
        """
        """
        if 'name' not in self.data[node]:
            #Not configured
            return
        #~ print "draw links for node %s" % node
        #~ for neighbor in self.data[node]['neighbors']:
            #~ print "neighbor %s" % neighbor
            #~ print "self.data[node]['links'] = %s" % self.data[node]['links']
            #~ if neighbor in self.data[node]['links'] and \
                    #~ self.data[node]['links'][neighbor] != None :
                #~ print "link to %s already exist" % neighbor
            #~ else:
                #~ print "link to %s does not exist" % neighbor
                #~ if neighbor in self.data:
                    #~ print "The neighbor %s exist" % neighbor
                    #~ if node in self.data[neighbor]['links'] and \
                            #~ self.data[neighbor]['links'][node] != None:
                        #~ print "the neighbor %s has already draw the line" % neighbor
                        #~ self.data[node]['links'][neighbor] = self.data[neighbor]['links'][node]
                    #~ else :
                        #~ print "we draw the line to %s" % neighbor
                        #~ x1,y1 = self.get_coord(neighbor)
                        #~ x0 = self.data[node]['posx']
                        #~ y0 = self.data[node]['posy']
                        #~ lnkid = self.canvas.create_line(x0, y0, x1, y1, fill='gray14')
                        #~ self.canvas.tag_lower(lnkid)
                        #~ self.data[node]['links'][neighbor] = lnkid
                        #~ self.data[neighbor]['links'][node] = lnkid
                #~ else :
                    #~ print "The neighbor %s does not exist" % neighbor
                    #~ self.data[node]['links'][neighbor] = None
        imgid = self.canvas.create_image(self.data[node]['posx'], self.data[node]['posy'], \
                image=self.imagetk_node)
        self.data[node]['image_id'] = imgid
        helv = tkFont.Font(family='Helvetica', size=int(self.label_size * self.scale))
        textw = helv.measure(self.data[node]['name'])
        self.data[node]['label_width'] = textw
        lblid = self.canvas.create_text(\
                self.data[node]['posx'] - self.data[node]['label_width'] / 2, \
                self.data[node]['posy'], text = self.data[node]['name'],\
                anchor="w", justify='center', font=helv)
        self.data[node]['label_id'] = lblid
        #~ print "draw %s" % self.data[node]['capabilities']
        #~ if 'primaryController' in self.data[node]['capabilities'] or \
                #~ 'staticUpdateController' in self.data[node]['capabilities'] or \
                #~ 'bridgeController' in self.data[node]['capabilities'] :
            #~ print "controller"
            #~ ctrlid = self.canvas.create_image( \
                    #~ self.data[node]['posx'] + self.controler_dx*self.scale, \
                    #~ self.data[node]['posy'] + self.controler_dy*self.scale, \
                    #~ image=self.imagetk_controler)
            #~ self.data[node]['ctrl_id'] = ctrlid
        #~ if 'sleeping' not in self.data[node] or self.data[node]['sleeping'] == None :
            #~ if 'sleep_id' in self.data[node]:
                #~ del(self.data[node]['sleep_id'])
        #~ elif self.data[node]['sleeping'] == False:
            #~ sleepid = self.canvas.create_image( \
                    #~ self.data[node]['posx'] + self.sleep_dx*self.scale, \
                    #~ self.data[node]['posy'] + self.sleep_dy*self.scale, \
                    #~ image=self.imagetk_sleeps[0])
            #~ self.data[node]['sleep_id'] = sleepid
        #~ elif self.data[node]['sleeping'] == True:
            #~ sleepid = self.canvas.create_image( \
                    #~ self.data[node]['posx'] + self.sleep_dx*self.scale, \
                    #~ self.data[node]['posy'] + self.sleep_dy*self.scale, \
                    #~ image=self.imagetk_sleeps[1])
            #~ self.data[node]['sleep_id'] = sleepid
        #~ if 'battery' not in self.data[node] or self.data[node]['battery'] == None :
            #~ ctrlid = self.canvas.create_image( \
                    #~ self.data[node]['posx'] + self.battery_dx*self.scale, \
                    #~ self.data[node]['posy'] + self.battery_dy*self.scale, \
                    #~ image=self.imagetk_batteries[7])
        #~ elif self.data[node]['battery'] < 5:
            #~ ctrlid = self.canvas.create_image( \
                    #~ self.data[node]['posx'] + self.battery_dx*self.scale, \
                    #~ self.data[node]['posy'] + self.battery_dy*self.scale, \
                    #~ image=self.imagetk_batteries[0])
        #~ elif self.data[node]['battery'] < 15:
            #~ ctrlid = self.canvas.create_image( \
                    #~ self.data[node]['posx'] + self.battery_dx*self.scale, \
                    #~ self.data[node]['posy'] + self.battery_dy*self.scale, \
                    #~ image=self.imagetk_batteries[1])
        #~ elif self.data[node]['battery'] < 25:
            #~ ctrlid = self.canvas.create_image( \
                    #~ self.data[node]['posx'] + self.battery_dx*self.scale, \
                    #~ self.data[node]['posy'] + self.battery_dy*self.scale, \
                    #~ image=self.imagetk_batteries[2])
        #~ elif self.data[node]['battery'] < 50:
            #~ ctrlid = self.canvas.create_image( \
                    #~ self.data[node]['posx'] + self.battery_dx*self.scale, \
                    #~ self.data[node]['posy'] + self.battery_dy*self.scale, \
                    #~ image=self.imagetk_batteries[3])
        #~ elif self.data[node]['battery'] < 70:
            #~ ctrlid = self.canvas.create_image( \
                    #~ self.data[node]['posx'] + self.battery_dx*self.scale, \
                    #~ self.data[node]['posy'] + self.battery_dy*self.scale, \
                    #~ image=self.imagetk_batteries[4])
        #~ elif self.data[node]['battery'] < 85:
            #~ ctrlid = self.canvas.create_image( \
                    #~ self.data[node]['posx'] + self.battery_dx*self.scale, \
                    #~ self.data[node]['posy'] + self.battery_dy*self.scale, \
                    #~ image=self.imagetk_batteries[5])
        #~ else:
            #~ ctrlid = self.canvas.create_image( \
                    #~ self.data[node]['posx'] + self.battery_dx*self.scale, \
                    #~ self.data[node]['posy'] + self.battery_dy*self.scale, \
                    #~ image=self.imagetk_batteries[6])
        #~ self.data[node]['battery_id'] = ctrlid

    def search_by_canvas(self, x, y):
        """
        """
        # on recherche un objet dessiné dans le canevas près de (x, y)
        pres = 1
        objets = self.canvas.find_overlapping(x - pres, y - pres, x + pres, y + pres)
        #print "objets %s" % (objets)
        if len(objets) > 0:     # s’il y en a...
            for imgid in objets :
                for node in self.data:
                    if 'image_id' in self.data[node] and \
                       'label_id' in self.data[node] and \
                        imgid in (self.data[node]['image_id'], self.data[node]['label_id']):
                        return node
        return None

class FrameRoot(ttk.Frame):

    def __init__(self, parent, options, section='tkinter'):
        ttk.Frame.__init__(self)

        self.tkroot = parent
        self.options = options
        self.section = section

        self.frame_network = FrameNetwork(self, name='state', tkroot=self.tkroot, options=self.options, section=self.section)
        self.frame_network.grid(row=0, column=0, sticky='new', pady=5, padx=5, in_=self)

        self.notebook = ttk.Notebook(self, name='notebook')
        self.notebook.grid(row=1, column=0, columnspan=3, sticky='nsew', pady=5, padx=5, in_=self)

        self.frame_map = FrameMap(self.notebook, name='map', tkroot=self.tkroot, options=self.options, section=self.section)
        self.notebook.add(self.frame_map, text='Map', underline=0, padding=2)

        self.frame_nodes = FrameNodes(self.notebook, name='nodes', tkroot=self.tkroot, options=self.options, section=self.section)
        self.notebook.add(self.frame_nodes, text='Nodes', underline=0, padding=2)

        self.rowconfigure((0), weight=0)
        self.rowconfigure((1), weight=1)
        self.columnconfigure((0), weight=1, uniform=1)
        #~ self.columnconfigure((3,4), weight=0, uniform=1)
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

