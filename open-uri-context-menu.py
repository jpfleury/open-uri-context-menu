"""
This file is part of Open URI Context Menu.
Adds context menu actions in gedit to open, browse or copy the URI under the pointer.

Copyright (C) 2011-2014, 2019, 2025 Jean-Philippe Fleury
Copyright (C) 2007-2008 Martin Szulecki

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import os
import re
import string
import subprocess

from gettext import gettext as _

from gi.repository import Gdk, Gedit, Gio, GObject, Gtk, GtkSource

ACCEPTED_SCHEMES = ["file", "ftp", "sftp", "smb", "dav", "davs", "ssh", "http", "https"]
RE_DELIM = re.compile(r"[\w#/\?:%@&=+\.'\\~\-']+", re.UNICODE | re.MULTILINE)
RE_URI_RFC2396 = re.compile(
    r"((([a-zA-Z][0-9a-zA-Z+\-\.]*):)?/{0,2}"
    r"([0-9a-zA-Z;:,/\?@&=\+\$\.\-_!~\*'\(\)%]+))?"
    r"(#[0-9a-zA-Z;,/\?:@&\=+$\.\\-_!~\*'\(\)%]+)?"
)


class OpenURIContextMenuPlugin(GObject.Object, Gedit.WindowActivatable):
    __gtype_name__ = "OpenURIContextMenuPlugin"
    window = GObject.property(type=Gedit.Window)

    def __init__(self):
        GObject.Object.__init__(self)
        self.uri = ""
        self.window = None
        self.encoding = GtkSource.Encoding.get_from_charset("UTF-8")

    def do_activate(self):
        handler_ids = []
        for signal in ("tab-added", "tab-removed"):
            method = getattr(self, "on_window_" + signal.replace("-", "_"))
            handler_ids.append(self.window.connect(signal, method))
        self.window.OpenURIContextMenuPluginID = handler_ids
        for view in self.window.get_views():
            self.connect_view(view)

    def do_deactivate(self):
        widgets = [self.window] + self.window.get_views()
        for widget in widgets:
            handler_ids = widget.OpenURIContextMenuPluginID
            if not handler_ids is None:
                for handler_id in handler_ids:
                    widget.disconnect(handler_id)
            widget.OpenURIContextMenuPluginID = None
        self.window = None

    def connect_view(self, view):
        handler_id = view.connect("populate-popup", self.on_view_populate_popup)
        view.OpenURIContextMenuPluginID = [handler_id]

    def update_ui(self, window):
        pass

    def browse_url(self, menu_item, url):
        command = ["xdg-open", url]
        if os.getuid() == 0 and os.environ.has_key("SUDO_USER"):
            command = ["sudo", "-u", os.environ["SUDO_USER"]] + command
        subprocess.Popen(command)

    def on_window_tab_added(self, window, tab):
        self.connect_view(tab.get_view())

    def on_window_tab_removed(self, window, tab):
        pass

    def on_view_populate_popup(self, view, menu):
        doc = view.get_buffer()
        win = view.get_window(Gtk.TextWindowType.TEXT)
        ptr_window, x, y, mod = win.get_pointer()
        x, y = view.window_to_buffer_coords(Gtk.TextWindowType.TEXT, x, y)

        # First try at pointer location
        insert = view.get_iter_at_location(x, y)
        if isinstance(insert, tuple):
            insert = insert[1] if insert[0] else None

        # Second try at cursor
        if insert == None:
            insert = doc.get_iter_at_mark(doc.get_insert())
            if isinstance(insert, tuple):
                insert = insert[1] if insert[0] else None

        while insert.forward_char():
            if not RE_DELIM.match(insert.get_char()):
                break

        start = insert.copy()
        while start.backward_char():
            if not RE_DELIM.match(start.get_char()):
                start.forward_char()
                break

        word = doc.get_text(start, insert, False)
        if len(word) == 0:
            return True

        word = self.validate_uri(word)
        if not word:
            return True

        displayed_word = word
        if len(displayed_word) > 50:
            displayed_word = displayed_word[:50] + "\u2026"

        copy_uri_item = Gtk.ImageMenuItem(_("Copy '%s'") % (displayed_word))
        copy_uri_item.set_image(
            Gtk.Image.new_from_stock(Gtk.STOCK_COPY, Gtk.IconSize.MENU)
        )
        copy_uri_item.connect("activate", self.on_copy_uri_activate, word)
        copy_uri_item.show()

        browse_to = False
        if word.startswith("http://") or word.startswith("https://"):
            browse_to = True

        if browse_to:
            browse_uri_item = Gtk.ImageMenuItem(_("Browse to '%s'") % (displayed_word))
            browse_uri_item.set_image(
                Gtk.Image.new_from_stock(Gtk.STOCK_JUMP_TO, Gtk.IconSize.MENU)
            )
            browse_uri_item.connect("activate", self.browse_url, word)
            browse_uri_item.show()

        open_uri_item = Gtk.ImageMenuItem(_("Open '%s'") % (displayed_word))
        open_uri_item.set_image(
            Gtk.Image.new_from_stock(Gtk.STOCK_OPEN, Gtk.IconSize.MENU)
        )
        open_uri_item.connect("activate", self.on_open_uri_activate, word)
        open_uri_item.show()

        separator = Gtk.SeparatorMenuItem()
        separator.show()
        menu.prepend(separator)
        menu.prepend(copy_uri_item)
        menu.prepend(open_uri_item)

        if browse_to:
            menu.prepend(browse_uri_item)
        return True

    def on_copy_uri_activate(self, menu_item, uri):
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        clipboard.set_text(uri, -1)
        clipboard.store()
        return True

    def on_open_uri_activate(self, menu_item, uri):
        self.open_uri(uri)
        return True

    def validate_uri(self, uri):
        m = RE_URI_RFC2396.search(uri)
        if not m:
            return False

        target = m.group()

        if m.group(4) == None or m.group(4) == "/":
            return False

        if m.group(2) != None:
            if m.group(3) in ACCEPTED_SCHEMES:
                return target
            else:
                return False
        else:
            if m.group(4).startswith("www."):
                return "http://" + target

        target = os.path.expanduser(target)
        if os.path.isfile(target):
            if os.path.isabs(target):
                return "file://" + target

        doc_dir = self.window.get_active_document().get_uri_for_display()
        if doc_dir != None:
            if doc_dir.startswith("file://"):
                f = os.path.join(os.path.dirname(doc_dir), target)
                if os.path.isfile(f.replace("file://", "", 1)):
                    return f
            else:
                return os.path.join(os.path.dirname(doc_dir), target)

        paths = string.split(os.environ["PATH"], os.pathsep)
        for dirname in paths:
            f = os.path.join(os.path.dirname(dirname), "include", target)
            if os.path.isfile(f):
                return "file://" + f

        return False

    def get_document_by_uri(self, uri):
        docs = self.window.get_documents()
        for d in docs[:]:
            if d.get_file().get_location() == uri:
                return d
        return None

    def open_uri(self, uri):
        doc = self.get_document_by_uri(uri)
        if doc != None:
            tab = Gedit.tab_get_from_document(doc)
            self.window.set_active_tab(tab)
        else:
            file_obj = Gio.file_new_for_uri(uri)
            tab = self.window.get_tab_from_location(file_obj)
            if tab:
                self.window.set_active_tab(tab)
            else:
                Gedit.commands_load_location(self.window, file_obj, self.encoding, 0, 0)
            status = self.window.get_statusbar()
            status_id = status.push(
                status.get_context_id("OpenURIContextMenuPlugin"),
                _("Loading file '%s'...") % (uri),
            )
            GObject.timeout_add(
                4000,
                self.on_statusbar_timeout,
                status,
                status.get_context_id("OpenURIContextMenuPlugin"),
                status_id,
            )

    def on_statusbar_timeout(self, status, context_id, status_id):
        status.remove(context_id, status_id)
        return False
