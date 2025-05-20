## Overview

"Open URI Context Menu" is a plugin for gedit, the default GNOME text editor. This plugin adds 3 context menu items when you right-click on a URI present in the file content:

- open in the browser
- open in gedit to view the source code
- copy to the clipboard

![Context menu in gedit with URI options](https://raw.githubusercontent.com/jpfleury/open-uri-context-menu/master/assets/example-context-menu.png)

## Requirements

The plugin uses the `xdg-open` command from the `xdg-utils` package.

## Installation

- Download the appropriate version according to your setup:

	- for gedit 3.0 to 3.6: [download Open URI Context Menu v1](https://github.com/jpfleury/open-uri-context-menu/archive/v1.zip);
	
	- for gedit 3.8 to 3.12: [download Open URI Context Menu v2](https://github.com/jpfleury/open-uri-context-menu/archive/v2.zip);
	
	- for gedit 3.14 to 3.28: [download Open URI Context Menu v3](https://github.com/jpfleury/open-uri-context-menu/archive/v3.zip);
	
	- for gedit 3.36 to 3.38: [download Open URI Context Menu v4](https://github.com/jpfleury/open-uri-context-menu/archive/v4.zip);
	
	- for gedit 41 and later: [download Open URI Context Menu v5](https://github.com/jpfleury/open-uri-context-menu/archive/master.zip);

- Extract the archive.

- Copy the files `open-uri-context-menu.plugin` and `open-uri-context-menu.py` into the following folder:

		~/.local/share/gedit/plugins/

- Enable the plugin in the gedit menu *Edit > Preferences > Plugins*.

## Development

Git is used for version control. [The repository can be browsed online or cloned.](https://github.com/jpfleury/open-uri-context-menu)

The original version was developed by Martin Szulecki for gedit 2. The current repository is a port of the plugin for gedit 3 and later versions.

## License

Copyright © 2011-2014, 2019, 2025 Jean-Philippe Fleury <https://github.com/jpfleury>  
Copyright © 2007-2008 Martin Szulecki <opensuse@sukimashita.com>

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
