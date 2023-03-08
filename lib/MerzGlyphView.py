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
from fontParts.fontshell import RBPoint
from fontParts.world import OpenFont

from mojo.subscriber import Subscriber, WindowController, registerCurrentGlyphSubscriber

class MerzGlyphView():

    def __init__(self, theme, size, glyph):
        
        self.previewGlyph = glyph
        
        self.theme = theme
        self.pointsView = merz.MerzView("auto", backgroundColor=(1,1,1,1))        
        
        
        self.view = self.pointsView
        self.container = self.view.getMerzContainer()
        self.container.clearSublayers()
        
        self.backgroundLayer = self.container.appendRectangleSublayer(
            fillColor=None,
            strokeColor=None
        )
                        
        self.glyphLayer = self.container.appendPathSublayer(
            fillColor=tuple(self.theme["glyphViewAlternateFillColor.dark"]),
            strokeColor=tuple(self.theme["glyphViewStrokeColor.dark"]),
            strokeWidth=.5
        )
        
        self.bluesLayer = self.container.appendPathSublayer(
            fillColor=tuple(self.theme["glyphViewBluesColor.dark"]),
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
            fillColor=tuple(self.theme["glyphViewComponentFillColor.dark"]),
            strokeColor=tuple(self.theme["glyphViewComponentStrokeColor.dark"]),
            strokeWidth=.5
        )


        self.backgroundLayer.clearSublayers()
        self.glyphLayer.clearSublayers()
        self.bluesLayer.clearSublayers()
        self.handleLayer.clearSublayers()
        self.linesLayer.clearSublayers()
        self.ovalCurveLayer.clearSublayers()
        self.compLayer.clearSublayers()

        f = glyph.font
        if glyph is not None:
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
                fillColor=tuple(self.theme["glyphViewBackgroundColor.dark"]),
                ) 
            self.backgroundLayer.appendRectangleSublayer(
                position=(-100,0),
                size=(glyph.width,top),
                fillColor=tuple(self.theme["glyphViewMarginColor.dark"]),
                )
                                
            self.glyphLayer.appendPathSublayer(
                size=(glyph.width, contentHeight),
                fillColor=tuple(self.theme["glyphViewAlternateFillColor.dark"]),
                strokeColor=tuple(self.theme["glyphViewStrokeColor.dark"]),
                strokeWidth=.5
            )


            if f.info.postscriptBlueValues:
                blueValues = list(zip(*[iter(f.info.postscriptBlueValues)] * 2))[0]
                self.drawBlues(blueValues, tuple(self.theme["glyphViewBluesColor.dark"]))

            self.drawMetrics(f.info.xHeight, tuple(self.theme["glyphViewFontMetricsStrokeColor.dark"]), .5)
            self.drawMetrics(f.info.capHeight, tuple(self.theme["glyphViewFontMetricsStrokeColor.dark"]), .5)
            self.drawMetrics(0, tuple(self.theme["glyphViewFontMetricsStrokeColor.dark"]), .5)

            
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
                            self.drawHandle((bIn,bPoint.anchor),tuple(self.theme["glyphViewCubicHandlesStrokeColor.dark"]),.5)
                            self.drawHandle((bPoint.anchor,bOut),tuple(self.theme["glyphViewCubicHandlesStrokeColor.dark"]),.5)

                        if point.type == "offcurve":
                            self.drawPoint("oval", (point.x, point.y), self.theme["glyphViewOffCurvePointsSize"], tuple(self.theme["glyphViewOffCurvePointsFill.dark"]), tuple(self.theme["glyphViewOffCurveCubicPointsStroke.dark"]), .5)

                        elif point.type == "curve":
                            if allContPoints[point.index + 1].type == "line":
                                if point.smooth:
                                    self.drawPoint("triangle", (point.x, point.y), self.theme["glyphViewOncurvePointsSize"], tuple(self.theme["glyphViewTangentPointsFill.dark"]), tuple(self.theme["glyphViewTangentPointsStroke.dark"]), .5)
                                else:
                                    self.drawPoint("rectangle", (point.x, point.y), self.theme["glyphViewOncurvePointsSize"], tuple(self.theme["glyphViewCornerPointsFill.dark"]), tuple(self.theme["glyphViewCornerPointsStroke.dark"]), .5)
                            else:
                                if point.smooth:
                                    strokeColor = tuple(self.theme["glyphViewSmoothPointStroke.dark"])
                                else:
                                    strokeColor = tuple(self.theme["glyphViewCurvePointsStroke.dark"])
                                self.drawPoint("oval", (point.x, point.y), self.theme["glyphViewOncurvePointsSize"]*1.2, tuple(self.theme["glyphViewCurvePointsFill.dark"]), strokeColor, .5)
                            
                        elif point.type == "line":
                            if point.smooth:
                                self.drawPoint("triangle", (point.x, point.y), self.theme["glyphViewOncurvePointsSize"], tuple(self.theme["glyphViewTangentPointsFill.dark"]), tuple(self.theme["glyphViewTangentPointsStroke.dark"]), .5)
                            else:
                                self.drawPoint("rectangle", (point.x, point.y), self.theme["glyphViewOncurvePointsSize"], tuple(self.theme["glyphViewCornerPointsFill.dark"]), tuple(self.theme["glyphViewCornerPointsStroke.dark"]), .5)
   
                            
                        
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
    

                            

