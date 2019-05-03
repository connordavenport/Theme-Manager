from AppKit import NSColor, NSGraphicsContext, NSForegroundColorAttributeName, NSFont, NSFontAttributeName, \
    NSStrokeColorAttributeName, NSStrokeWidthAttributeName, NSShadowAttributeName, NSAffineTransform, \
    NSShadow, NSCompositeSourceOver, NSBezierPath, NSRectFillUsingOperation, NSAttributedString
import math

"""
Common glyph drawing functions for all views. Notes:
- all drawing is done in font units
- the scale argument is the factor to scale a glyph unit to a view unit
- the rect argument is the rect that the glyph is being drawn in
"""

"""
setLayer_drawingAttributes_(layerName, attributes)

showGlyphFill
showGlyphStroke
showGlyphOnCurvePoints
showGlyphStartPoints
showGlyphOffCurvePoints
showGlyphPointCoordinates
showGlyphAnchors
showGlyphImage
showGlyphMargins
showFontVerticalMetrics
showFontVerticalMetricsTitles
showFontPostscriptBlues
showFontPostscriptFamilyBlues
"""

# ------
# Colors
# ------

defaultColors = dict(

    # General
    # -------

    background=NSColor.whiteColor(),

    # Font
    # ----

    # vertical metrics
    fontVerticalMetrics=NSColor.colorWithCalibratedWhite_alpha_(.4, .5),

    fontPostscriptBlues=NSColor.colorWithCalibratedRed_green_blue_alpha_(.5, .7, 1, .3),
    fontPostscriptFamilyBlues=NSColor.colorWithCalibratedRed_green_blue_alpha_(1, 1, .5, .3),

    # Glyph
    # -----

    # margins
    glyphMarginsFill=NSColor.colorWithCalibratedWhite_alpha_(.5, .11),
    glyphMarginsStroke=NSColor.colorWithCalibratedWhite_alpha_(.7, .5),

    # contour fill
    glyphContourFill=NSColor.colorWithCalibratedRed_green_blue_alpha_(0, 0, 0, 1),

    # contour stroke
    glyphContourStroke=NSColor.colorWithCalibratedRed_green_blue_alpha_(0, 0, 0, 1),

    # component fill
    glyphComponentFill=NSColor.colorWithCalibratedRed_green_blue_alpha_(0, 0, 0, 1),

    # component stroke
    glyphComponentStroke=NSColor.colorWithCalibratedRed_green_blue_alpha_(0, 0, 0, 1),

    # points
    glyphPoints=NSColor.colorWithCalibratedRed_green_blue_alpha_(.6, .6, .6, 1),

    # anchors
    glyphAnchor=NSColor.colorWithCalibratedRed_green_blue_alpha_(1, .2, 0, 1),

)


def colorToNSColor(color):
    r, g, b, a = color
    return NSColor.colorWithCalibratedRed_green_blue_alpha_(r, g, b, a)


def getDefaultColor(name):
    return defaultColors[name]


# ----------
# Primitives
# ----------

def drawFilledRect(rect):
    context = NSGraphicsContext.currentContext()
    context.setShouldAntialias_(False)
    NSRectFillUsingOperation(rect, NSCompositeSourceOver)
    context.setShouldAntialias_(True)


def drawFilledOval(rect):
    path = NSBezierPath.bezierPath()
    path.appendBezierPathWithOvalInRect_(rect)
    path.fill()


def drawLine(xy1, xy2, lineWidth=1.0):
    x1, y1 = xy1
    x2, y2 = xy2
    turnOffAntiAliasing = False
    if x1 == x2 or y1 == y2:
        turnOffAntiAliasing = True
    if turnOffAntiAliasing:
        context = NSGraphicsContext.currentContext()
        context.setShouldAntialias_(False)
    path = NSBezierPath.bezierPath()
    path.moveToPoint_((x1, y1))
    path.lineToPoint_((x2, y2))
    if turnOffAntiAliasing and lineWidth == 1.0:
        lineWidth = 0.001
    path.setLineWidth_(lineWidth)
    path.stroke()
    if turnOffAntiAliasing:
        context.setShouldAntialias_(True)


def drawTextAtPoint(text, pt, scale, attributes={}, xAlign="left", yAlign="bottom", flipped=False):
    text = NSAttributedString.alloc().initWithString_attributes_(text, attributes)
    if xAlign != "left" or yAlign != "bottom":
        width, height = text.size()
        width *= scale
        height *= scale
        x, y = pt
        f = 1
        if flipped:
            f = -1
        if xAlign == "center":
            x -= width / 2
        elif xAlign == "right":
            x -= width
        if yAlign == "center":
            y -= height / 2 * f
        elif yAlign == "top":
            y -= height * f
        pt = (x, y)
    context = NSGraphicsContext.currentContext()
    context.saveGraphicsState()
    transform = NSAffineTransform.transform()
    transform.translateXBy_yBy_(pt[0], pt[1])
    if flipped:
        s = -scale
    else:
        s = scale
    transform.scaleXBy_yBy_(scale, s)
    transform.concat()
    text.drawAtPoint_((0, 0))
    context.restoreGraphicsState()


# ----
# Font
# ----

# Vertical Metrics

def drawFontVerticalMetrics(glyph, scale, rect, 
        drawLines=True, 
        drawText=True, 
        colorMetrics=None,
        colorMetricsTitles=None,
        backgroundColor=None, 
        flipped=False):
    font = glyph.font
    if font is None:
        return
    backgroundColor.set()
    # gather y positions
    toDraw = (
        ("Descender", "descender"),
        ("X Height", "xHeight"),
        ("Cap Height", "capHeight"),
        ("Ascender", "ascender")
    )
    toDraw = [(name, getattr(font.info, attr)) for name, attr in toDraw if getattr(font.info, attr) is not None]
    toDraw.append(("Baseline", 0))
    positions = {}
    for name, position in toDraw:
        if position not in positions:
            positions[position] = []
        positions[position].append(name)
    # create lines
    xMin = rect[0][0]
    xMax = xMin + rect[1][0]
    lines = []
    for y, names in sorted(positions.items()):
        names = ", ".join(names)
        lines.append(((xMin, y), (xMax, y), names))
    # draw lines
    if drawLines:
        colorMetrics.set()
        lineWidth = 0.5 * scale
        for pt1, pt2, names in lines:
            drawLine(pt1, pt2, lineWidth=lineWidth)
    # draw text
    if drawText:
        colorMetricsTitles.set()
        fontSize = 12
        attributes = {
            NSFontAttributeName: NSFont.systemFontOfSize_(fontSize),
            NSForegroundColorAttributeName: colorMetricsTitles
        }
        for pt1, pt2, names in lines:
            x, y = pt1
            x = glyph.width
            x += 15 * scale
            y += 10 * scale
            y -= (fontSize / 2.0) * scale
            drawTextAtPoint(names, (x, y), scale, attributes, flipped=flipped)


# Blues

def drawFontPostscriptBlues(glyph, scale, rect, color=None, backgroundColor=None):
    font = glyph.font
    if font is None:
        return
    blues = []
    if font.info.postscriptBlueValues:
        blues += font.info.postscriptBlueValues
    if font.info.postscriptOtherBlues:
        blues += font.info.postscriptOtherBlues
    if not blues:
        return
    if color is None:
        color = getDefaultColor("fontPostscriptBlues")
    color.set()
    _drawBlues(blues, rect)


def drawFontPostscriptFamilyBlues(glyph, scale, rect, color=None, backgroundColor=None):
    font = glyph.font
    if font is None:
        return
    blues = []
    if font.info.postscriptFamilyBlues:
        blues += font.info.postscriptFamilyBlues
    if font.info.postscriptFamilyOtherBlues:
        blues += font.info.postscriptFamilyOtherBlues
    if not blues:
        return
    if color is None:
        color = getDefaultColor("fontPostscriptFamilyBlues")
    color.set()
    _drawBlues(blues, rect)


def _drawBlues(blues, rect):
    yMins = [i for index, i in enumerate(blues) if not index % 2]
    yMaxs = [i for index, i in enumerate(blues) if index % 2]
    blues = zip(yMins, yMaxs)
    x = rect[0][0]
    w = rect[1][0]
    for yMin, yMax in blues:
        drawFilledRect(((x, yMin), (w, yMax - yMin)))


# Image

def drawGlyphImage(glyph, scale, rect, backgroundColor=None):
    if glyph.image.fileName is None:
        return
    context = NSGraphicsContext.currentContext()
    context.saveGraphicsState()
    aT = NSAffineTransform.transform()
    aT.setTransformStruct_(glyph.image.transformation)
    aT.concat()
    image = glyph.image.getRepresentation("defconAppKit.NSImage")
    image.drawAtPoint_fromRect_operation_fraction_(
        (0, 0), ((0, 0), image.size()), NSCompositeSourceOver, 1.0
    )
    context.restoreGraphicsState()


# Margins

def drawGlyphMargins(glyph, scale, rect, 
        drawFill=True, drawStroke=False, marginColor=None, flipped=False):
    fillColor = marginColor
    (x, y), (w, h) = rect
    if drawFill:
        left = ((x, y), (-x, h))
        right = ((glyph.width, y), (w - glyph.width, h))
        fillColor.set()
        for rect in (left, right):
            drawFilledRect(rect)



# Fill and Stroke

def drawGlyphFillAndStroke(glyph, scale, rect,
        drawFill=True, drawStroke=True,
        contourFillColor=None, contourStrokeColor=None, componentFillColor=None, componentStrokeColor=None, backgroundColor=None,
        contourStrokeWidth=1.0):
    # get the paths
    contourPath = glyph.getRepresentation("defconAppKit.NoComponentsNSBezierPath")
    componentPath = glyph.getRepresentation("defconAppKit.OnlyComponentsNSBezierPath")
    # fill
    if drawFill:
        # components
        componentFillColor.set()
        componentPath.fill()
        # contours
        contourFillColor.set()
        contourPath.fill()
    # stroke
    if drawStroke:
        # components
        componentPath.setLineWidth_(contourStrokeWidth * 0.5 * scale)
        componentStrokeColor.set()
        componentPath.stroke()
        # contours
        contourPath.setLineWidth_(contourStrokeWidth * 0.5 * scale)
        contourStrokeColor.set()
        contourPath.stroke()


# points

def drawGlyphPoints(glyph, scale, rect, 
            drawStartPoint=False,
            drawOnCurves=False, 
            drawOffCurves=False, 
            drawCoordinates=False,
            colorCornerPointsFill=None,
            colorCornerPointsStroke=None,
            colorTangentPointsFill=None,
            colorTangentPointsStroke=None,
            colorCurvePointsFill=None,
            colorCurvePointsStroke=None,
            colorOffCurvePointsFill=None,
            colorOffCurvePointsStroke=None,
            colorOffCurveQuadPointsStroke=None,
            colorSmoothPointStroke=None,
            colorStartPointsArrow=None,
            colorOpenStartPointsArrow=None,
            colorPointCoordinate=None,
            colorPointCoordinateBackground=None,
            colorHandlesStroke=None,
            colorHandlesQuadStroke=None,
            backgroundColor=None,
            pointSizeOnCurve=False,
            pointSizeOffCurve=False,
            flipped=False):
            
    # get the outline data
    outlineData = glyph.getRepresentation("defconAppKit.OutlineInformation")
    points = []
    # start point
    if drawStartPoint and outlineData["startPoints"]:
        startWidth = startHeight = 15 * scale
        startHalf = startWidth / 2.0
        path = NSBezierPath.bezierPath()
        for point, angle in outlineData["startPoints"]:
            x, y = point
            if angle is not None:
                path.moveToPoint_((x, y))
                path.appendBezierPathWithArcWithCenter_radius_startAngle_endAngle_clockwise_(
                    (x, y), startHalf, angle - 90, angle + 90, True)
                path.closePath()
            else:
                path.appendBezierPathWithOvalInRect_(((x - startHalf, y - startHalf), (startWidth, startHeight)))
        colorStartPointsArrow.set()
        path.fill()
    # off curve
    if drawOffCurves and outlineData["offCurvePoints"]:
        # lines
        colorHandlesStroke.set()
        for point1, point2 in outlineData["bezierHandles"]:
            drawLine(point1, point2)
        # points
        offWidth = pointSizeOffCurve * scale
        offHalf = offWidth / 2.0
        path = NSBezierPath.bezierPath()
        for point in outlineData["offCurvePoints"]:
            x, y = point["point"]
            points.append((x, y))
            x -= offHalf
            y -= offHalf
            path.appendBezierPathWithOvalInRect_(((x, y), (offWidth, offWidth)))
        path.setLineWidth_(2.0 * scale)
        colorOffCurvePointsStroke.set()
        path.stroke()
        #backgroundColor.set()
        #path.fill()
        colorOffCurvePointsFill.set()
        path.setLineWidth_(1.0 * scale)
        path.fill()
    # on curve
    if drawOnCurves and outlineData["onCurvePoints"]:
        width = pointSizeOnCurve * scale
        half = width / 2.0
        triOuter = width / math.sqrt(3)
        triInner = width * math.sqrt(3) / 6.0
        for point in outlineData["onCurvePoints"]:
            path = NSBezierPath.bezierPath()
            x, y = point["point"]
            points.append((x, y))
            if point["segmentType"] == "curve":
                if point["smooth"]:
                    path.appendBezierPathWithOvalInRect_(((x-half, y-half), (width, width)))
                    colorSmoothPointStroke.set()
                    path.setLineWidth_(2 * scale)
                    path.stroke()
                    colorCurvePointsFill.set()
                    path.fill()
                else:
                    path.appendBezierPathWithOvalInRect_(((x-half, y-half), (width, width)))
                    colorCurvePointsStroke.set()
                    path.setLineWidth_(2 * scale)
                    path.stroke()
                    colorCurvePointsFill.set()
                    path.fill()
            elif point["segmentType"] == "line":
                if point["smooth"]:
                    path.moveToPoint_((x-half, y-triInner))
                    path.lineToPoint_((x, y+triOuter))
                    path.lineToPoint_((x+half, y-triInner))
                    #path.lineToPoint_((x-half, y-third))
                    path.closePath()
                    #path.appendBezierPathWithRect_(((x-half, y-half), (width, width)))
                    colorTangentPointsStroke.set()
                    path.setLineWidth_(2 * scale)
                    path.stroke()
                    colorTangentPointsFill.set()
                    path.fill()
                else:
                    path.appendBezierPathWithRect_(((x-half, y-half), (width, width)))
                    colorCornerPointsStroke.set()
                    path.setLineWidth_(2 * scale)
                    path.stroke()
                    colorCornerPointsFill.set()
                    path.fill()
        # path.appendBezierPathWithOvalInRect_(((x, y), (smoothWidth, smoothWidth)))
        # path.appendBezierPathWithRect_(((x, y), (width, width)))
    # coordinates
    if drawCoordinates:
        fontSize = 9
        attributes = {
            NSFontAttributeName: NSFont.systemFontOfSize_(fontSize),
            NSForegroundColorAttributeName: colorPointCoordinate
        }
        for x, y in points:
            posX = x
            posY = y - 3
            x = round(x, 1)
            if int(x) == x:
                x = int(x)
            y = round(y, 1)
            if int(y) == y:
                y = int(y)
            text = "%d  %d" % (x, y)
            drawTextAtPoint(text, (posX, posY), scale, attributes=attributes, xAlign="center", yAlign="top", flipped=flipped)


# Anchors

def drawGlyphAnchors(glyph, scale, rect, drawAnchor=True, drawText=True, color=None, textColor=None, backgroundColor=None, flipped=False):
    if not glyph.anchors:
        return
    if color is None:
        color = getDefaultColor("glyphAnchor")
    fallbackColor = color
    if backgroundColor is None:
        backgroundColor = getDefaultColor("background")
    anchorSize = 5 * scale
    anchorHalfSize = anchorSize / 2
    for anchor in glyph.anchors:
        if anchor.color is not None:
            color = colorToNSColor(anchor.color)
        else:
            color = fallbackColor
        x = anchor.x
        y = anchor.y
        name = anchor.name
        context = NSGraphicsContext.currentContext()
        context.saveGraphicsState()
        #shadow = NSShadow.alloc().init()
        #shadow.setShadowColor_(backgroundColor)
        #shadow.setShadowOffset_((0, 0))
        #shadow.setShadowBlurRadius_(3)
        #shadow.set()
        if drawAnchor:
            r = ((x - anchorHalfSize, y - anchorHalfSize), (anchorSize, anchorSize))
            color.set()
            drawFilledOval(r)
        if drawText and name:
            attributes = {
                NSFontAttributeName: NSFont.boldSystemFontOfSize_(12),
                NSForegroundColorAttributeName: textColor,
            }
            y += 25 * scale
            drawTextAtPoint(name, (x, y), scale, attributes, xAlign="center", yAlign="top", flipped=flipped)
        context.restoreGraphicsState()