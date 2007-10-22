# Copyright (C) 2007-2008 Martin Szulecki
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

'''
Adds context menu item to open an URI at the pointer position

Testcases (some still fail):

- #include <linux/smb.h>
- <openuricontextmenu.gedit-plugin>, "openuricontextmenu.gedit-plugin"
- (../plugins/openuricontextmenu.gedit-plugin)
- ~/.gnome2/gedit/plugins/openuricontextmenu.gedit-plugin
- http://www.gnome.org/~home/index.php3?test=param&another=one#final_anchor
- mailto:myself@page.com?subject=Some%20matter+me
- http://www.google.com/search?sourceid=navclient&ie=UTF-8&rls=GGLC,GGLC:1969-53,GGLC:en&q=uri+query
- openuricontextmenu.gedit-plugin,openuricontextmenu.py
- https://bugzilla.novell.com
- SOMEVAR=file:///var/log/messages

Loads of room for improving the URI detection ;)

Version: 0.2.0
'''

from gettext import gettext as _

import gtk
import gobject
import gedit
import re
import sys
import os
import string

OPEN_SCHEMES = ['file', 'http', 'https', 'ftp', 'sftp', 'smb', 'dav', 'davs', 'ssh']

RE_DELIM = re.compile(r'[\w#/\?:%@&\=\+\.\\~-]+', re.UNICODE|re.MULTILINE)
RE_URI_RFC2396 = re.compile("((([a-zA-Z][0-9a-zA-Z+\\-\\.]*):)?/{0,2}[0-9a-zA-Z;:,/\?@&=\+\$\.\-_!~\*'\(\)%]+)?(#[0-9a-zA-Z;,/\?:@&\=+$\.\\-_!~\*'\(\)%]+)?")

class OpenURIContextMenuPlugin(gedit.Plugin):
	def __init__(self):
		gedit.Plugin.__init__(self)

		self.uri = ""
		self.window = None
		self.id_name = 'OpenURIContextMenuPluginID'
		self.encoding = gedit.encoding_get_from_charset("UTF-8")

	def activate(self, window):
		self.window = window

		handler_ids = []
		for signal in ('tab-added', 'tab-removed'):
			method = getattr(self, 'on_window_' + signal.replace('-', '_'))
			handler_ids.append(window.connect(signal, method))
		window.set_data(self.id_name, handler_ids)

		for view in window.get_views():
			self.connect_view(view)

	def deactivate(self, window):
		widgets = [window] + window.get_views()
		for widget in widgets:
			handler_ids = widget.get_data(self.id_name)
			if not handler_ids is None:
				for handler_id in handler_ids:
					widget.disconnect(handler_id)
			widget.set_data(self.id_name, None)

		self.window = None

	def connect_view(self, view):
		handler_id = view.connect('populate-popup', self.on_view_populate_popup)
		view.set_data(self.id_name, [handler_id])

	def update_ui(self, window):
		pass

	def on_window_tab_added(self, window, tab):
		self.connect_view(tab.get_view())

	def on_window_tab_removed(self, window, tab):
		pass

	def on_view_populate_popup(self, view, menu):
		doc = view.get_buffer()

		win = view.get_window(gtk.TEXT_WINDOW_TEXT);
		x, y, mod = win.get_pointer()
		x, y = view.window_to_buffer_coords(gtk.TEXT_WINDOW_TEXT, x, y);

		# First try at pointer location
		insert = view.get_iter_at_location(x, y);
		
		# Second try at cursor
		if insert == None:
			insert = doc.get_iter_at_mark(doc.get_insert())
			
		while insert.forward_char():
			if not RE_DELIM.match(insert.get_char()):
				break

		start = insert.copy()
		while start.backward_char():
			if not RE_DELIM.match(start.get_char()):
				start.forward_char();
				break

		word = unicode(doc.get_text(start, insert))

		if len(word) == 0:
			return True

		word = self.validate_uri(word)
		if not word:
			return True

		open_uri_item = gtk.ImageMenuItem(_("Open '%s'") % (word.replace('file://', '')))
		open_uri_item.set_image(gtk.image_new_from_stock(gtk.STOCK_OPEN, gtk.ICON_SIZE_MENU))
		open_uri_item.connect('activate', self.on_open_uri_activate, word);
		open_uri_item.show();

		separator = gtk.SeparatorMenuItem()
		separator.show();

		menu.prepend(separator)
		menu.prepend(open_uri_item)
		return True
	
	def on_open_uri_activate(self, menu_item, uri):
		self.open_uri(uri)
		return True
	
	def validate_uri(self, uri):
		m = RE_URI_RFC2396.search(uri);
		if not m:
			return False
		
		target = m.group()
		
		if m.group(2) != None:
			if m.group(3) in OPEN_SCHEMES:
				return target
			else:
				return False
		
		target = os.path.expanduser(target)

		if os.path.isfile(target):
			if os.path.isabs(target):
				return 'file://' + target
		
		doc_dir = self.window.get_active_document().get_uri()
		if doc_dir != None:
			if doc_dir.startswith('file://'):
				f = os.path.join(os.path.dirname(doc_dir), target)
				if os.path.isfile(f.replace('file://', '', 1)):
					return f
			else:
				return os.path.join(os.path.dirname(doc_dir), target)
		
		paths = string.split(os.environ["PATH"], os.pathsep)
		for dirname in paths:
			f = os.path.join(os.path.dirname(dirname), 'include', target)
			if os.path.isfile(f):
				return 'file://' + f

		return False

	def get_document_by_uri(self, uri):
		docs = self.window.get_documents()

		for d in docs [:]:
			if d.get_uri() == uri:
				return d
		return None

	def open_uri(self, uri):
		doc = self.get_document_by_uri(uri)
		if doc != None :
			tab = gedit.tab_get_from_document(doc)
			self.window.set_active_tab(tab)
		else:
			self.window.create_tab_from_uri(uri, self.encoding, 0, False, True)
			status = self.window.get_statusbar()
			status_id = status.push(status.get_context_id(self.id_name), _("Loading file '%s'...") % (uri))
			gobject.timeout_add(4000, self.on_statusbar_timeout, status, status.get_context_id(self.id_name), status_id)

	def on_statusbar_timeout(self, status, context_id, status_id):
		status.remove(context_id, status_id)
		return False

