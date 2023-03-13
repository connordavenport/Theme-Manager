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
from lib.tools.misc import NSColorToRgba
import ThemeManagerGlyphView
import ThemeManagerScripting as themeScripter
import WCAGContrastRatio as contrast
importlib.reload(themeScripter)
importlib.reload(contrast)

PREVIEW_FONT_PATH = os.path.join(themeScripter.EXTENSIONBUNDLE.resourcesPath(), "GlyphPreview.ufo")
PREVIEW_FONT = OpenFont(PREVIEW_FONT_PATH, showInterface=False)
PREVIEW_GLYPH = PREVIEW_FONT["a"]

PREVIEW_HEIGHT = 600
WINDOW_WITHOUT_EDITOR_WIDTH = 530
WINDOW_WITH_EDITOR_WIDTH = 1050

# -----------------
# Window Controller
# -----------------

identifierToStorageKey = dict(
    editorNameField="themeName",
    editorOnCurveSizeField="glyphViewOnCurvePointsSize",
    editorOffCurveSizeField="glyphViewOffCurvePointsSize",
    editorGlyphStrokeWidthField="glyphViewStrokeWidth",
    editorSelectionStrokeWidthField="glyphViewSelectionStrokeWidth",
    editorHandleStrokeWidthField="glyphViewHandlesStrokeWidth",
)
storageKeyToIdentifier = {v:k for k, v in identifierToStorageKey.items()}


class ThemeManagerWindowController(ezui.WindowController):

    debug = True

    def build(self):
        # A temporary fix for renamed keys and dark mode-less themes
        themeScripter.renameThemeTypos()
        themeScripter.addDarkMode2Themes()
        
        # self.themes = []
        # store a backup of the current settings
        self.backupTheme = self.getCurrentUserDefaultsAsTheme()
        self.s = 0

        if AppKit.NSApp().appearance() == AppKit.NSAppearance.appearanceNamed_(AppKit.NSAppearanceNameDarkAqua):
            self.mode = "dark"
            button = 1
        else:
            self.mode = "light"
            button = 0
            
        content = """
        = HorizontalStack

        * VerticalStack @themeStack
        > |----------| @themeTable
        > | X | name |
        > |----------|
        > > ((( {plus} | {minus} | {arrow.counterclockwise} ))) @themeTableItemButton
        > > ((( {square.and.arrow.down} | {square.and.arrow.up} ))) @themeFileButton

        > ----------

        > * HorizontalStack @themeApplyButtonStack
        >> (Apply) @themeApplyButton
        >> (Undo) @themeUndoApplyButton
        
        >> ( {sun.max} | {moon.fill} ) @modeButton

        * ThemeManagerGlyphView @themePreview


        * VerticalStack @editorStack

        > !§ Name
        > -------
        > [__] @editorNameField

        > !§ Colors
        > ---------

        > |--------------| @editorColorsTable
        > | C | C | name |
        > |--------------|
        > ({wand.and.stars}) @themeAutoDarkModeButton        

        > !§ Sizes
        > --------

        > * HorizontalStack @editorOnCurveSizeStack
        >> [__](÷) @editorOnCurveSizeField
        >> Oncurve Size

        > * HorizontalStack @editorOffCurveSizeStack
        >> [__](÷) @editorOffCurveSizeField
        >> Offcurve Size

        > * HorizontalStack @editorGlyphStrokeWidthStack
        >> [__](÷) @editorGlyphStrokeWidthField
        >> Glyph Stroke Width

        > * HorizontalStack @editorSelectionStrokeWidthStack
        >> [__](÷) @editorSelectionStrokeWidthField
        >> Selection Stroke Width

        > * HorizontalStack @editorHandleStrokeWidthStack
        >> [__](÷) @editorHandleStrokeWidthField
        >> Handle Stroke Width
        """
        
        numberFieldWidth = 50
        descriptionData = dict(
            themeStack=dict(
                width=200
            ),
            themeTable=dict(
                height="fill",
                columnDescriptions=[
                    dict(
                        identifier="themeImage",
                        cellDescription=dict(
                            cellType="Image"
                        ),
                        width=12
                    ),
                    dict(
                        identifier="themeName"
                    )
                ],
                allowsGroupRows=True,
                showColumnTitles=False,
                allowsMultipleSelection=False,
                allowsEmptySelection=False
            ),
            themeTableItemButton=dict(
                gravity="leading"
            ),
            themeFileButton=dict(
            ),
            themeApplyButton=dict(
            ),
            themeUndoApplyButton=dict(
            ),

            themePreview=dict(
                width=300,
                height=PREVIEW_HEIGHT,
                backgroundColor=(1, 1, 1 ,1),
                theme=self.backupTheme,
                size=(300,300),
                glyph=PREVIEW_GLYPH,
            ),

            modeButton=dict(
            ),
            editorStack=dict(
                width=500
            ),
            editorColorsTable=dict(
                height="fill",
                # height=300,
                columnDescriptions=[
                    dict(
                        identifier="color",
                        title="Light",
                        width=50,
                        editable=True,
                        cellDescription=dict(cellType="ColorWell")
                    ),
                    dict(
                        identifier="darkColor",
                        title="Dark",
                        width=50,
                        editable=True,
                        cellDescription=dict(cellType="ColorWell")
                    ),
                    dict(
                        identifier="name",
                        title="",
                        editable=False
                    )
                ],
                allowsGroupRows=True,
                showColumnTitles=True,
                allowsMultipleSelection=False,
                allowsEmptySelection=False,
            ),
            editorOnCurveSizeField=dict(
                width=numberFieldWidth
            ),
            editorOffCurveSizeField=dict(
                width=numberFieldWidth
            ),
            editorGlyphStrokeWidthField=dict(
                width=numberFieldWidth
            ),
            editorSelectionStrokeWidthField=dict(
                width=numberFieldWidth
            ),
            editorHandleStrokeWidthField=dict(
                width=numberFieldWidth
            )
        )
        self.w = ezui.EZWindow(
            content=content,
            descriptionData=descriptionData,
            controller=self,
            title="Theme Manager",
            size=(WINDOW_WITHOUT_EDITOR_WIDTH, "auto")
        )
        # store references to the commonly needed items
        self.themeTable = self.w.getItem("themeTable")
        self.editorStack = self.w.getItem("editorStack")
        self.editorColorsTable = self.w.getItem("editorColorsTable")
        self.themePreview = self.w.getItem("themePreview")
        # build the preview
        #self.buildPreview()
        
        #self.themePreview.setTheme(self.backupTheme, self.mode)
        
        # self.onCurveSize = self.w.getItem("editorOnCurveSizeField")
        # self.offCurveSize = self.w.getItem("editorOffCurveSizeField")
        # self.glyphStroke = self.w.getItem("editorGlyphStrokeWidthField")
        # self.selectionStroke = self.w.getItem("editorSelectionStrokeWidthField")
        # self.handleStroke = self.w.getItem("editorHandleStrokeWidthField")
        self.selectedTheme = self.backupTheme  
        # load the data
        self.loadThemes()
        # set default button states
        self.w.getItem("themeUndoApplyButton").enable(False)
        self.w.getItem("modeButton").enable(False)
        self.w.getItem("modeButton").set(button)

    def started(self):
        self.w.open()

    def windowWillClose(self, sender):
        self.saveThemes()

    # User Defaults Load/Save
    # -----------------------

    def loadThemes(self):
        # user defined themes
        userDefinedThemes = themeScripter.loadUserDefinedThemes()
        userDefinedItems = self.wrapThemeTableItems(userDefinedThemes, themeType="User")
        self.themeLengths = len(userDefinedItems)
        # built-in themes
        builtInThemes = themeScripter.loadBuiltInThemes()
        builtInItems = self.wrapThemeTableItems(builtInThemes, themeType="Default")
        self.populateThemeTable(userDefinedItems, builtInItems)

    def saveThemes(self, overrideThemes=None):
        userDefinedItems, builtInItems = self.getThemeTableItems()
        if overrideThemes:
            themes = overrideThemes
        else:
            themes = [self.unwrapThemeTableItem(item) for item in userDefinedItems]
        themeScripter.saveThemes(themes)

    def getCurrentUserDefaultsAsTheme(self):
        theme = {}
        for key, name, dataType in themeScripter.THEMEKEYS + themeScripter.DARKTHEMEKEYS:
            data = getDefault(key)
            convertedData = themeScripter._dataConverter(data, dataType)
            theme[key] = data
        return theme

    # Theme Table
    # -----------

    def getThemeTableItems(self):
        items = [
            item for item in self.themeTable.get()
            if not isinstance(item, ezui.TableGroupRow)
        ]
        userDefinedItems = []
        builtInItems = []
        for item in items:
            if item["themeType"] == "User":
                userDefinedItems.append(item)
            elif item["themeType"] == "Default":
                builtInItems.append(item)
        return (userDefinedItems, builtInItems)

    def wrapThemeTableItem(self, theme, themeType="User"):
        theme = dict(theme)
        theme["themeType"] = themeType
        if themeType == "User":
            themeImage = ezui.makeImage(
                symbolName="star.fill",
                template=True
            )
        else:
            themeImage = ezui.makeImage(
                symbolName="lock",
                template=True
            )
        theme["themeImage"] = themeImage
        return theme

    def wrapThemeTableItems(self, themes, themeType="User"):
        items = [
            self.wrapThemeTableItem(theme, themeType=themeType)
            for theme in themes
        ]
        return items

    def unwrapThemeTableItem(self, item):
        item = dict(item)
        del item["themeImage"]
        theme = copy(item)
        return theme

    def populateThemeTable(self, userDefinedItems, builtInItems, selection=None):
        items = (
              [ezui.TableGroupRow("Your Themes")]
            + userDefinedItems
            + [ezui.TableGroupRow("Built-In Themes")]
            + builtInItems
        )
        self.themeTable.set(items)
        if selection is not None:
            # select the specified theme
            name = selection["themeName"]
            for i, item in enumerate(items):
                if isinstance(item, ezui.TableGroupRow):
                    continue
                if item["themeName"] == name:
                    self.themeTable.setSelectedIndexes([i])
                    break
        else:
            # select the first theme
            for i, item in enumerate(items):
                if isinstance(item, ezui.TableGroupRow):
                    continue
                self.themeTable.setSelectedIndexes([i])
                self.themePreview.setTheme(item, self.mode)
                break

    def themeTableSelectionCallback(self, sender):
        self.w.getItem("modeButton").enable(True)

        items = sender.getSelectedItems()
        if not items:
            raise NotImplementedError("There must be at least one item in themeTable.")
        item = items[0]

        # if self.s >= 1 and self.themeLengths == len(self.getThemeTableItems()[0]):
        #     self.insertTheme(self.selectedTheme)

        self.themeLengths = len(self.getThemeTableItems()[0])
        self.selectedTheme = item
        if isinstance(item, ezui.TableGroupRow):
            return
        colorItems = []
        values = dict(
            editorNameField=item["themeName"]
        )
        for nameKey, name, valueType in themeScripter.THEMEKEYS:
            if valueType == tuple:
                color = item.get(nameKey, themeScripter.FALLBACKCOLOR)
                darkColor = item.get(nameKey + ".dark", color)
                colorItem = dict(
                    color=color,
                    darkColor=darkColor,
                    name=name,
                    nameKey=nameKey,
                )
                colorItems.append(colorItem)
            else:
                identifier = storageKeyToIdentifier[nameKey]
                value = item.get(nameKey, themeScripter.FALLBACKSIZE)
                values[identifier] = valueType(value)
        
        self.editorColorsTable.set(colorItems)
        self.editorStack.setItemValues(values)
        showEditor = item["themeType"] != "Default"
        x, y, w, h = self.w.getPosSize()
        if showEditor:
            self.w.setPosSize((x, y, WINDOW_WITH_EDITOR_WIDTH, h))
            self.editorStack.show(True)
        else:
            self.editorStack.show(False)
            self.w.setPosSize((x, y, WINDOW_WITHOUT_EDITOR_WIDTH, h))
        self.themePreview.setTheme(item,self.mode)

        self.s += 1
    # creation/destruction
    
    def insertTheme(self, themeData):
        userDefinedItems, builtInItems = self.getThemeTableItems()
        index = userDefinedItems.index([t for t in userDefinedItems if t["themeName"] == themeData["themeName"]][0])
        userDefinedItems[index] = themeData
        self.themeLengths = len(userDefinedItems)
        self.saveThemes(userDefinedItems)

    def themeTableItemButtonCallback(self, sender):
        request = sender.get()
        if request == 0:
            self.themeTableAddTheme()
        elif request == 1:
            self.themeTableRemoveTheme()
        elif request == 2:
            self.themeTableRefreshThemes()
        else:
            raise NotImplementedError(f"Unknown themeTableItemButton value: {request}")

    def themeTableAddTheme(self):
        # Read all of the current preferences into a new theme dictionary
        # if holding Shift on +, duplicate the current theme instead of using default
        if AppKit.NSEvent.modifierFlags() & AppKit.NSShiftKeyMask:
            theme = self.selectedTheme
        else:
            theme = self.getCurrentUserDefaultsAsTheme()
        # Give the theme a default name
        theme["themeName"] = self.findNewThemeName()
        # Get the loaded items
        userDefinedItems, builtInItems = self.getThemeTableItems()
        item = self.wrapThemeTableItem(theme, themeType="User")
        userDefinedItems.append(item)
        # self.themes.append(item)
        self.populateThemeTable(userDefinedItems, builtInItems, selection=item)

    def themeTableRemoveTheme(self):
        items = self.themeTable.getSelectedItems()
        item = items[0]
        if item["themeType"] == "Default":
            self.showMessage("You can’t delete built-in themes.")
            return
        themeName = item["themeName"]
        remove = None
        userDefinedItems, builtInItems = self.getThemeTableItems()
        for i, theme in enumerate(userDefinedItems):
            if theme["themeName"] == themeName:
                remove = i
        del userDefinedItems[remove]
        self.populateThemeTable(userDefinedItems, builtInItems)
        # self.themeLengths = len(userDefinedItems)

    def themeTableRefreshThemes(self):
        self.loadThemes()
        print("reload")

    def themeTableDuplicateTheme(self):
        items = self.themeTable.getSelectedItems()
        item = items[0]
        theme = self.unwrapThemeTableItem(item)
        theme = deepcopy(theme)
        theme["themeName"] = self.findNewThemeName()
        item = self.wrapThemeTableItem(theme, themeType="User")
        userDefinedItems, builtInItems = self.getThemeTableItems()
        userDefinedItems.append(item)
        # self.themes.append(item)
        self.populateThemeTable(userDefinedItems, builtInItems)

    def findNewThemeName(self):
        userDefinedItems, builtInItems = self.getThemeTableItems()
        names = [theme["themeName"] for theme in userDefinedItems]
        names += [theme["themeName"] for theme in builtInItems]
        counter = 0
        while 1:
            if counter == 0:
                name = "New Theme"
            else:
                name = f"New Theme {counter}"
            if name not in names:
                return name
            counter += 1

    # import/export

    def themeFileButtonCallback(self, sender):
        request = sender.get()
        if request == 0:
            self.importTheme()
        elif request == 1:
            self.exportTheme()
        else:
            raise NotImplementedError(f"Unknown themeFileButton value: {request}")

    def importTheme(self):
        self.showGetFile(
            self.importThemeDialogCallback,
            fileTypes=["roboFontTheme"],
            allowsMultipleSelection=False
        )

    def importThemeDialogCallback(self, paths):
        if not paths:
            return
        path = paths[0]
        with open(path, "rb") as themeFile:
            themeData = plistlib.load(themeFile)
        themeData = {(themeScripter.RENAMEMAP[key] if key in themeScripter.RENAMEMAP.keys() else key):val for key,val in themeData.items()}
        themeData = themeScripter.addDarkMode(themeData) 
        themeData = themeScripter.addMissing(themeData)
        themeName = themeData.pop("themeName")
        themeData.pop("themeType")
        validated = dict(
            themeType="User"
        )
        invalidValueTypes = []
        for nameKey, name, valueType in themeScripter.THEMEKEYS + themeScripter.DARKTHEMEKEYS:                
            if nameKey not in themeData:
                continue
            value = themeData.pop(nameKey)
            try:
                v = valueType(value)
                value = v
            except TypeError:
                pass
            if not isinstance(value, valueType):
                invalidValueTypes.append(nameKey)
                continue
            validated[nameKey] = value
        validityMessage = []
        if themeData:
            validityMessage.append(
                f"Unknown keys defined: {', '.join(themeData.keys())}"
            )
        if invalidValueTypes:
            validityMessage.append(
                f"Invalid value types for keys: {', '.join(invalidValueTypes)}"
            )
        userDefinedItems, builtInItems = self.getThemeTableItems()
        existingNames = [item["themeName"] for item in userDefinedItems + builtInItems]
        if themeName in existingNames:
            validityMessage.append(f"The name '{themeName}' is already used.")
            themeName = self.findNewThemeName()
        validated["themeName"] = themeName
        item = self.wrapThemeTableItem(validated)
        userDefinedItems.append(item)
        # self.themes.append(item)
        self.populateThemeTable(userDefinedItems, builtInItems, selection=item)
        if validityMessage:
            AppKit.NSBeep()
            validityMessage = [
                "This is an invalid theme file. As much of the data was imported as possible. These are the errors:"
            ] + validityMessage
            self.showMessage(
                "Sorry!",
                "\n".join(validityMessage)
            )

    def exportTheme(self):
        items = self.themeTable.getSelectedItems()
        if not items:
            return
        item = items[0]
        theme = self.unwrapThemeTableItem(item)
        fileName = f"{theme['themeName']}.roboFontTheme"
        self._exportingTheme = theme
        self.showPutFile(
            self.exportThemeDialogCallback,
            fileTypes=["roboFontTheme"],
            fileName=fileName
        )

    def exportThemeDialogCallback(self, path):
        theme = self._exportingTheme
        del self._exportingTheme
        if not path:
            return
        themeStorage = dict(
            themeName=theme["themeName"],
            themeType="User"
        )
        for key, name, valueType in themeScripter.THEMEKEYS + themeScripter.DARKTHEMEKEYS:
            data = theme.get(key)
            v = themeScripter._dataConverter(data, valueType)
            themeStorage[key] = v
        with open(path, "wb") as themeFile:
            plistlib.dump(themeStorage, themeFile)

    # apply/undo
    
    def themeAutoDarkModeButtonCallback(self, sender):
        background = contrast.getPercievedColor(contrast.invertColor(self.selectedTheme["glyphViewBackgroundColor"]), contrast.invertColor(self.selectedTheme["glyphViewMarginColor"]))
        for keyName, _, dataType in themeScripter.THEMEKEYS:
            self.selectedTheme[keyName] = dataType(self.selectedTheme[keyName])
        for keyName, _, dataType in themeScripter.DARKTHEMEKEYS:
            if dataType == tuple:
                if keyName in ["glyphViewBackgroundColor.dark", "glyphViewMarginColor.dark"]:
                    color = contrast.invertColor(self.selectedTheme[keyName])
                else:
                    c = self.selectedTheme[keyName.replace(".dark", "")]
                    ic = contrast.invertColor(c)
                    df = contrast.rgb(c,background)
                    at = contrast.rgb(ic,background)
                    if at > df:
                        color = ic
                    else:
                        color = c
                self.selectedTheme[keyName] = dataType([round(i,4) for i in color])
        self.themePreview.setTheme(self.selectedTheme,self.mode)

    def themeApplyButtonCallback(self, sender):
        items = self.themeTable.getSelectedItems()
        if not items:
            return
        item = items[0]
        theme = self.unwrapThemeTableItem(item)
        themeScripter.applyTheme(theme)
        self.w.getItem("themeUndoApplyButton").enable(True)
        
    def modeButtonCallback(self, sender):
        if sender.get() == 0:
            self.mode = "light"
        else:
            self.mode = "dark"
        self.themePreview.setTheme(self.selectedTheme,self.mode)

    def themeUndoApplyButtonCallback(self, sender):
        themeScripter.applyTheme(self.backupTheme)

    def editorColorsTableEditCallback(self, sender):
        for item in self.editorColorsTable.get():
            color = item["color"]
            darkColor = item["darkColor"]
            nameKey = item["nameKey"]
            self.selectedTheme[nameKey] = color
            self.selectedTheme[nameKey + ".dark"] = darkColor
        self.themePreview.setTheme(self.selectedTheme,self.mode)

    def editorOnCurveSizeFieldCallback(self,sender):
        nameKey = "glyphViewOnCurvePointsSize"
        self.selectedTheme[nameKey] = sender.get()
        self.themePreview.setTheme(self.selectedTheme,self.mode)
                
    def editorOffCurveSizeFieldCallback(self,sender):
        nameKey = "glyphViewOffCurvePointsSize"
        self.selectedTheme[nameKey] = sender.get()
        self.themePreview.setTheme(self.selectedTheme,self.mode)
        
    def editorGlyphStrokeWidthFieldCallback(self,sender):
        nameKey = "glyphViewStrokeWidth"
        self.selectedTheme[nameKey] = sender.get()
        self.themePreview.setTheme(self.selectedTheme,self.mode)
        
    def editorSelectionStrokeWidthFieldCallback(self,sender):
        nameKey = "glyphViewSelectionStrokeWidth"
        self.selectedTheme[nameKey] = sender.get()
        self.themePreview.setTheme(self.selectedTheme,self.mode)
        
    def editorHandleStrokeWidthFieldCallback(self,sender):
        nameKey = "glyphViewHandlesStrokeWidth"
        self.selectedTheme[nameKey] = sender.get()
        self.themePreview.setTheme(self.selectedTheme,self.mode)

    def editorNameFieldCallback(self, sender):
        nameKey = "themeName"
        self.selectedTheme[nameKey] = sender.get()
        
    # Editor
    # ------

    def storeEditorValues(self):
        selectedThemeItem = self.themeTable.getSelectedItems()[0]
        for identifier, nameKey in identifierToStorageKey.items():
            selectedThemeItem[nameKey] = self.editorStack.getItemValue(identifier)
        for item in self.editorColorsTable.get():
            color = item["color"]
            darkColor = item["darkColor"]
            nameKey = item["nameKey"]
            selectedThemeItem[nameKey] = color
            selectedThemeItem[nameKey + ".dark"] = darkColor

    def editorTableCallback(self, sender):
        self.storeEditorValues()

    def editorStackEditCallback(self, sender):
        self.storeEditorValues()
        self.themeTable.reloadData(self.themeTable.getSelectedIndexes())


if __name__ == "__main__":
    ThemeManagerWindowController()