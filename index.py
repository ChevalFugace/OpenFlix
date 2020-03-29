import xbmc
import xbmcgui
import xbmcaddon
import os

ADDON = xbmcaddon.Addon()
CWD = ADDON.getAddonInfo('path').decode('utf-8')

class OpenFlixGUI(xbmcgui.WindowXML):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def onInit(self):

        xbmc.executebuiltin('Container.SetViewMode(50)')

        listitems = list()

        listitem1 = xbmcgui.ListItem('my first item')
        listitems.append(listitem1)

        listitem2 = xbmcgui.ListItem('my second item')
        listitems.append(listitem2)

        self.clearList()

        self.addItems(listitems)
        xbmc.sleep(100)
    
        self.setFocusId(self.getCurrentContainerId())


if (__name__ == "__main__"):
    print(CWD)
    ui = OpenFlixGUI("main.xml", CWD)
    ui.doModal()

    del ui
