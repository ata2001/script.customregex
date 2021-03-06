# script.customregex
# Copyright 2017 Attila Szöllősi
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import xbmc
import xbmcaddon
import xbmcgui
import pyxbmct
import sys
import os

addon = xbmcaddon.Addon()
addon_version = addon.getAddonInfo('version')
addon_language = addon.getLocalizedString
addon_path = addon.getAddonInfo('path').decode("utf-8")
sys.path.append(xbmc.translatePath(os.path.join(addon_path, 'resources', 'lib')))

from misc import Dialog
from tvrenamr.cli.core import rename
from tvrenamr.logs import start_logging

class RenamerDialog(pyxbmct.AddonDialogWindow):
    def __init__(self, title):
        super(RenamerDialog, self).__init__(title)

        # Use the old confluence theme, when we're on confluence
        if xbmc.getSkinDir() == "skin.confluence":
            pyxbmct.skin.estuary = False

        self.setGeometry(830, 590, 11, 4)
        self.dialog = Dialog()

        self.add_controls()
        self.connect_controls()
        self.set_navigation()

        self.load_settings()
        if self.debug:
            log_level = 10
        else:
            log_level = None
        start_logging(None, log_level, False)

    def add_controls(self):
        self.add_labels()
        self.add_textboxes()
        self.add_edits()
        self.add_radiobuttons()
        self.add_buttons()

    def add_labels(self):
        self.source_label = pyxbmct.Label("Source path:")
        self.placeControl(self.source_label, 0, 0, columnspan=2)

        self.customRe_label = pyxbmct.Label("Custom regular expression:")
        self.placeControl(self.customRe_label, 0, 2, columnspan=2) 

        self.files_label = pyxbmct.Label("Files to select:")
        self.placeControl(self.files_label, 3, 0, columnspan=2)

        self.help_label = pyxbmct.Label("Help")
        self.placeControl(self.help_label, 2, 2, columnspan=2)

        self.destination_label = pyxbmct.Label("Destination:")
        self.placeControl(self.destination_label, 7, 0, columnspan=2)

    def add_textboxes(self):
        self.help_textbox = pyxbmct.TextBox()
        self.placeControl(self.help_textbox, 3, 2, rowspan=6, columnspan=2)
        self.help_textbox.setText("""Replace the parts of the filename with the following strings:

The name of the show:          %n
Season:                                     %s
Episode:                                    %e

Example:

Regular.Show.S01.E01.mkv -->
%n.S%s.E%e.mkv
                                     """)
        self.help_textbox.autoScroll(3000, 4000, 6000)

    def add_edits(self):
        self.source_edit = pyxbmct.Edit("Set source path")
        self.placeControl(self.source_edit, 1, 0, columnspan=2)

        self.regex_edit = pyxbmct.Edit("Set custom regular expression")
        self.placeControl(self.regex_edit, 1, 2, columnspan=2)

        self.files_edit = pyxbmct.Edit("Files to select")
        self.placeControl(self.files_edit, 4, 0, columnspan=2)

        self.destination_edit = pyxbmct.Edit("Set destination")
        self.placeControl(self.destination_edit, 8, 0, columnspan=2)

    def add_radiobuttons(self):
        self.files_radiobutton = pyxbmct.RadioButton("Select all files inside the directory")
        self.placeControl(self.files_radiobutton, 6, 0, columnspan=2)

        self.working_dir_radiobutton = pyxbmct.RadioButton("Stay in working directory")
        self.placeControl(self.working_dir_radiobutton, 10, 0)

        self.symlink_radiobutton = pyxbmct.RadioButton("Use symlinks")
        self.placeControl(self.symlink_radiobutton, 10, 1)

    def add_buttons(self):
        self.source_browse_button = pyxbmct.Button("Browse")
        self.placeControl(self.source_browse_button, 2, 0)

        self.source_clear_button = pyxbmct.Button("Clear")
        self.placeControl(self.source_clear_button, 2, 1)

        self.files_browse_button = pyxbmct.Button("Browse")
        self.placeControl(self.files_browse_button, 5, 0)

        self.files_clear_button = pyxbmct.Button("Clear")
        self.placeControl(self.files_clear_button, 5, 1)

        self.destination_browse_button = pyxbmct.Button("Browse")
        self.placeControl(self.destination_browse_button, 9, 0)

        self.destination_clear_button = pyxbmct.Button("Clear")
        self.placeControl(self.destination_clear_button, 9, 1)

        self.help_button = pyxbmct.Button("Help")
        self.placeControl(self.help_button, 9, 2)

        self.settings_button = pyxbmct.Button("Settings")
        self.placeControl(self.settings_button, 9, 3)

        self.close_button = pyxbmct.Button("Close")
        self.placeControl(self.close_button, 10, 2)

        self.start_button = pyxbmct.Button("Start")
        self.placeControl(self.start_button, 10, 3)

    def connect_controls(self):
        self.connect(self.source_browse_button, self.source_browse)
        self.connect(self.source_clear_button, self.source_clear)
        self.connect(self.files_browse_button, self.files_browse)
        self.connect(self.files_clear_button, self.files_clear)
        self.connect(self.files_radiobutton, self.files_all)
        self.connect(self.destination_browse_button, self.destination_browse)
        self.connect(self.destination_clear_button, self.destination_clear)
        self.connect(self.working_dir_radiobutton, self.working_dir_radiobutton_handler)
        self.connect(self.settings_button, addon.openSettings)
        self.connect(self.close_button, self.close)
        self.connect(self.start_button, self.start)

    def set_navigation(self):
        """Set navigations for remote control."""
        self.source_edit.controlDown(self.source_browse_button)
        self.source_edit.controlRight(self.regex_edit)

        self.source_browse_button.controlDown(self.files_edit)
        self.source_browse_button.controlUp(self.source_edit)
        self.source_browse_button.controlLeft(self.source_clear_button)
        self.source_browse_button.controlRight(self.source_clear_button)

        self.source_clear_button.controlDown(self.files_edit)
        self.source_clear_button.controlUp(self.source_edit)
        self.source_clear_button.controlLeft(self.source_browse_button)

        self.files_edit.controlDown(self.files_browse_button)
        self.files_edit.controlUp(self.source_clear_button)

        self.files_browse_button.controlDown(self.files_radiobutton)
        self.files_browse_button.controlUp(self.files_edit)
        self.files_browse_button.controlRight(self.files_clear_button)

        self.files_clear_button.controlDown(self.files_radiobutton)
        self.files_clear_button.controlUp(self.files_edit)
        self.files_clear_button.controlLeft(self.files_browse_button)

        self.files_radiobutton.controlDown(self.destination_edit)
        self.files_radiobutton.controlUp(self.files_clear_button)

        self.destination_edit.controlDown(self.destination_browse_button)
        self.destination_edit.controlUp(self.files_radiobutton)

        self.destination_browse_button.controlDown(self.working_dir_radiobutton)
        self.destination_browse_button.controlUp(self.destination_edit)
        self.destination_browse_button.controlRight(self.destination_clear_button)

        self.destination_clear_button.controlDown(self.symlink_radiobutton)
        self.destination_clear_button.controlUp(self.destination_edit)
        self.destination_clear_button.controlLeft(self.destination_browse_button)
        self.destination_clear_button.controlRight(self.help_button)

        self.working_dir_radiobutton.controlUp(self.destination_browse_button)
        self.working_dir_radiobutton.controlRight(self.symlink_radiobutton)

        self.symlink_radiobutton.controlUp(self.destination_clear_button)
        self.symlink_radiobutton.controlLeft(self.working_dir_radiobutton)
        self.symlink_radiobutton.controlRight(self.close_button)

        self.regex_edit.controlDown(self.help_button)
        self.regex_edit.controlLeft(self.source_edit)

        self.help_button.controlDown(self.close_button)
        self.help_button.controlUp(self.regex_edit)
        self.help_button.controlLeft(self.destination_clear_button)
        self.help_button.controlRight(self.settings_button)

        self.settings_button.controlDown(self.start_button)
        self.settings_button.controlUp(self.regex_edit)
        self.settings_button.controlLeft(self.help_button)

        self.close_button.controlUp(self.help_button)
        self.close_button.controlLeft(self.symlink_radiobutton)
        self.close_button.controlRight(self.start_button)

        self.start_button.controlUp(self.settings_button)
        self.start_button.controlLeft(self.close_button)

        #set initial focus
        self.setFocus(self.source_edit)

    def source_browse(self):
        self.source_edit.setText(self.dialog.choose_directory("Select source directory"))

    def source_clear(self):
        self.source_edit.setText("")

    def files_browse(self):
        parent = self.source_edit.getText()
        self.files = os.listdir(parent)
        self.file_indices = self.dialog.multiselect('Select files', self.files)
        files_to_select = [self.files[i] for i in self.file_indices]
        self.files_edit.setText('; '.join(files_to_select))

        # Copy one of the filenames to the regex form
        self.regex_edit.setText(files_to_select[0])

    def files_clear(self):
        self.files_edit.setText("")

    def files_all(self):
        if self.files_radiobutton.isSelected():
            self.files_label.setEnabled(False)
            self.files_edit.setEnabled(False)
            self.files_browse_button.setEnabled(False)
            self.files_clear_button.setEnabled(False)

            # Copy one of the filenames to the regex form
            files = os.listdir(self.source_edit.getText())
            self.regex_edit.setText(files[0])
        else:
            self.files_edit.setEnabled(True)
            self.files_label.setEnabled(True)
            self.files_browse_button.setEnabled(True)
            self.files_clear_button.setEnabled(True)

    def destination_browse(self):
        self.destination_edit.setText(self.dialog.choose_directory("Select target directory"))

    def destination_clear(self):
        self.destination_edit.setText("")

    def working_dir_radiobutton_handler(self):
        use_working_dir = self.working_dir_radiobutton.isSelected()
        if use_working_dir:
            self.destination_label.setEnabled(False)
            self.destination_edit.setEnabled(False)
            self.destination_browse_button.setEnabled(False)
            self.destination_clear_button.setEnabled(False)
        else:
            self.destination_label.setEnabled(True)
            self.destination_edit.setEnabled(True)
            self.destination_browse_button.setEnabled(True)
            self.destination_clear_button.setEnabled(True)

    def start(self):
        # load settings
        self.load_settings()

        # parse data from Edits
        source_path = self.source_edit.getText()

        if not source_path:
            self.dialog.alert("You must specify the source directory.")
            return

        all_files = self.files_radiobutton.isSelected()

        if all_files:
            paths = (source_path,)
        else:
            filenames = self.files_edit.getText()

            if not filenames:
                self.dialog.alert("You must specify, what files to select.")
                return

            filenames = filenames.split('; ')
            paths = [os.path.join(source_path, filename) 
                     for filename in filenames]
            paths = tuple(paths)

        stay_in_working_dir = self.working_dir_radiobutton.isSelected()
        if stay_in_working_dir:
            destination = None
        else:
            destination = self.destination_edit.getText()
            if not destination:
                self.dialog.alert("You must specify a destination path.")
                return

        use_symlink = self.symlink_radiobutton.isSelected()

        regex = self.regex_edit.getText()

        if not regex:
            self.dialog.alert("You must specify a regular expression.")
            return

        rename(config=None, canonical=None, debug=self.debug,
                dry_run=self.dry_run, episode=None,
                ignore_filelist=(), log_file=None, log_level=None,
                name=None, no_cache=False,
                output_format=self.output_format,
                organise=self.organise, partial=self.partial,
                quiet=False, recursive=self.recursive, rename_dir=destination,
                regex=regex, season=None, show=None,
                show_override=None, specials=None, symlink=use_symlink,
                the=self.the, paths=paths)

        from tvrenamr.logs import log_buffer
        self.dialog.notification("Done", "Check log for more information!")

        # display log
        self.dialog.textviewer("Log", log_buffer.getvalue())
        log_buffer.truncate(0)

    def load_settings(self):
        self.output_format = addon.getSetting('output_format')
        self.output_format = self.output_format.encode('utf8')
        self.organise = addon.getSetting('organise')
        self.organise = self.organise == 'true'
        self.partial = addon.getSetting('partial')
        self.partial = self.partial == 'true'
        self.recursive = addon.getSetting('recursive')
        self.recursive = self.recursive == 'true'
        self.the = addon.getSetting('the')
        self.the = self.the == 'true'
        self.dry_run = addon.getSetting('dry_run')
        self.dry_run = self.dry_run == 'true'
        self.debug = addon.getSetting('debug')
        self.debug = self.debug == 'true'


if __name__ == "__main__":
    window = RenamerDialog("TV Show renamer")
    window.doModal()
    del window
