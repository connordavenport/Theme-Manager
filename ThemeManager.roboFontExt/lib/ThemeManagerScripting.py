'''
Make scripting API seperate file
Get glyph view working
'''

import os
import plistlib
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

def loadThemes(names=False):
    # get all themes, if names == True return only the names
    themes = loadUserDefinedThemes()
    themes += loadBuiltInThemes()
    if names:
        return [t["themeName"] for t in themes]
    else:
        return themes

def getThemeData(themeName):
    if themeName in loadThemes(True):
        for theme in loadThemes():
            if theme["themeName"] == themeName:
                return theme
    else:
        print(f"{themeName} does not exist...")

def themeBlender(theme1, theme2, factor, save=False):
    # contributed by Erik van Blokland
    
    allThemes = loadThemes(True)
    newTheme = {}    
    if theme1 in allThemes and theme2 in allThemes:
        theme1 = getThemeData(theme1)
        theme2 = getThemeData(theme2)
        blendedName = f"A {factor*100:3.1f}% blend between \"{theme1['themeName']}\" and \"{theme2['themeName']}\""
        for name, value1 in theme1.items():
            if name == "themeName":
                newTheme[name] = blendedName
                continue
            elif name == 'themeType':
                newTheme[name] = "User"
                continue
                
            if name not in theme2.keys():
                newTheme[name] = value1
            else:
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
    if theme:
        for key, val in theme.items():
            setDefault(key, val)
        PostNotification("doodle.preferencesChanged")
    else:
        print(f"{themeOrThemeName} does not exist...")
        

# -----------------
# Helpers
# -----------------

def interpolate(a, b, f ):
    return a+f*(b-a)

print("setting up module")
