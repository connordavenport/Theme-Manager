"""
Window showing info about the current glyph

This example shows a floating window that displays information
about the current glyph. The window knows when the user has
switched the current glyph and updates accordingly. The displayed
information is updated when the data within the current glyph
is changed.
"""

import vanilla
import merz
import ezui
from fontParts.fontshell import RBPoint
from fontParts.world import OpenFont
from ThemeManagerScripting import getThemeData as gtd
from mojo.subscriber import Subscriber, WindowController, registerCurrentGlyphSubscriber

class ThemeManagerGlyphView(ezui.MerzView):

    def __init__(self, theme=None, size=(100,100), glyph=None, **kwargs):
        super().__init__(**kwargs)
        self.glyph = glyph
        self.size = size
        self.theme = theme
        self.container = self.getMerzContainer()
        self.container.clearSublayers()

        
    def setTheme(self, theme, mode):
        
        if mode == "dark":
            suffix = ".dark"
        else:
            suffix = ""
            
        self.glyphViewOffCurvePointsSize        = theme["glyphViewOffCurvePointsSize"]
        self.glyphViewOnCurvePointsSize         = theme["glyphViewOnCurvePointsSize"]

        self.glyphViewAlternateFillColor        = tuple(theme[f"glyphViewAlternateFillColor{suffix}"])
        self.glyphViewStrokeColor               = tuple(theme[f"glyphViewStrokeColor{suffix}"])
        self.glyphViewBluesColor                = tuple(theme[f"glyphViewBluesColor{suffix}"])
        self.glyphViewComponentFillColor        = tuple(theme[f"glyphViewComponentFillColor{suffix}"])
        self.glyphViewComponentStrokeColor      = tuple(theme[f"glyphViewComponentStrokeColor{suffix}"])
        self.glyphViewBackgroundColor           = tuple(theme[f"glyphViewBackgroundColor{suffix}"])
        self.glyphViewMarginColor               = tuple(theme[f"glyphViewMarginColor{suffix}"])
        self.glyphViewFontMetricsStrokeColor    = tuple(theme[f"glyphViewFontMetricsStrokeColor{suffix}"])
        self.glyphViewCubicHandlesStrokeColor   = tuple(theme[f"glyphViewCubicHandlesStrokeColor{suffix}"])
        self.glyphViewOffCurvePointsFill        = tuple(theme[f"glyphViewOffCurvePointsFill{suffix}"])
        self.glyphViewOffCurveCubicPointsStroke = tuple(theme[f"glyphViewOffCurveCubicPointsStroke{suffix}"])
        self.glyphViewTangentPointsFill         = tuple(theme[f"glyphViewTangentPointsFill{suffix}"])
        self.glyphViewTangentPointsStroke       = tuple(theme[f"glyphViewTangentPointsStroke{suffix}"])
        self.glyphViewCornerPointsFill          = tuple(theme[f"glyphViewCornerPointsFill{suffix}"])
        self.glyphViewCornerPointsStroke        = tuple(theme[f"glyphViewCornerPointsStroke{suffix}"])
        self.glyphViewSmoothPointStroke         = tuple(theme[f"glyphViewSmoothPointStroke{suffix}"])
        self.glyphViewCurvePointsStroke         = tuple(theme[f"glyphViewCurvePointsStroke{suffix}"])
        self.glyphViewCurvePointsFill           = tuple(theme[f"glyphViewCurvePointsFill{suffix}"])


        self.backgroundLayer = self.container.appendRectangleSublayer(
            fillColor=self.glyphViewMarginColor,
            strokeColor=None
        )
        self.glyphLayer = self.container.appendPathSublayer(
            fillColor=self.glyphViewAlternateFillColor,
            strokeColor=self.glyphViewStrokeColor,
            strokeWidth=.5
        )
        self.bluesLayer = self.container.appendPathSublayer(
            fillColor=None,
            strokeColor=None
        )
        self.handleLayer = self.container.appendPathSublayer(
            fillColor=None,
            strokeColor=None
        )
        self.linesLayer = self.container.appendPathSublayer(
            fillColor=None,
            strokeColor=None
        )
        self.ovalCurveLayer = self.container.appendPathSublayer(
            fillColor=None,
            strokeColor=None
        )
        self.compLayer = self.container.appendPathSublayer(
            fillColor=self.glyphViewComponentFillColor,
            strokeColor=self.glyphViewComponentStrokeColor,
            strokeWidth=.5
        )
        
        self.backgroundLayer.clearSublayers()
        self.glyphLayer.clearSublayers()
        self.bluesLayer.clearSublayers()
        self.handleLayer.clearSublayers()
        self.linesLayer.clearSublayers()
        self.ovalCurveLayer.clearSublayers()
        self.compLayer.clearSublayers()        
        
        if theme:
            if self.glyph is not None:
                f = self.glyph.font
                viewWidth = self.size[0]
                viewHeight = self.size[1]
                verticalMetrics = [
                    f.info.descender,
                    f.info.xHeight,
                    f.info.capHeight,
                    f.info.ascender
                ]
                bottom = min(verticalMetrics)
                top = max(verticalMetrics)
                contentHeight = (top * .4) - bottom
                fitHeight = viewHeight * 0.8
                scale = fitHeight / contentHeight
                x = (viewWidth - (self.glyph.width * scale)) / 2
                y = (viewHeight - fitHeight) / 2
        
                self.container.addSublayerTransformation((scale, 0, 0, scale, 50,30), name="scale&translate")
                                               
                self.backgroundLayer.appendRectangleSublayer(
                    position=(x,-1000),
                    size=(self.glyph.width,2000),
                    fillColor=self.glyphViewBackgroundColor,
                    ) 
                self.backgroundLayer.appendRectangleSublayer(
                    position=(-1000,-1000),
                    size=(self.glyph.width+1000,2000),
                    fillColor=self.glyphViewMarginColor,
                    )
                                
                self.glyphLayer.appendPathSublayer(
                    size=(self.glyph.width, contentHeight),
                    fillColor=self.glyphViewAlternateFillColor,
                    strokeColor=self.glyphViewStrokeColor,
                    strokeWidth=.5
                )

                if f.info.postscriptBlueValues:
                    blueValues = list(zip(*[iter(f.info.postscriptBlueValues)] * 2))[0]
                    self.drawBlues(blueValues, self.glyphViewBluesColor)

                self.drawMetrics(f.info.xHeight, self.glyphViewFontMetricsStrokeColor, .5)
                self.drawMetrics(f.info.capHeight, self.glyphViewFontMetricsStrokeColor, .5)
                self.drawMetrics(0, self.glyphViewFontMetricsStrokeColor, .5)

                for component in self.glyph.components:
                    #self.compLayer.appendPathSublayer()
                    compPath = f[component.baseGlyph].getRepresentation("merz.CGPath")
                    self.compLayer.setPath(compPath)

        
                glyphPath = self.glyph.getRepresentation("merz.CGPath")
                self.glyphLayer.setPath(glyphPath)
                with self.glyphLayer.sublayerGroup():
                    for contour in self.glyph.contours:
                        allContPoints = [p for p in contour.points]
                        for point in contour.points:
                        
                            if point.type != "offcurve":
                        
                                bPoint = RBPoint()
                                bPoint._setPoint(point)
                                bPoint.contour = contour
                     
                                bIn = (float(bPoint.bcpIn[0] + bPoint.anchor[0]), float(bPoint.bcpIn[1] + bPoint.anchor[1]))
                                bOut = (float(bPoint.bcpOut[0] + bPoint.anchor[0]), float(bPoint.bcpOut[1] + bPoint.anchor[1]))
                                self.drawHandle((bIn,bPoint.anchor),self.glyphViewCubicHandlesStrokeColor,.5)
                                self.drawHandle((bPoint.anchor,bOut),self.glyphViewCubicHandlesStrokeColor,.5)

                            if point.type == "offcurve":
                                self.drawPoint("oval", (point.x, point.y), self.glyphViewOffCurvePointsSize, self.glyphViewOffCurvePointsFill, self.glyphViewOffCurveCubicPointsStroke, .5)

                            elif point.type == "curve":
                                if allContPoints[point.index + 1].type == "line":
                                    if point.smooth:
                                        self.drawPoint("triangle", (point.x, point.y), self.glyphViewOnCurvePointsSize, self.glyphViewTangentPointsFill, self.glyphViewTangentPointsStroke, .5)
                                    else:
                                        self.drawPoint("rectangle", (point.x, point.y), self.glyphViewOnCurvePointsSize, self.glyphViewCornerPointsFill, self.glyphViewCornerPointsStroke, .5)
                                else:
                                    if point.smooth:
                                        strokeColor = self.glyphViewSmoothPointStroke
                                    else:
                                        strokeColor = self.glyphViewCurvePointsStroke
                                    self.drawPoint("oval", (point.x, point.y), self.glyphViewOnCurvePointsSize*1.2, self.glyphViewCurvePointsFill, strokeColor, .5)
                            
                            elif point.type == "line":
                                if point.smooth:
                                    self.drawPoint("triangle", (point.x, point.y), self.glyphViewOnCurvePointsSize, self.glyphViewTangentPointsFill, self.glyphViewTangentPointsStroke, .5)
                                else:
                                    self.drawPoint("rectangle", (point.x, point.y), self.glyphViewOnCurvePointsSize, self.glyphViewCornerPointsFill, self.glyphViewCornerPointsStroke, .5)
    
                    for anchor in self.glyph.anchors:
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
    
ezui.tools.classes.registerClass("ThemeManagerGlyphView", ThemeManagerGlyphView)