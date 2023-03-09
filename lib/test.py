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
import ThemeManagerScripting
from ThemeManagerScripting import *
importlib.reload(ThemeManagerScripting)


PREVIEW_HEIGHT = 600
WINDOW_WITHOUT_EDITOR_WIDTH = 530
WINDOW_WITH_EDITOR_WIDTH = 1050

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


class ThemeManagerGlyphView(ezui.MerzView):

    def __init__(self, theme=None, mode=None, size=(300,300), glyph=None, **kwargs):
        super().__init__(**kwargs)

        if theme:
            if mode == "dark":
                suffix = ".dark"
            else:
                suffix = ""
            
            container = self.getMerzContainer()
            container.clearSublayers()
        
        
            self.backgroundLayer = container.appendRectangleSublayer(
                fillColor=None,
                strokeColor=None
            )
                        
            self.glyphLayer = container.appendPathSublayer(
                fillColor=tuple(theme[f"glyphViewAlternateFillColor{suffix}"]),
                strokeColor=tuple(theme[f"glyphViewStrokeColor{suffix}"]),
                strokeWidth=.5
            )
        
            self.bluesLayer = container.appendPathSublayer(
                fillColor=tuple(theme[f"glyphViewBluesColor{suffix}"]),
                strokeColor=None
            )
        
            self.handleLayer = container.appendPathSublayer(
                fillColor=None,
                strokeColor=None
            )
        
            self.linesLayer = container.appendPathSublayer(
                fillColor=None,
                strokeColor=None
            )
        
            self.ovalCurveLayer = container.appendPathSublayer(
                fillColor=None,
                strokeColor=None
            )
        
            self.compLayer = container.appendPathSublayer(
                fillColor=tuple(theme[f"glyphViewComponentFillColor{suffix}"]),
                strokeColor=tuple(theme[f"glyphViewComponentStrokeColor{suffix}"]),
                strokeWidth=.5
            )


            self.backgroundLayer.clearSublayers()
            self.glyphLayer.clearSublayers()
            self.bluesLayer.clearSublayers()
            self.handleLayer.clearSublayers()
            self.linesLayer.clearSublayers()
            self.ovalCurveLayer.clearSublayers()
            self.compLayer.clearSublayers()


            if glyph is not None:
                f = glyph.font
                viewWidth = size[0]
                viewHeight = size[1]
                verticalMetrics = [
                    f.info.descender,
                    f.info.xHeight,
                    f.info.capHeight,
                    f.info.ascender
                ]
                bottom = min(verticalMetrics)
                top = max(verticalMetrics)
                contentHeight = (top * .46) - bottom
                fitHeight = viewHeight * 0.8
                scale = fitHeight / contentHeight
                x = (viewWidth - (glyph.width * scale)) / 2
                y = (viewHeight - fitHeight) / 2
        
                container.addSublayerTransformation((scale, 0, 0, scale, 40,-80), name="scale&translate")
                                               
                self.backgroundLayer.appendRectangleSublayer(
                    position=(x,0),
                    size=(glyph.width,top),
                    fillColor=tuple(theme[f"glyphViewBackgroundColor{suffix}"]),
                    ) 
                self.backgroundLayer.appendRectangleSublayer(
                    position=(-100,0),
                    size=(glyph.width,top),
                    fillColor=tuple(theme[f"glyphViewMarginColor{suffix}"]),
                    )
                                
                self.glyphLayer.appendPathSublayer(
                    size=(glyph.width, contentHeight),
                    fillColor=tuple(theme[f"glyphViewAlternateFillColor{suffix}"]),
                    strokeColor=tuple(theme[f"glyphViewStrokeColor{suffix}"]),
                    strokeWidth=.5
                )

                if f.info.postscriptBlueValues:
                    blueValues = list(zip(*[iter(f.info.postscriptBlueValues)] * 2))[0]
                    self.drawBlues(blueValues, tuple(theme[f"glyphViewBluesColor{suffix}"]))

                self.drawMetrics(f.info.xHeight, tuple(theme[f"glyphViewFontMetricsStrokeColor{suffix}"]), .5)
                self.drawMetrics(f.info.capHeight, tuple(theme[f"glyphViewFontMetricsStrokeColor{suffix}"]), .5)
                self.drawMetrics(0, tuple(theme[f"glyphViewFontMetricsStrokeColor{suffix}"]), .5)

                for component in glyph.components:
                    #self.compLayer.appendPathSublayer()
                    compPath = f[component.baseGlyph].getRepresentation("merz.CGPath")
                    self.compLayer.setPath(compPath)

        
                glyphPath = glyph.getRepresentation("merz.CGPath")
                self.glyphLayer.setPath(glyphPath)
                with self.glyphLayer.sublayerGroup():
                    for contour in glyph.contours:
                        allContPoints = [p for p in contour.points]
                        for point in contour.points:
                        
                            if point.type != "offcurve":
                        
                                bPoint = RBPoint()
                                bPoint._setPoint(point)
                                bPoint.contour = contour
                     
                                bIn = (float(bPoint.bcpIn[0] + bPoint.anchor[0]), float(bPoint.bcpIn[1] + bPoint.anchor[1]))
                                bOut = (float(bPoint.bcpOut[0] + bPoint.anchor[0]), float(bPoint.bcpOut[1] + bPoint.anchor[1]))
                                self.drawHandle((bIn,bPoint.anchor),tuple(theme[f"glyphViewCubicHandlesStrokeColor{suffix}"]),.5)
                                self.drawHandle((bPoint.anchor,bOut),tuple(theme[f"glyphViewCubicHandlesStrokeColor{suffix}"]),.5)

                            if point.type == "offcurve":
                                self.drawPoint("oval", (point.x, point.y), theme["glyphViewOffCurvePointsSize"], tuple(theme[f"glyphViewOffCurvePointsFill{suffix}"]), tuple(theme[f"glyphViewOffCurveCubicPointsStroke{suffix}"]), .5)

                            elif point.type == "curve":
                                if allContPoints[point.index + 1].type == "line":
                                    if point.smooth:
                                        self.drawPoint("triangle", (point.x, point.y), theme["glyphViewOncurvePointsSize"], tuple(theme[f"glyphViewTangentPointsFill{suffix}"]), tuple(theme[f"glyphViewTangentPointsStroke{suffix}"]), .5)
                                    else:
                                        self.drawPoint("rectangle", (point.x, point.y), theme["glyphViewOncurvePointsSize"], tuple(theme[f"glyphViewCornerPointsFill{suffix}"]), tuple(theme[f"glyphViewCornerPointsStroke{suffix}"]), .5)
                                else:
                                    if point.smooth:
                                        strokeColor = tuple(theme[f"glyphViewSmoothPointStroke{suffix}"])
                                    else:
                                        strokeColor = tuple(theme[f"glyphViewCurvePointsStroke{suffix}"])
                                    self.drawPoint("oval", (point.x, point.y), theme[f"glyphViewOncurvePointsSize"]*1.2, tuple(theme[f"glyphViewCurvePointsFill{suffix}"]), strokeColor, .5)
                            
                            elif point.type == "line":
                                if point.smooth:
                                    self.drawPoint("triangle", (point.x, point.y), theme["glyphViewOncurvePointsSize"], tuple(theme[f"glyphViewTangentPointsFill{suffix}"]), tuple(theme[f"glyphViewTangentPointsStroke{suffix}"]), .5)
                                else:
                                    self.drawPoint("rectangle", (point.x, point.y), theme["glyphViewOncurvePointsSize"], tuple(theme[f"glyphViewCornerPointsFill{suffix}"]), tuple(theme[f"glyphViewCornerPointsStroke{suffix}"]), .5)
    
                    for anchor in glyph.anchors:
                        self.drawPoint("oval", (anchor.x, anchor.y), 3, (1,0,0,1), None, 0)


    def drawMetrics(self, location, lineStrokeColor, strokeWidth):
        self.linesLayer.appendLineSublayer(
           startPoint = (-1000,location),
           endPoint = (1000,location),
           strokeWidth = strokeWidth,
           strokeColor = lineStrokeColor
        )

    def drawHandle(self, location, handleStrokeColor, strokeWidth):
        start,end = location
        self.handleLayer.appendLineSublayer(
           startPoint = start,
           endPoint = end,
           strokeWidth = strokeWidth,
           strokeColor = handleStrokeColor
        )

    def drawPoint(self, shape, location, pointSize, pointFillColor, pointStrokeColor, strokeWidth):
        pointSize *= 2
        self.ovalCurveLayer.appendSymbolSublayer(
            position=location,
            imageSettings=dict(
                name=shape,
                size=(pointSize,pointSize),
                fillColor = pointFillColor,
                strokeColor = pointStrokeColor,
                strokeWidth = strokeWidth,
            )
        )
    
    def drawBlues(self, size, blueFillColor):
        width = 1000
        height = (size[1] - size[0])
        self.bluesLayer.appendSymbolSublayer(
            position=(0,size[0]),
            imageSettings=dict(
                name="rectangle",
                size=(width,height),
                fillColor = blueFillColor,
            )
        )
    
ezui.tools.classes.registerClass("ts", ThemeManagerGlyphView)




class Demo(ezui.WindowController):

    def build(self):
        content = """
        * ts @glyphView
        """
        descriptionData = dict(
            glyphView=dict(
                theme=getThemeData("Connor's New Theme"),
                mode="dark",
                glyph=CurrentGlyph()
            )
        )
        self.w = ezui.EZWindow(
            content=content,
            descriptionData=descriptionData,
            controller=self,
            size=(400, 400),
        )

    def started(self):
        self.w.open()
        
        
Demo()