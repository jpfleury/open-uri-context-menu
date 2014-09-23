## À propos

«Open URI Context Menu» est un greffon pour gedit, l'éditeur de texte par défaut de Gnome. Ce greffon ajoute deux options dans le menu contextuel lors d'un clic droit sur une URI contenue dans le texte d'un fichier: ouverture dans le navigateur ou ouverture dans gedit pour consultation du code source.

La [version originale](http://wiki.sukimashita.com/GEdit_Plugins) a été développée par Martin Szulecki pour gedit 2.

Le présent dépôt constitue un portage du greffon vers gedit 3.

## Dépendances

Le greffon utilise la commande `xdg-open` du paquet `xdg-utils`.

## Installation

- Télécharger l'archive de la version correspondant à votre situation:

	- pour gedit 3.6 et versions antérieures: [télécharger Open URI Context Menu 1](https://github.com/jpfleury/open-uri-context-menu/archive/v1.zip);
	
	- pour gedit 3.8 et versions suivantes: [télécharger Open URI Context Menu 2](https://github.com/jpfleury/open-uri-context-menu/archive/master.zip).

- Extraire l'archive.

- Copier les fichiers `open-uri-context-menu.plugin` et `open-uri-context-menu.py` dans le dossier suivant:

		~/.local/share/gedit/plugins/

- Activer le greffon dans le menu *Édition > Préférences > Greffons* de gedit.

## Développement

Le logiciel Git est utilisé pour la gestion de versions. [Le dépôt peut être consulté en ligne ou récupéré en local.](https://github.com/jpfleury/open-uri-context-menu)

## Licence

Auteurs: Martin Szulecki <<opensuse@sukimashita.com>>, Jean-Philippe Fleury (<http://www.jpfleury.net/contact.php>)  
Copyright © Martin Szulecki, 2007-2008.  
Copyright © Jean-Philippe Fleury, 2011.

Ce programme est un logiciel libre; vous pouvez le redistribuer ou le
modifier suivant les termes de la GNU General Public License telle que
publiée par la Free Software Foundation: soit la version 3 de cette
licence, soit (à votre gré) toute version ultérieure.

Ce programme est distribué dans l'espoir qu'il vous sera utile, mais SANS
AUCUNE GARANTIE: sans même la garantie implicite de COMMERCIALISABILITÉ
ni d'ADÉQUATION À UN OBJECTIF PARTICULIER. Consultez la Licence publique
générale GNU pour plus de détails.

Vous devriez avoir reçu une copie de la Licence publique générale GNU avec
ce programme; si ce n'est pas le cas, consultez
<http://www.gnu.org/licenses/>.
