from AppKit import *
import os

import vanilla
from mojo.UI import GetFile, PutFile
from mojo.UI import getDefault, setDefault
from mojo.extensions import getExtensionDefault, setExtensionDefault, ExtensionBundle
from mojo.roboFont import OpenWindow

from lib.tools.notifications import PostNotification
from lib.cells.colorCell import RFPopupColorPanel, RFColorCell
from lib.tools.misc import NSColorToRgba

import plistlib

# Our own branch of the defconAppKit GlyphView
from defconAppKitBranch.glyphView import GlyphView
from defconAppKit.windows.baseWindow import BaseWindowController

# Temp name for a key to save the extension's preferences
DEFAULTSKEY = "com.andyclymer.themeManager"

EXTENSIONBUNDLE = ExtensionBundle("ThemeManager")

# Preference keys and names for the theme settings
THEMEKEYS = [
    ("glyphViewOncurvePointsSize", "Oncurve Size", float),
    ("glyphViewOffCurvePointsSize", "Offcurve Size", float),
    ("glyphViewStrokeWidth", "Glyph Stroke Width", int),
    ("glyphViewSelectionStrokeWidth", "Selection Stroke Width", int),
    ("glyphViewHandlesStrokeWidth", "Handle stroke width", int),
    ("glyphViewBackgroundColor", "Background Color", tuple),
    ("glyphViewFillColor", "Fill Color", tuple),
    ("glyphViewPreviewFillColor", "Preview Fill Color", tuple),
    ("glyphViewPreviewBackgroundColor", "Preview Background Color", tuple),
    ("glyphViewAlternateFillColor", "Alternate Fill Color", tuple),
    ("glyphViewStrokeColor", "Stroke Color", tuple),
    ("glyphViewCornerPointsFill", "Corner Point Fill Color", tuple),
    ("glyphViewCornerPointsStroke", "Corner Point Stroke Color", tuple),
    ("glyphViewCurvePointsFill", "Curve Point Fill Color", tuple),
    ("glyphViewCurvePointsStroke", "Curve Point Stroke Color", tuple),
    ("glyphViewTangentPointsFill", "Tangent Fill Color", tuple),
    ("glyphViewTangentPointsStroke", "Tangent Stroke Color", tuple),
    ("glyphViewOffCurvePointsFill", "Offcurve Fill Color", tuple),
    ("glyphViewOffCurveCubicPointsStroke", "Offcurve Stroke Color (Cubic Beziers, PostScript)", tuple),
    ("glyphViewOffCurveQuadPointsStroke", "Offcurve Stroke Color (Quadratic Beziers, TrueType)", tuple),
    ("glyphViewSmoothPointStroke", "Smooth Point Color", tuple),
    ("glyphViewComponentFillColor", "Component Fill Color", tuple),
    ("glyphViewComponentStrokeColor", "Component Stroke Color", tuple),
    ("glyphViewComponentInfoColor", "Component Info Text Color", tuple),
    ("glyphViewImageInfoColor", "Image Info Text Color", tuple),
    ("glyphViewCubicHandlesStrokeColor", "Handle Stroke Color (Cubic Beziers, PostScript)", tuple),
    ("glyphViewQuadraticHandlesStrokeColor", "Handle Stroke Color (Quadratic Beziers, TrueType)", tuple),
    ("glyphViewStartPointsArrowColor", "Start Point Arrow Color for closed contour", tuple),
    ("glyphViewOpenStartPointsArrowColor", "Start Point Arrow Color for an open contour", tuple),
    ("glyphViewSelectionColor", "Selection Color", tuple),
    ("glyphViewSelectionMarqueColor", "Selection Marquee Color", tuple),
    ("glyphViewPointCoordinateColor", "Point Coordinate Color", tuple),
    ("glyphViewPointCoordinateBackgroundColor", "Point Coordinate Background Color", tuple),
    ("glyphViewLocalGuidesColor", "Local Guides Color", tuple),
    ("glyphViewGlobalGuidesColor", "Global Guides Color", tuple),
    ("glyphViewFamilyBluesColor", "Family Blues Color", tuple),
    ("glyphViewBluesColor", "Blues Color", tuple),
    ("glyphViewAnchorColor", "Anchor Color", tuple),
    ("glyphViewAnchorTextColor", "Anchor Text Color", tuple),
    ("glyphViewMarginColor", "Margins Background Color", tuple),
    ("glyphViewFontMetricsStrokeColor", "Vertical Metrics Color", tuple),
    ("glyphViewMetricsTitlesColor", "Vertical Metrics Titles Color", tuple),
    ("glyphViewGridColor", "Grid Color", tuple),
    ("glyphViewBitmapColor", "Bitmap Color", tuple),
    ("glyphViewOutlineErrorsColor", "Line Straightness Indicator Color", tuple),
    ("glyphViewMeasurementsTextColor", "Measurements Text Color", tuple),
    ("glyphViewMeasurementsForegroundColor", "Measurements Line Color", tuple),
    ("glyphViewMeasurementsBackgroundColor", "Measurements Secondary Line Color", tuple),
    ("glyphViewContourIndexColor", "Contour Index Text Color", tuple),
    ("glyphViewSegmentIndexColor", "Segment Index Text Color", tuple),
    ("glyphViewPointIndexColor", "Point Index Text Color", tuple),
    ("glyphViewEchoStrokeColor", "Echo Path Stroke Color", tuple)]

NONCOLORKEYS = [k for k in THEMEKEYS if not k[2] == tuple]
FALLBACKCOLOR = [.5, .5, .5, .5]

"""
Other theme preferences, for the future:

DebuggerBackgroundColor
DebuggerTextColor
PyDEBackgroundColor
PyDEHightLightColor
PyDETokenColors
    Comment
    Error
    Generic.Emph
    Generic.Heading
    Generic.Strong
    Generic.Subheading
    Keyword
    Keyword.Namespace
    Literal.Number
    Literal.Number.Float
    Literal.Number.Hex
    Literal.Number.Oct
    Literal.String
    Literal.String.Doc
    Name
    Name.Attribute
    Name.Builtin
    Name.Builtin.Pseudo
    Name.Class
    Name.Constant
    Name.Decorator
    Name.Exception
    Name.Function
    Name.Namespace
    Name.Tag
    Name.Variable
    Operator
    Operator.Word
    Punctuation
    Text

spaceCenterBackgroundColor
spaceCenterBeamStrokeColor
spaceCenterGlyphColor
spaceCenterHightLightColor
spaceCenterInputSelectionColor
spaceCenterMarginsColor
spaceCenterMetricsColor
spaceCenterReverseColor
"""

"""
todo:
@@@ come up with smarter duplication function
@@@ add licenses to all themes? @antonio
@@@ right now we have it so the file is invalid if the THEMEKEYS key is in themeData, but should
    we reverse that since new themes might be missing some keys. we would also need to
    re-write *def setEditingList()* so that it builds the list from the selected theme and not
    the THEMEKEYS.
"""

class ThemeManager(BaseWindowController):


    def __init__(self):

        self.debug = False

        # List of theme data dictionaries
        self.themes = []
        # On launch: go ahead and start loading themes
        self.readThemePrefs()
        self.loadDefaultThemes()
        # On launch: hold aside current preferences for "undo"
        self.backupTheme = {}
        self.makeBackupTheme()
        # Build the list of theme names
        self.themeNames = []

        # Placeholder for the name edit sheet
        self.nameSheet = None

        mid = 280
        # The Vanilla window
        self.w = vanilla.Window((300, 560), "Theme Manager")
        # Theme list
        self.w.themeList = vanilla.List((20, 20, mid-20, 165), self.themeNames,
            selectionCallback=self.listSelectionCallback,
            doubleClickCallback=self.listDoubleClickCallback,
            allowsMultipleSelection = False)
        # Editing list
        extrasHeight = len(NONCOLORKEYS) * 25 + 5
        colorCell = RFColorCell.alloc().init()
        columnDescriptions = [
            dict(title="Color", key="color", cell=colorCell, width=90),
            dict(title="Attribute", key="name")]
        self.w.editingList = vanilla.List((mid+20, 20, 480, -extrasHeight-20), [],
            columnDescriptions=columnDescriptions,
            allowsEmptySelection=False,
            allowsMultipleSelection=False,
            enableTypingSensitivity=True,
            rowHeight=20,
            allowsSorting=False,
            doubleClickCallback=self.colorDoubleClickCallback)
        # Extra values for editing
        self.w.editingExtras = vanilla.Group((mid+20, -extrasHeight-10, 480, -20))
        for i, extra in enumerate(NONCOLORKEYS):
            extraKey, extraName, extraType = extra
            extraEditor = vanilla.EditText((20, i*25, 50, 20), sizeStyle="small", callback=self.setThemeExtra)
            extraTitle = vanilla.TextBox((95, i*25, -20, 20), extraName)
            setattr(self.w.editingExtras, extraKey, extraEditor)
            setattr(self.w.editingExtras, extraKey + "-title", extraTitle)
        # Buttons
        y = 200
        self.w.buttonNewTheme = vanilla.SquareButton((20, y, 31, 25), "✚", callback=self.newThemeCallback) # ⌫✕✖︎✗✘★✚
        self.w.buttonNewTheme.getNSButton().setToolTip_("New Theme")
        self.w.buttonRemoveTheme = vanilla.SquareButton((50, y, 31, 25), "✘", callback=self.removeThemeCallback) #✘+
        self.w.buttonRemoveTheme.getNSButton().setToolTip_("Remove Theme")
        self.w.buttonDuplicateTheme = vanilla.SquareButton((80, y, 30, 25), "❏", callback=self.duplicateTheme)
        self.w.buttonDuplicateTheme.getNSButton().setToolTip_("Duplicate Theme")
        self.w.buttonEditTheme = vanilla.SquareButton((250, y, 30, 25), "✑", callback=self.editThemeCallback)
        self.w.buttonEditTheme.getNSButton().setToolTip_("Edit Theme")

        self.w.buttonImport = vanilla.SquareButton((120, y, 61, 25), "Import", callback=self.importThemeCallback)
        self.w.buttonExport = vanilla.SquareButton((180, y, 60, 25), "Export", callback=self.exportThemeCallback)

        self.w.buttonDuplicateTheme.enable(False)
        self.w.buttonRemoveTheme.enable(False)
        # Preview
        y += 40
        self.w.previewGlyphView = GlyphView((20, y, mid-20, 270))
        self.w.previewGlyphView.setTheme(self.backupTheme)
        self.w.previewGlyphView.setShowOffCurvePoints(True)
        self.w.previewGlyphView.setShowBlues(True)
        # Apply theme
        y += 280
        self.w.applyButton = vanilla.SquareButton((20, y, mid-60, 25), "Apply theme", callback=self.applyThemeCallback)
        self.w.applyButton.enable(False)
        self.w.buttonUndo = vanilla.SquareButton((mid-30, y, 30, 25), "↩︎", callback=self.undoThemeCallback) # ⤺⟲⎌
        self.w.buttonUndo.getNSButton().setToolTip_("Revert Theme")
        self.w.buttonUndo.enable(False)
        # Give the window a callback to call when the window closes
        self.w.bind("close", self.windowClosedCallback)

        # Open the window
        self.w.open()

        self.rebuildThemeList(setList=True)

        # Load the preview font
        previewFontPath = os.path.join(EXTENSIONBUNDLE.resourcesPath(), "GlyphPreview.ufo")
        previewFont = OpenFont(previewFontPath, showInterface=False)
        previewGlyph = previewFont["a"]
        self.w.previewGlyphView.set(previewGlyph.naked())


    # Helpers

    # =====

    def setEditingList(self, theme):
        # Collect the theme data for the selected theme and set it to the editingList
        if self.debug: print("setEditingList")
        listItems = []
        for nameKey, name, valueType in THEMEKEYS:
            if valueType == tuple:
                color = theme.get(nameKey, FALLBACKCOLOR)
                listItem = {
                    'color': NSColor.colorWithCalibratedRed_green_blue_alpha_(*color),
                    'name': name,
                    'nameKey': nameKey}
                listItems.append(listItem)
            else:
                value = theme[nameKey]
                extraEditor = getattr(self.w.editingExtras, nameKey)
                extraEditor.set(value)
        self.w.editingList.set(listItems)


    def getSelectedColorItem(self):
        # Get the selected item from the editingList
        items = self.w.editingList.get()
        if len(items):
            i = self.w.editingList.getSelection()[0]
            return items[i]


    def getSelectedThemeIdx(self):
        # Return the index of the selected theme, or None if there's no selection
        selection = self.w.themeList.getSelection()
        if selection:
            # If there is a selection, it will be returned as a list even if there's one item.
            # Take the first item only
            selectedIdx = selection[0]
            return selectedIdx
        else: return None


    # Theme editing callbacks

    def setColor_(self, sender):
        item = self.getSelectedColorItem()
        item['color'] = sender.color()
        selectedIdx = self.getSelectedThemeIdx()
        if not selectedIdx == None:
            theme = self.themes[selectedIdx]
            nameKey = (item['nameKey'])
            theme[nameKey] = NSColorToRgba(item['color'])
            if self.debug: print(theme[nameKey])
            self.w.previewGlyphView.setTheme(theme)


    def colorDoubleClickCallback(self, sender):
        item = self.getSelectedColorItem()
        # Doesnt allow defaults to be edited
        selectedIdx = self.getSelectedThemeIdx()
        if not selectedIdx == None:
            theme = self.themes[selectedIdx]
            if theme["themeType"] != "Default":
                self._popupColorPanel = RFPopupColorPanel(self.setColor_, item['color'], alpha=True)
            else:
                self.showMessage("Sorry!","You can't edit the default themes.\nIf you'd like to make changes to this theme,\nyou can duplicate '❏' it and edit that theme.") #🤷‍♂️


    def setThemeExtra(self, sender):
        selectedIdx = self.getSelectedThemeIdx()
        if not selectedIdx == None:
            theme = self.themes[selectedIdx]
            for extra in NONCOLORKEYS:
                extraKey, extraName, extraType = extra
                extraEditor = getattr(self.w.editingExtras, extraKey)
                extraValue = extraEditor.get()
                try:
                    extraValue = extraType(extraValue)
                    theme[extraKey] = extraValue
                except: pass
        # Update
        self.listSelectionCallback(None)


    # Interface Callbacks

    def windowClosedCallback(self, sender):
        if self.debug: print("windowClosedCallback")
        # The window is closing, save the themes into the extension preferenes using setExtensionDefault()
        # First, only keep the user defined themes, don't need to save the default themes
        themesToSave = []
        for theme in self.themes:
            if theme["themeType"] == "User":
                themesToSave += [theme]
        setExtensionDefault(DEFAULTSKEY, themesToSave)


    def undoThemeCallback(self, sender):
        if self.debug: print("undoThemeCallback")
        # Apply the backed up theme
        self._applyTheme(self.backupTheme)


    def importThemeCallback(self, sender):
        if self.debug: print("importThemeCallback")
        # Callback from the "Import" button
        # Pop open an "Open" dialog to get a file path, then call readThemePlist()
        path = GetFile(message="Import Theme", fileTypes=["roboFontTheme"])
        # If they did choose a path, save it.
        # If they clicked cancel, there would be no path.
        if path:
            with open(path, "rb") as themeFile:
                themeData = plistlib.load(themeFile)
            # Validate the themeData
            valid = True
            for key, name, valueType in THEMEKEYS:
                if not key in themeData:
                    valid = False
            if valid:
                self.themes += [themeData]
                self.rebuildThemeList()
            else:
                NSBeep()
                self.showMessage("Sorry!", "This is an invalid theme file.")


    def exportThemeCallback(self, sender):
        if self.debug: print("exportThemeCallback")
        # Callback from the "Export" button
        # Pop open a "Save" dialog to get a file path, then call writeThemePlist()
        selectedIdx = self.getSelectedThemeIdx()
        if not selectedIdx == None:
            # Fetch the theme
            theme = self.themes[selectedIdx]
            # Format a filename to save this theme as
            name = theme["themeName"]
            fileName = "%s.roboFontTheme" % name
            # Open the PutFile window to see if the user can locate a path to save the file
            path = PutFile(fileName=fileName)
            # If they did choose a path, save it.
            # If they clicked cancel, there would be no path.
            if path:
                # Make a copy of the theme, fixing the item types (the plist has problems saving otherwise)
                themeCopy = {}
                for key, name, valueType in THEMEKEYS:
                    k = str(key)
                    if valueType == tuple:
                        v = theme.get(key, FALLBACKCOLOR)
                    else:
                        v = valueType(theme[key])
                    themeCopy[k] = v
                themeCopy["themeName"] = str(theme["themeName"])
                themeCopy["themeType"] = "User"
                with open(path, "wb") as themeFile:
                    plistlib.dump(themeCopy, themeFile)

    def applyThemeCallback(self, sender):
        if self.debug: print("applyThemeCallback")
        # Callback from the "Apply Theme" button
        # Use setDefault() to set the value for each of the preferences keys
        selectedIdx = self.getSelectedThemeIdx()
        if not selectedIdx == None:
            # Fetch the theme
            theme = self.themes[selectedIdx]
            self._applyTheme(theme)
        self.w.buttonUndo.enable(True)


    def _applyTheme(self, theme):
        # Do the actual applying of the theme
        for key, val in theme.items():
            setDefault(key, val)
        PostNotification("doodle.preferencesChanged")

    def removeThemeCallback(self, sender):
        if self.debug: print("removeThemeCallback")
        # Callback from the "Remove" button
        # Remove this theme from the self.themes dictionary and update the vanilla list to no longer show it
        selectedIdx = self.getSelectedThemeIdx()
        if not selectedIdx == None:
            theme = self.themes[selectedIdx]
            if theme["themeType"] == "User":
                del(self.themes[selectedIdx])
                self.rebuildThemeList()


    def newThemeCallback(self, sender):
        if self.debug: print("newThemeCallback")
        # Callback from the "New" button
        # Read all of the current preferences into a new theme dictionary and update the Vanilla list
        theme = {}
        for key, name, dataType in THEMEKEYS:
            data = getDefault(key)
            data = dataType(data)
            # Save the data in the theme
            theme[key] = data
        # Give the theme a default name
        new = []
        name = "★ New Theme"
        for themes in self.themeNames:
            if name in themes:
                new.append(themes)
        length = len(new) + 1
        if name in self.themeNames:
            newName = name.replace("★ ", "")
            themeName = newName + " (%s)" % length
            theme["themeName"] = themeName
            theme["themeType"] = "User" # User or Default
        else:
            theme["themeName"] = "New Theme"
            theme["themeType"] = "User" # User or Default
        self.themes += [theme]
        self.rebuildThemeList()
        self.editName((len(self.themes) - 1), theme["themeName"])

    def duplicateTheme(self, sender):
        if self.debug: print("duplicateTheme")
        selectedIdx = self.getSelectedThemeIdx()
        if not selectedIdx == None:
            theme = self.themes[selectedIdx]
            dupeTheme = theme.copy()
            name = theme["themeName"]
            if name in self.themeNames:
                i = 2
                while "★ " + name + " (%s)" % i in self.themeNames:
                    i += 1
                name = name + " (%s)" % i
            dupeTheme["themeName"] = name
            dupeTheme["themeType"] = "User"
        self.themes += [dupeTheme]
        self.rebuildThemeList()


    def listSelectionCallback(self, sender):
        if self.debug: print("listSelectionCallback")
        # Callback when the selection in the Vanlla List changed
        # Figure out which item was selected (it can be more than one)
        selectedIdx = self.getSelectedThemeIdx()
        # The selection is a list of indices, because more than one thing could be selected
        # Just call the updatePrewview function and it will handle the rest
        self.updatePreview(selectedIdx)


    def listDoubleClickCallback(self, sender):
        if self.debug: print("listDoubleClickCallback")
        # Callback when the list of themes is double-clicked
        # Pop open a sheet to rename the theme
        selectedIdx = self.getSelectedThemeIdx()
        if not selectedIdx == None:
            if self.debug: print(selectedIdx)
            theme = self.themes[selectedIdx]
            if theme["themeType"] == "User":
                self.editName(selectedIdx, theme["themeName"])


    def editThemeCallback(self, sender):
        # Open/close the theme editor
        winX, winY, width, height = self.w.getPosSize()
        if width == 300:
            newWidth = 800
        else: newWidth = 300
        self.w.setPosSize((winX, winY, newWidth, height))


    # Functions when the extension launches


    def readThemePrefs(self):
        if self.debug: print("readThemePrefs")
        # Use getExtensionDefault() to read out all of the saved themes
        savedThemes = getExtensionDefault(DEFAULTSKEY)
        if savedThemes:
            # Copy each theme into the self.themes dictionary
            for theme in savedThemes:
                self.themes += [theme]


    def loadDefaultThemes(self):
        if self.debug: print("loadDefaultThemes")
        # Use the readThemePlist() function to load all of the curated themes out of a folder that lives in this roboFontExt
        presetFolder = os.path.join(EXTENSIONBUNDLE.resourcesPath(), "presetThemes")
        for fileName in os.listdir(presetFolder):
            name, ext = os.path.splitext(fileName)
            if ext == ".roboFontTheme":
                plistPath = os.path.join(presetFolder, fileName)
                with open(plistPath, "rb") as themeFile:
                    themeData = plistlib.load(themeFile)
                # Make sure that it's flagged as a default theme
                themeData["themeType"] = "Default"
                self.themes += [themeData]


    def rebuildThemeList(self, setList=True):
        if self.debug: print("rebuildThemeList")
        # Rebuid the list in the interface, after loading/adding/deleting themes
        self.themeNames = []
        for theme in self.themes:
            themeName = theme["themeName"]
            if theme["themeType"] == "User":
                themeName = "★ " + themeName
            if theme["themeType"] == "Default":
                pass
            self.themeNames += [themeName]
        if setList:
            self.w.themeList.set(self.themeNames)
        self.w.themeList.setSelection([])


    def makeBackupTheme(self):
        if self.debug: print("makeBackupTheme")
        # Make a backup of the current user prefs
        self.backupTheme = {}
        for key, name, dataType in THEMEKEYS:
            data = getDefault(key)
            data = dataType(data)
            self.backupTheme[key] = data


    # Theme preview


    def updatePreview(self, selectedIdx):
        if self.debug: print("updatePreview")
        # Update the preview drawing to use the colors of the selected theme in the list
        # The selection is a list, because the way a vanilla list works sometimes is that more than one thing can be selected
        if not selectedIdx == None:
            # Something was selected
            # Update the UI to enable the export and apply button
            self.w.buttonExport.enable(True)
            self.w.applyButton.enable(True)
            self.w.buttonDuplicateTheme.enable(True)
            # Enable the "Remove" button only if this is a user defined theme
            theme = self.themes[selectedIdx]
            if theme["themeType"] == "User":
                self.w.buttonRemoveTheme.enable(True)
                for extra in NONCOLORKEYS:
                    extraKey, extraName, extraType = extra
                    extraEditor = getattr(self.w.editingExtras, extraKey)
                    extraEditor.enable(True)
            else:
                self.w.buttonRemoveTheme.enable(False)
                for extra in NONCOLORKEYS:
                    extraKey, extraName, extraType = extra
                    extraEditor = getattr(self.w.editingExtras, extraKey)
                    extraEditor.enable(False)
            # Using this index, get the theme name out of the self.themes list
            theme = self.themes[selectedIdx]
            self.w.previewGlyphView.setTheme(theme)
            self.setEditingList(theme)
            self.w.editingList.enable(True)
        else:
            # Nothing was selected, clear out the temp theme namer
            self.w.previewGlyphView.setTheme(self.backupTheme)
            # Update the UI to disable buttons that shouldn't be active when nothing is selected
            self.w.buttonExport.enable(False)
            self.w.applyButton.enable(False)
            self.w.buttonDuplicateTheme.enable(False)
            self.w.buttonRemoveTheme.enable(False)
            self.setEditingList(self.backupTheme)
            self.w.editingList.enable(False)
            for extra in NONCOLORKEYS:
                extraKey, extraName, extraType = extra
                extraEditor = getattr(self.w.editingExtras, extraKey)
                extraEditor.enable(False)


    # Edit name sheet


    def editName(self, index, name):
        # Make a new vanilla "sheet" with controls for editing the name of the theme
        self.nameSheet = vanilla.Sheet((200, 110), self.w)
        self.nameSheet.editingIndex = index
        self.nameSheet.nameTitle = vanilla.TextBox((10, 10, -10, 25), "Theme Name:")
        self.nameSheet.name = vanilla.EditText((10, 35, -10, 25), name)
        self.nameSheet.cancelButton = vanilla.Button((10, -35, 95, 25), "Cancel", callback=self.editSheetClose)
        self.nameSheet.okButton = vanilla.Button((115, -35, -10, 25), "OK", callback=self.editSheetOKCallback)
        self.nameSheet.open()


    def editSheetClose(self, sender):
        # Callback to close the sheet
        if self.nameSheet:
            self.nameSheet.close()
            self.nameSheet = None


    def editSheetOKCallback(self, sender):
        # Callback when clicking "OK" in the Edit Name sheet
        if self.nameSheet:
            themeIndex = self.nameSheet.editingIndex
            newName = self.nameSheet.name.get()
            self.themes[themeIndex]["themeName"] = newName
            self.rebuildThemeList()
        self.w.themeList.setSelection([themeIndex])
        self.editSheetClose(None)


OpenWindow(ThemeManager)
