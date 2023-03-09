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

    def __init__(self, theme=None, size=(100,100), mode=None, glyph=None, **kwargs):
        super().__init__(**kwargs)

        if theme:
            if mode == "dark":
                suffix = ".dark"
            else:
                suffix = ""
            
            self.container = self.getMerzContainer()
            self.container.clearSublayers()
        
        
            self.backgroundLayer = self.container.appendRectangleSublayer(
                fillColor=None,
                strokeColor=None
            )
                        
            self.glyphLayer = self.container.appendPathSublayer(
                fillColor=tuple(theme[f"glyphViewAlternateFillColor{suffix}"]),
                strokeColor=tuple(theme[f"glyphViewStrokeColor{suffix}"]),
                strokeWidth=.5
            )
        
            self.bluesLayer = self.container.appendPathSublayer(
                fillColor=tuple(theme[f"glyphViewBluesColor{suffix}"]),
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
        
                self.container.addSublayerTransformation((scale, 0, 0, scale, 40,-80), name="scale&translate")
                                               
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
                                        self.drawPoint("triangle", (point.x, point.y), theme["glyphViewOnCurvePointsSize"], tuple(theme[f"glyphViewTangentPointsFill{suffix}"]), tuple(theme[f"glyphViewTangentPointsStroke{suffix}"]), .5)
                                    else:
                                        self.drawPoint("rectangle", (point.x, point.y), theme["glyphViewOnCurvePointsSize"], tuple(theme[f"glyphViewCornerPointsFill{suffix}"]), tuple(theme[f"glyphViewCornerPointsStroke{suffix}"]), .5)
                                else:
                                    if point.smooth:
                                        strokeColor = tuple(theme[f"glyphViewSmoothPointStroke{suffix}"])
                                    else:
                                        strokeColor = tuple(theme[f"glyphViewCurvePointsStroke{suffix}"])
                                    self.drawPoint("oval", (point.x, point.y), theme[f"glyphViewOnCurvePointsSize"]*1.2, tuple(theme[f"glyphViewCurvePointsFill{suffix}"]), strokeColor, .5)
                            
                            elif point.type == "line":
                                if point.smooth:
                                    self.drawPoint("triangle", (point.x, point.y), theme["glyphViewOnCurvePointsSize"], tuple(theme[f"glyphViewTangentPointsFill{suffix}"]), tuple(theme[f"glyphViewTangentPointsStroke{suffix}"]), .5)
                                else:
                                    self.drawPoint("rectangle", (point.x, point.y), theme["glyphViewOnCurvePointsSize"], tuple(theme[f"glyphViewCornerPointsFill{suffix}"]), tuple(theme[f"glyphViewCornerPointsStroke{suffix}"]), .5)
    
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
    
ezui.tools.classes.registerClass("ThemeManagerGlyphView", ThemeManagerGlyphView)