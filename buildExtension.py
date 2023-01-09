from __future__ import absolute_import
from __future__ import print_function
import os
from mojo.extensions import ExtensionBundle


basePath = os.path.dirname(__file__)
extensionPath = os.path.join(basePath, "ThemeManager.roboFontExt")
libPath = os.path.join(basePath, "lib")
htmlPath = os.path.join(basePath, "html")
resourcesPath = os.path.join(basePath, "resources")

B = ExtensionBundle()

B.name = "Theme Manager"
B.version = "1.0.6"
B.developer = "Connor Davenport and Andy Clymer"
B.developerURL = 'http://www.connordavenport.com/ http://www.andyclymer.com/'

B.launchAtStartUp = False
B.addToMenu = [
    {
        'path' : 'ThemeManager.py',
        'preferredName': 'Theme Manager...',
        'shortKey' : '',
    }]

B.requiresVersionMajor = '3'
B.requiresVersionMinor = '1'
B.infoDictionary["html"] = True

B.save(extensionPath, libPath=libPath, htmlPath=htmlPath, resourcesPath=resourcesPath, pycOnly=False)

print("Done")
