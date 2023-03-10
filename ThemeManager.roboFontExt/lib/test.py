'''
Make scripting API seperate file
Get glyph view working
'''

import os
from copy import deepcopy, copy
import plistlib
import AppKit
import ezui
from fontParts.fontshell import RBPoint
from fontParts.world import OpenFont
import importlib
from mojo.UI import getDefault, setDefault
from mojo.extensions import getExtensionDefault, setExtensionDefault, ExtensionBundle
from lib.tools.notifications import PostNotification
import ThemeManagerScripting as themeScripter
     
            
themes = themeScripter.loadUserDefinedThemes()
setExtensionDefault(themeScripter.DEFAULTSKEY, {})
    
    
    # print(theme["themeName"])
    
    # themeStorage = dict(
    #     themeName=theme["themeName"],
    #     themeType="Default"
    # )
        
    # for keyName, _, dataType in THEMEKEYS:
    #     themeStorage[keyName]  =  dataType(theme[keyName])
            
    # for keyName, _, dataType in DARKTHEMEKEYS:
    #     if keyName in theme:
    #         themeStorage[keyName]  =  dataType(theme[keyName])
    #     else:
    #         themeStorage[keyName]  =  dataType(theme[keyName.replace(".dark","")])

    # fileName = f"{theme['themeName'].replace(' ','')}.roboFontTheme"
    
    # with open(fileName, "wb") as themeFile:
    #     plistlib.dump(themeStorage, themeFile)

    # print(themeStorage)