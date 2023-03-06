import os
from copy import deepcopy
import plistlib
import AppKit
import ezui
from mojo.UI import getDefault, setDefault
from mojo.extensions import getExtensionDefault, setExtensionDefault, ExtensionBundle
from lib.tools.notifications import PostNotification

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
    ("glyphViewEchoStrokeColor", "Echo Path Stroke Color", tuple)
]
DARKTHEMEKEYS = [(f"{key}.dark",name,val) for (key,name,val) in THEMEKEYS if getDefault(f"{key}.dark")]
FALLBACKCOLOR = [.5, .5, .5, .5]

PREVIEW_HEIGHT = 600
WINDOW_WITHOUT_EDITOR_WIDTH = 530
WINDOW_WITH_EDITOR_WIDTH = 1050

# -------------
# Scripting API
# -------------

def loadUserDefinedThemes():
    userDefinedThemes = getExtensionDefault(DEFAULTSKEY)
    loaded = []
    if userDefinedThemes:
        for theme in userDefinedThemes:
            for nameKey, name, valueType in THEMEKEYS:
                if nameKey not in theme:
                    continue
                theme[nameKey] = valueType(theme[nameKey])
            loaded.append(theme)
    return loaded

def loadBuiltInThemes():
    presetFolder = os.path.join(
        EXTENSIONBUNDLE.resourcesPath(),
        "presetThemes"
    )
    loaded = []
    for fileName in os.listdir(presetFolder):
        name, ext = os.path.splitext(fileName)
        if ext == ".roboFontTheme":
            plistPath = os.path.join(presetFolder, fileName)
            with open(plistPath, "rb") as themeFile:
                theme = plistlib.load(themeFile)
                theme["themeType"] = "Default"
                loaded.append(theme)
    return loaded

def loadThemes():
    themes = loadUserDefinedThemes()
    themes += loadBuiltInThemes()
    return themes

def themeBlender(theme1, theme2, factor, save=False):
    # contributed by Erik van Blokland
    
    # gather all of the theme names
    allThemes = [theme["themeName"] for theme in loadBuiltInThemes]
    allThemes.extend([theme["themeName"] for theme in getExtensionDefault(DEFAULTSKEY)])
    newTheme = {}    
    if theme1 in allThemes and theme2 in allThemes:
        blendedName = f"A {factor*100:3.1f}% blend between \"{theme1['themeName']}\" and \"{theme2['themeName']}\""
        for name, value1 in theme1.items():
            if name == "themeName":
                newTheme[name] = blendedName
                continue
            elif name == 'themeType':
                newTheme[name] = value1
                continue
            value2 = theme2[name]
            if isinstance(value1, (int, float)) and isinstance(value2, (int, float)):
                newTheme[name] = interpolate(value1, value2, factor)
                continue
            if len(value1) == len(value2):
                r = []
                for i, v1 in enumerate(value1):
                    v2 = value2[i]
                    r.append(interpolate(v1, v2, factor))
                newTheme[name] = r
    if save:
        pastThemes = loadUserDefinedThemes()
        pastThemes.append(newTheme)
        saveThemes(pastThemes)
        
    return newTheme
    
def saveThemes(themes):
    themes = [
        theme for theme in themes
        if theme["themeType"] == "User"
    ]
    setExtensionDefault(DEFAULTSKEY, themes)

def applyTheme(themeOrThemeName):
    theme = None
    if isinstance(themeOrThemeName, str):
        themes = loadThemes()
        for t in themes:
            if t["themeName"] == themeOrThemeName:
                theme = t
                break
    else:
        theme = themeOrThemeName
    for key, val in theme.items():
        setDefault(key, val)
    PostNotification("doodle.preferencesChanged")


# -----------------
# Helpers
# -----------------

def interpolate(a, b, f ):
    return a+f*(b-a)

# -----------------
# Window Controller
# -----------------

identifierToStorageKey = dict(
    editorNameField="themeName",
    editorOnCurveSizeField="glyphViewOncurvePointsSize",
    editorOffCurveSizeField="glyphViewOffCurvePointsSize",
    editorGlyphStrokeWidthField="glyphViewStrokeWidth",
    editorSelectionStrokeWidthField="glyphViewSelectionStrokeWidth",
    editorHandleStrokeWidthField="glyphViewHandlesStrokeWidth",
)
storageKeyToIdentifier = {v:k for k, v in identifierToStorageKey.items()}

class ThemeManagerWindowController(ezui.WindowController):

    debug = True

    def build(self):
        content = """
        = HorizontalStack

        * VerticalStack @themeStack
        > |----------| @themeTable
        > | X | name |
        > |----------|
        > > ((( {plus} | {minus} | {multiply} ))) @themeTableItemButton
        > > ((( {square.and.arrow.down} | {square.and.arrow.up} ))) @themeFileButton

        > ----------

        > * HorizontalStack @themeApplyButtonStack
        >> (Apply) @themeApplyButton
        >> (Undo) @themeUndoApplyButton

        * MerzView @themePreview

        * VerticalStack @editorStack

        > !§ Name
        > -------
        > [__] @editorNameField

        > !§ Colors
        > ---------

        > |--------------| @editorColorsTable
        > | C | C | name |
        > |--------------|

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
                backgroundColor=(1, 0, 0 ,1)
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
                allowsEmptySelection=False
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
        # store a backup of the current settings
        self.backupTheme = self.getCurrentUserDefaultsAsTheme()
        # store references to the commonly needed items
        self.themeTable = self.w.getItem("themeTable")
        self.editorStack = self.w.getItem("editorStack")
        self.editorColorsTable = self.w.getItem("editorColorsTable")
        self.themePreview = self.w.getItem("themePreview")
        # build the preview
        self.buildPreview()
        # load the data
        self.loadThemes()
        # set default button states
        self.w.getItem("themeUndoApplyButton").enable(False)

    def started(self):
        self.w.open()

    def windowWillClose(self, sender):
        self.saveThemes()

    # User Defaults Load/Save
    # -----------------------

    def loadThemes(self):
        # user defined themes
        userDefinedThemes = loadUserDefinedThemes()
        userDefinedItems = self.wrapThemeTableItems(userDefinedThemes, themeType="User")
        # built-in themes
        builtInThemes = loadBuiltInThemes()
        builtInItems = self.wrapThemeTableItems(builtInThemes, themeType="Default")
        self.populateThemeTable(userDefinedItems, builtInItems)

    def saveThemes(self):
        userDefinedItems, builtInItems = self.getThemeTableItems()
        themes = [self.unwrapThemeTableItem(item) for item in userDefinedItems]
        saveThemes(themes)

    def getCurrentUserDefaultsAsTheme(self):
        theme = {}
        for key, name, dataType in THEMEKEYS + DARKTHEMEKEYS:
            data = getDefault(key)
            data = dataType(data)
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
        theme = deepcopy(item)
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
                break

    def themeTableSelectionCallback(self, sender):
        items = sender.getSelectedItems()
        if not items:
            raise NotImplementedError("There must be at least one item in themeTable.")
        item = items[0]
        if isinstance(item, ezui.TableGroupRow):
            return
        colorItems = []
        values = dict(
            editorNameField=item["themeName"]
        )
        for nameKey, name, valueType in THEMEKEYS:
            if valueType == tuple:
                color = item.get(nameKey, FALLBACKCOLOR)
                darkColor = item.get(nameKey + ".dark", color)
                colorItem = dict(
                    color=color,
                    darkColor=darkColor,
                    name=name,
                    nameKey=nameKey
                )
                colorItems.append(colorItem)
            else:
                identifier = storageKeyToIdentifier[nameKey]
                value = item[nameKey]
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

    # creation/destruction

    def themeTableItemButtonCallback(self, sender):
        request = sender.get()
        if request == 0:
            self.themeTableAddTheme()
        elif request == 1:
            self.themeTableRemoveTheme()
        elif request == 2:
            self.themeTableDuplicateTheme()
        else:
            raise NotImplementedError(f"Unknown themeTableItemButton value: {request}")

    def themeTableAddTheme(self):
        # Read all of the current preferences into a new theme dictionary
        theme = self.getCurrentUserDefaultsAsTheme()
        # Give the theme a default name
        theme["themeName"] = self.findNewThemeName()
        # Get the loaded items
        userDefinedItems, builtInItems = self.getThemeTableItems()
        item = self.wrapThemeTableItem(theme, themeType="User")
        userDefinedItems.append(item)
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
        del userDefinedItems[i]
        self.populateThemeTable(userDefinedItems, builtInItems)

    def themeTableDuplicateTheme(self):
        items = self.themeTable.getSelectedItems()
        item = items[0]
        theme = self.unwrapThemeTableItem(item)
        theme = deepcopy(theme)
        theme["themeName"] = self.findNewThemeName()
        item = self.wrapThemeTableItem(theme, themeType="User")
        userDefinedItems, builtInItems = self.getThemeTableItems()
        userDefinedItems.append(item)
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
        themeName = themeData.pop("themeName")
        themeData.pop("themeType")
        validated = dict(
            themeType="User"
        )
        invalidValueTypes = []
        for nameKey, name, valueType in THEMEKEYS + DARKTHEMEKEYS:
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
        for key, name, valueType in THEMEKEYS + DARKTHEMEKEYS:
            themeStorage[key] = valueType(theme[key])
        with open(path, "wb") as themeFile:
            plistlib.dump(themeStorage, themeFile)

    # apply/undo

    def themeApplyButtonCallback(self, sender):
        items = self.themeTable.getSelectedItems()
        if not items:
            return
        item = items[0]
        theme = self.unwrapThemeTableItem(item)
        applyTheme(theme)
        self.w.getItem("themeUndoApplyButton").enable(True)

    def themeUndoApplyButtonCallback(self, sender):
        applyTheme(self.backupTheme)

    # Preview
    # -------

    def buildPreview(self):
        # previewFontPath = os.path.join(EXTENSIONBUNDLE.resourcesPath(), "GlyphPreview.ufo")
        # self.previewFont = OpenFont(previewFontPath, showInterface=False)
        # self.previewGlyph = self.previewFont["a"]
        container = self.themePreview.getMerzContainer()
        self.previewLightModeContainer = container.appendBaseSublayer(
            position=("center", "top"),
            size=("width", PREVIEW_HEIGHT / 2),
            backgroundColor=(1, 1, 1, 1)
        )
        self.previewDarkModeContainer = container.appendBaseSublayer(
            position=("center", "bottom"),
            size=("width", PREVIEW_HEIGHT / 2),
            backgroundColor=(0, 0, 0, 1)
        )
        container.appendBaseSublayer(
            position=("center", "center"),
            size=("width", "height"),
            borderColor=(0.5, 0.5, 0.5, 1),
            borderWidth=1
        )

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

    def editorStackCallback(self, sender):
        self.storeEditorValues()
        self.themeTable.reloadData(self.themeTable.getSelectedIndexes())


if __name__ == "__main__":
    ThemeManagerWindowController()