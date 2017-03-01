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

        self.symlink_label = pyxbmct.Label("Symlink destination")
        self.placeControl(self.symlink_label, 7, 0, columnspan=2)

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

        self.symlink_edit = pyxbmct.Edit("Set symlink destination")
        self.placeControl(self.symlink_edit, 8, 0, columnspan=2)

    def add_radiobuttons(self):
        self.files_radiobutton = pyxbmct.RadioButton("Select all files inside the directory")
        self.placeControl(self.files_radiobutton, 6, 0, columnspan=2)

        self.symlink_radiobutton = pyxbmct.RadioButton("Use symlinks")
        self.placeControl(self.symlink_radiobutton, 10, 0, columnspan=2)

    def add_buttons(self):
        self.source_browse_button = pyxbmct.Button("Browse")
        self.placeControl(self.source_browse_button, 2, 0)

        self.source_clear_button = pyxbmct.Button("Clear")
        self.placeControl(self.source_clear_button, 2, 1)

        self.files_browse_button = pyxbmct.Button("Browse")
        self.placeControl(self.files_browse_button, 5, 0)

        self.files_clear_button = pyxbmct.Button("Clear")
        self.placeControl(self.files_clear_button, 5, 1)

        self.symlink_browse_button = pyxbmct.Button("Browse")
        self.placeControl(self.symlink_browse_button, 9, 0)

        self.symlink_clear_button = pyxbmct.Button("Clear")
        self.placeControl(self.symlink_clear_button, 9, 1)

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
        self.connect(self.symlink_browse_button, self.symlink_browse)
        self.connect(self.symlink_clear_button, self.symlink_clear)
        self.connect(self.symlink_radiobutton, self.symlink_radiobutton_handler)
        self.symlink_radiobutton_handler()
        self.connect(self.settings_button, addon.openSettings)
        self.connect(self.close_button, self.close)
        self.connect(self.start_button, self.start)

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

    def symlink_browse(self):
        self.symlink_edit.setText(self.dialog.choose_directory("Select symlink target directory"))

    def symlink_clear(self):
        self.symlink_edit.setText("")

    def symlink_radiobutton_handler(self):
        use_symlinks = self.symlink_radiobutton.isSelected()

        if use_symlinks:
            # Not yet implemented
            self.dialog.ok("Alert", "This feature is not yet implemented.")
            self.symlink_radiobutton.setSelected(False)
            self.symlink_radiobutton_handler()
#            self.symlink_label.setEnabled(True)
#            self.symlink_edit.setEnabled(True)
#            self.symlink_browse_button.setEnabled(True)
#            self.symlink_clear_button.setEnabled(True)
        else:
            self.symlink_label.setEnabled(False)
            self.symlink_edit.setEnabled(False)
            self.symlink_browse_button.setEnabled(False)
            self.symlink_clear_button.setEnabled(False)

    def start(self):
        # get settings
        self.debug = addon.getSetting('debug')

        # parse data from Edits
        source_path = self.source_edit.getText()

        if self.check_if_empty(source_path):
            self.dialog.alert("You must specify the source directory.")
            return

        all_files = self.files_radiobutton.isSelected()

        if all_files:
            paths = (source_path,)
        else:
            filenames = self.files_edit.getText()

            if self.check_if_empty(filenames):
                self.dialog.alert("You should specify, what files to select.")
                return

            filenames = filenames.split('; ')
            paths = [os.path.join(source_path, filename) 
                     for filename in filenames]
            paths = tuple(paths)

        regex = self.regex_edit.getText()

        if self.check_if_empty(regex):
            self.dialog.alert("You must specify a regular expression.")
            return

        if self.debug == "true":
            debug = True
        else:
            debug = False

        rename(config=None, canonical=None, debug=debug, dry_run=False,
                episode=None, ignore_filelist=(), log_file=None,
                log_level=None, name=None, no_cache=False,
                output_format=None, organise=True, partial=False,
                quiet=False, recursive=False, rename_dir=None,
                regex=regex, season=None, show=None,
                show_override=None, specials=None, symlink=False,
                the=False, paths=paths)

        from tvrenamr.logs import log_buffer
        self.dialog.notification("Done", "Check log for more information!")

        # display log
        self.dialog.textviewer("Log", log_buffer.getvalue())
        log_buffer.truncate(0)

    def check_if_empty(self, string):
        if string == "":
            return True
        else:
            return False

window = RenamerDialog("TV Show renamer")
window.doModal()
del window
