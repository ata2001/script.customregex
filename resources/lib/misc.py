import xbmc
import xbmcaddon
import xbmcgui
import pyxbmct
import sys

class Dialog(xbmcgui.Dialog):
    def __init__(self):
        self.superclass = super(Dialog, self)
        self.superclass.__init__()

    def alert(self, msg, title="Alert"):
        self.superclass.notification(title, msg, xbmcgui.NOTIFICATION_ERROR)

    def choose_directory(self, title):
        return self.superclass.browse(3, title, 'files')
