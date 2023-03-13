"""
A custom roboFont glyphView written in Merz
it works but its not perfect:)
"""

import vanilla
import merz
import ezui
import math
from fontParts.fontshell import RBPoint, RGlyph
from fontParts.world import OpenFont
import ThemeManagerScripting as themeScripter
from mojo.subscriber import Subscriber, WindowController, registerCurrentGlyphSubscriber
from  mojo.tools import IntersectGlyphWithLine

class ThemeManagerGlyphView(ezui.MerzView):

    def __init__(self, theme=None, size=(100,100), glyph=None, **kwargs):
        super().__init__(**kwargs)
        self.glyph = glyph
        self.size = size
        self.theme = theme
        self.container = self.getMerzContainer()
        self.container.clearSublayers()
        self.backgroundLayer = self.container.appendRectangleSublayer(
            fillColor=None,
            strokeColor=None
        )
        self.glyphLayer = self.container.appendPathSublayer(
            fillColor=None,
            strokeColor=None,
            strokeWidth=None
        )
        self.bluesLayer = self.container.appendPathSublayer(
            fillColor=None,
            strokeColor=None
        )
        self.handleLayer = self.container.appendPathSublayer(
            fillColor=None,
            strokeColor=None,
            strokeWidth=None
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
            fillColor=None,
            strokeColor=None,
            strokeWidth=.5
        )

        self.textLayer = self.container.appendTextLineSublayer(
           backgroundColor=None,
           text="",
           fillColor=None,
           horizontalAlignment="center"
        )


        
    def setTheme(self, theme, mode):
        if mode == "dark":
            suffix = ".dark"
        else:
            suffix = ""
            
        self.glyphViewOffCurvePointsSize          = theme["glyphViewOffCurvePointsSize"]
        self.glyphViewOnCurvePointsSize           = theme["glyphViewOnCurvePointsSize"]
        self.glyphViewStrokeWidth                 = theme["glyphViewStrokeWidth"]
#        self.glyphViewSelectionStrokeWidth        = theme["glyphViewSelectionStrokeWidth"]
        self.glyphViewHandlesStrokeWidth          = theme["glyphViewHandlesStrokeWidth"]

        self.glyphViewAlternateFillColor          = tuple(theme[f"glyphViewAlternateFillColor{suffix}"])
        self.glyphViewStrokeColor                 = tuple(theme[f"glyphViewStrokeColor{suffix}"])
        self.glyphViewBluesColor                  = tuple(theme[f"glyphViewBluesColor{suffix}"])
        self.glyphViewComponentFillColor          = tuple(theme[f"glyphViewComponentFillColor{suffix}"])
        self.glyphViewComponentStrokeColor        = tuple(theme[f"glyphViewComponentStrokeColor{suffix}"])
        self.glyphViewBackgroundColor             = tuple(theme[f"glyphViewBackgroundColor{suffix}"])
        self.glyphViewMarginColor                 = tuple(theme[f"glyphViewMarginColor{suffix}"])
        self.glyphViewFontMetricsStrokeColor      = tuple(theme[f"glyphViewFontMetricsStrokeColor{suffix}"])
        self.glyphViewCubicHandlesStrokeColor     = tuple(theme[f"glyphViewCubicHandlesStrokeColor{suffix}"])
        self.glyphViewOffCurvePointsFill          = tuple(theme[f"glyphViewOffCurvePointsFill{suffix}"])
        self.glyphViewOffCurveCubicPointsStroke   = tuple(theme[f"glyphViewOffCurveCubicPointsStroke{suffix}"])
        self.glyphViewTangentPointsFill           = tuple(theme[f"glyphViewTangentPointsFill{suffix}"])
        self.glyphViewTangentPointsStroke         = tuple(theme[f"glyphViewTangentPointsStroke{suffix}"])
        self.glyphViewCornerPointsFill            = tuple(theme[f"glyphViewCornerPointsFill{suffix}"])
        self.glyphViewCornerPointsStroke          = tuple(theme[f"glyphViewCornerPointsStroke{suffix}"])
        self.glyphViewSmoothPointStroke           = tuple(theme[f"glyphViewSmoothPointStroke{suffix}"])
        self.glyphViewCurvePointsStroke           = tuple(theme[f"glyphViewCurvePointsStroke{suffix}"])
        self.glyphViewCurvePointsFill             = tuple(theme[f"glyphViewCurvePointsFill{suffix}"])
        self.glyphViewMeasurementsForegroundColor = tuple(theme[f"glyphViewMeasurementsForegroundColor{suffix}"])
        self.glyphViewMeasurementsBackgroundColor = tuple(theme[f"glyphViewMeasurementsBackgroundColor{suffix}"])
        self.glyphViewMeasurementsTextColor       = tuple(theme[f"glyphViewMeasurementsTextColor{suffix}"])
        self.glyphViewAnchorColor                 = tuple(theme[f"glyphViewAnchorColor{suffix}"])
        self.glyphViewAnchorTextColor             = tuple(theme[f"glyphViewAnchorTextColor{suffix}"])

        
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
                
                contourGlyph = self.glyph.copy()
                contourGlyph.clearComponents()
                for contour in self.glyph:
                    contourGlyph.appendContour(contour)
                glyphPath = contourGlyph.getRepresentation("merz.CGPath")
                self.glyphLayer.setPath(glyphPath)
                self.glyphLayer.setStrokeColor(self.glyphViewStrokeColor)
                self.glyphLayer.setFillColor(self.glyphViewAlternateFillColor)
                self.glyphLayer.setStrokeWidth(self.glyphViewStrokeWidth/2)

                measurementLine = ((59,-19),(254,132))
                measurements = sorted(IntersectGlyphWithLine(self.glyph,measurementLine))
                self.drawHandle(measurementLine, self.glyphViewMeasurementsForegroundColor, .5)

                self.drawHandle((measurementLine[1], (measurementLine[0][0], measurementLine[1][1])), self.glyphViewMeasurementsBackgroundColor, .5)
                self.drawHandle((measurementLine[0], (measurementLine[0][0], measurementLine[1][1])), self.glyphViewMeasurementsBackgroundColor, .5)

                for instersect in measurements:
                    self.drawPoint("oval", instersect, self.glyphViewOnCurvePointsSize, self.glyphViewMeasurementsForegroundColor, None, None)

                self.drawPoint("oval", (measurementLine[0][0], measurements[0][1]), self.glyphViewOnCurvePointsSize * .8, self.glyphViewMeasurementsBackgroundColor, None, None)
                self.drawPoint("oval", (measurementLine[0][0], measurements[1][1]), self.glyphViewOnCurvePointsSize * .8, self.glyphViewMeasurementsBackgroundColor, None, None)

                self.drawPoint("oval", (measurements[1][0], measurementLine[1][1]), self.glyphViewOnCurvePointsSize * .8, self.glyphViewMeasurementsBackgroundColor, None, None)
                self.drawPoint("oval", (measurements[0][0], measurementLine[1][1]), self.glyphViewOnCurvePointsSize * .8, self.glyphViewMeasurementsBackgroundColor, None, None)

                loc = themeScripter._interpolate(measurementLine[0][0], measurementLine[1][0], .5) - 80,  themeScripter._interpolate(measurementLine[0][1], measurementLine[1][1], .5) - 20

                distance = round(math.sqrt((measurementLine[0][0]-measurementLine[1][0])**2 + (measurementLine[0][1]-measurementLine[1][1])**2), 2)
                self.drawCaption(loc, f"{distance}", self.glyphViewMeasurementsTextColor, "top", "center")

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
                                self.drawHandle((bIn,bPoint.anchor),self.glyphViewCubicHandlesStrokeColor,self.glyphViewHandlesStrokeWidth)
                                self.drawHandle((bPoint.anchor,bOut),self.glyphViewCubicHandlesStrokeColor,self.glyphViewHandlesStrokeWidth)

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
                        self.drawPoint("oval", (anchor.x, anchor.y), 3, self.glyphViewAnchorColor, None, 0)
                        self.drawCaption(((anchor.x-85, anchor.y)), anchor.name, self.glyphViewAnchorTextColor)
                        


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

    def drawCaption(self, location, text, color, vAlign=None, hAlign=None):
        if not vAlign:
            vAlign = "center"
        if not hAlign:
            hAlign = "center"

        self.textLayer.appendTextLineSublayer(
           position=location,
           pointSize=10,
           text=f"{text}",
           fillColor=color,
           horizontalAlignment=hAlign,
           verticalAlignment=vAlign,
        )
    
ezui.tools.classes.registerClass("ThemeManagerGlyphView", ThemeManagerGlyphView)