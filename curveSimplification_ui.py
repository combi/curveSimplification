import random
import sys
import time
# import profiler

from PySide import QtGui,QtCore
# from collections import defaultdict
# from itertools import izip_longest
from functools import wraps

import curveSimplification as curveSimplification

# TODO(combi): pouvoir faire plusieurs simplifications (naive, Douglas-Peucker, visvalingam, etc...) par shape

# https://github.com/bootchk/freehandTool/blob/master/freehandApp.py
# https://www.codeproject.com/Articles/373463/Painting-on-a-Widget

def timeIt(func):
    @wraps(func)
    def func_decorated(*args, **kwargs):
        startTime = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time()-startTime
        print '[%s time] (%ss)' %(func.__name__, elapsed)
        return result

    return func_decorated


# @timeIt
# @profileIt
def callDouglasPeucker(qPoints, epsilon=0.01):
    result= None
    pointsTuples = [pnt.toTuple() for pnt in qPoints]
    simplified, dMax  = curveSimplification.douglasPeuckerTuples(pointsTuples, epsilon=epsilon)
    newPoints = [QtCore.QPointF(*p.data) for p in simplified]

    result = (newPoints, dMax)
    return result

def callVisvalingan(pointsList, epsilon=0.01):
    # result = pointsList  # DEBUGONLY
    result = None
    pointsList_ = [pnt.toTuple() for pnt in pointsList]
    simplified  = curveSimplification.visvalinganTuples(pointsList_, epsilon=epsilon)
    result      = [QtCore.QPointF(*p.data) for p in simplified]
    return result

class Colors():
    red           = QtGui.QColor(120,   0,   0)
    green         = QtGui.QColor(000, 120,   0)
    blue          = QtGui.QColor(100, 100, 220)
    orange        = QtGui.QColor(200, 100,   0)
    yellow        = QtGui.QColor(255, 255,   0)

    green_dim     = QtGui.QColor(050,  90,  50)
    orange_dim    = QtGui.QColor(100,  50,  50)
    blue_dim      = QtGui.QColor(50,  50, 110)
    yellow_dim    = QtGui.QColor(180, 180,   0)

    grey          = QtGui.QColor(100, 100, 100)
    darkGrey      = QtGui.QColor(050,  50,  50)
    darkerGrey    = QtGui.QColor(040,  40,  40)
    black         = QtGui.QColor(000,   0,   0)


def randomColor(alpha=255):

    return QtGui.QColor(random.randint(0,255), random.randint(0,255), random.randint(0,255), alpha)

def setBgCol(widget, color):
    palette = widget.palette()
    palette.setColor(widget.backgroundRole(), color)
    widget.setAutoFillBackground(True)

    widget.setPalette(palette)

class LayoutWidget(QtGui.QWidget):
    def __init__(self, mode='vertical', parent=None):
        super(LayoutWidget, self).__init__(parent=parent)
        if mode in ('vertical', 'horizontal'):
            self.layout = QtGui.QBoxLayout(QtGui.QBoxLayout.LeftToRight, parent=self)  # On est oblige de donner une direction a la creation du layout
            if mode == 'horizontal':
                self.layout.setDirection(QtGui.QBoxLayout.LeftToRight)
            elif mode =='vertical':
                self.layout.setDirection(QtGui.QBoxLayout.TopToBottom)
        elif mode == 'grid':
            self.layout = QtGui.QGridLayout(self)  # On est oblige de donner une direction a la creation du layout
        else:
            raise()

        self.setLayout(self.layout)
        self.layout.setContentsMargins(0, 0, 0, 0)

    def addWidget(self, *args, **kwargs):
        self.layout.addWidget(*args, **kwargs)

    def setmargins(self, left=0, top=0, right=0, bottom=0):
        self.layout.setContentsMargins(left, top, right, bottom)


class Point(object):
    def __init__(self, nX, nY):
        self.X = nX
        self.Y = nY


# Shape class; holds data on the drawing point
class Shape(object):
    def __init__(self, width=1, color=None, points=None, simplify=0.0):
        self.points   = points or []
        self.width    = width
        self.color    = color or QtGui.QColor(0,0,0)
        self.simplify = simplify
        self.maxDist  = 0


class Painter(QtGui.QWidget):

    def __init__(self, parent=None):
        super(Painter, self).__init__(parent=parent)

        self.currentShape         = None
        self.shapes               = list()
        self.shapesSimplified     = list()

        self.simplificationMethod    = None
        self.simplificationAmount    = 0.0
        # self.drawSimplified          = False

        self.painter          = QtGui.QPainter()
        self.brushWidth       = 1
        self.brushColor       = QtGui.QColor(0,0,0)

        initialShape = produceShape(shapeNum=2)
        self.shapes.append(initialShape)

    def mousePressEvent(self, event):
        # eventX = event.x()
        # eventY = event.y()
        # print 'pos = (%s,%s)' %(eventX, eventY)
        self.currentShape = Shape(width=self.brushWidth, color=self.brushColor)
        self.shapes.append(self.currentShape)

    def mouseMoveEvent(self, event):
        # Se declenche quand on deplace la souris ET qu'un bouton est enfonce
        eventX = event.x()
        eventY = event.y()
        self.currentShape.points.append(QtCore.QPointF(eventX, eventY))

        self.repaint()

    def mouseReleaseEvent(self, event):
        if not self.currentShape.points:
            self.shapes.pop()
            return
        self.simplifyCurves()
        # pointsList = [p.toTuple() for p in self.currentShape.points]
        # maxDist = mathLib.getMaxDistInPointsList(pointsList)
        # print 'maxDist=', maxDist
        # self.currentShape.maxDist = maxDist

    def setBrushColor(self, color):
        self.brushColor = color
        self.repaint()

    def setBrushWidth(self, width):
        self.brushWidth = width
        self.repaint()

    def debug(self):
        print '[painter.debug]'

    def onMethodChange(self, method):
        # print '[[onMethodChange]]'
        # print 'method=', method
        self.simplificationMethod = method
        self.simplifyCurves()

    def onAmountChanged(self, amount):
        self.simplificationAmount = amount
        self.simplifyCurves()

    def simplifyCurves(self):
        if not self.simplificationMethod:
            self.shapesSimplified = list()
        elif self.simplificationMethod == 1:
            self.simplifyByDouglasPeucker()
        elif self.simplificationMethod == 2:
            self.simplifyByVisvalingan()
        self.repaint()

    def simplifyByDouglasPeucker(self):
        self.shapesSimplified[:] = []
        for shape in self.shapes:
            shapeSimplified = Shape(color=Colors.yellow, width=1, simplify=self.simplificationAmount)
            pointsSimplified, dMax = callDouglasPeucker(shape.points, epsilon=self.simplificationAmount)
            shapeSimplified.points  = pointsSimplified
            shapeSimplified.maxDist = dMax
            self.shapesSimplified.append(shapeSimplified)


    def simplifyByVisvalingan(self):
        self.shapesSimplified[:] = []

        for shape in self.shapes:
            shapeSimplified = Shape(color=Colors.yellow, width=1, simplify=self.simplificationAmount)
            pointsSimplified = callVisvalingan(shape.points, self.simplificationAmount)
            shapeSimplified.points  = pointsSimplified

            self.shapesSimplified.append(shapeSimplified)

    def paintEvent(self, event):
        # print '[[paint event]]: self.simplificationMethod', self.simplificationMethod
        self.painter.begin(self)
        self.painter.setRenderHint(QtGui.QPainter.Antialiasing)
        if not self.simplificationMethod:
            self.drawOriginals()
        elif self.simplificationMethod == 1:
            # print 'Douglas Peucker'
            self.drawDouglasPeucker()
        elif self.simplificationMethod == 2:
            # print 'Visvalingan'
            self.drawVisvalingan()
        self.painter.end()

    def drawOriginals(self):
        for shape in self.shapes:
            self.painter.setPen(QtGui.QPen(shape.color, shape.width))
            self.painter.drawPolyline(shape.points)

    def drawPointsIds(self):
        # for shape in self.shapes:
        yellowPen = QtGui.QPen(Colors.yellow, 1)
        bluePen   = QtGui.QPen(Colors.blue, 1)

        shiftToLeft = QtCore.QPointF(-10, 0)
        shiftToRight = QtCore.QPointF(10, 0)
        for i, shape in enumerate(self.shapes):
            for j, pnt in enumerate(shape.points):
                self.painter.setPen(yellowPen)
                self.painter.drawText(pnt+shiftToLeft, str(j))
                if j and j<len(shape.points)-1:
                    self.painter.setPen(bluePen)
                    self.painter.drawText(pnt+shiftToRight, str(j-1))

    def drawTriangles(self):
        random.seed(12345)

        for shape in self.shapes:
            if not len(shape.points)>=3:
                continue
            for i in range(len(shape.points))[1:-1]:
                pntA = shape.points[i-1]
                pntB = shape.points[i]
                pntC = shape.points[i+1]
                polygon = QtGui.QPolygonF()
                polygon.append(pntA)
                polygon.append(pntB)
                polygon.append(pntC)

                brush = QtGui.QBrush(randomColor(alpha=125), QtCore.Qt.SolidPattern)
                pen   = QtGui.QPen()
                pen.setStyle(QtCore.Qt.NoPen)
                self.painter.setPen(pen)
                self.painter.setBrush(brush)
                self.painter.drawPolygon(polygon)

    def drawSimplified(self):
        for shapeSimplified in self.shapesSimplified:
            self.painter.setPen(QtGui.QPen(shapeSimplified.color, shapeSimplified.width))
            self.painter.drawPolyline(shapeSimplified.points)


    def drawDouglasPeucker(self):
        self.drawOriginals()
        self.drawSimplified()

        # Draw text infos
        textH = 15
        self.painter.setPen(QtGui.QPen(Colors.yellow, 1))
        for i, (shape, shapeSimplified) in enumerate(zip(self.shapes, self.shapesSimplified)):
            numPointsShape = len(shape.points)
            numPointsShapeSimplified = len(shapeSimplified.points)
            self.painter.drawText(0, i*textH, 800, textH, 0, 'shape %d: %d points simplified to %d points (simplification at %.2f%% for length %.2f)' %(i+1, numPointsShape, numPointsShapeSimplified, shapeSimplified.simplify, shapeSimplified.maxDist))

    def drawVisvalingan(self):
        self.drawTriangles()
        self.drawOriginals()
        self.drawPointsIds()
        # self.drawSmallestAreas()
        self.drawSimplified()

    def clearSlate(self):
        self.shapes = list()
        self.shapesSimplified = list()
        self.repaint()



class CurveSimplificationUI(QtGui.QWidget):

    colorChanged = QtCore.Signal(object)

    '''
    ------
    | |  |
    ------
    '''
    def __init__(self):
        super(CurveSimplificationUI, self).__init__()

        self.changeColour_Button  = QtGui.QPushButton('Change Color')
        self.clear_Button         = QtGui.QPushButton('Clear')
        self.thickness_Spinner    = QtGui.QSpinBox(parent=self)
        self.paintPanel           = Painter(parent=self)
        self.slider               = QtGui.QSlider(QtCore.Qt.Horizontal, parent=self)
        self.simplificationMethod = QtGui.QComboBox(parent=self)

        self.simplificationMethod.addItems(['None', 'Douglas-Peucker', 'Visvalingan'])

        self.slider.setTracking(False)

        self.slider.setMaximum(1000)
        self.slider.setSingleStep(1)

        self.Debug_Button = QtGui.QPushButton('Debug')

        leftColumnLWidget  = LayoutWidget(parent=self, mode='vertical')
        rightColumnLWidget = LayoutWidget(parent=self, mode='vertical')

        leftColumnLWidget.addWidget(self.changeColour_Button)
        leftColumnLWidget.addWidget(self.thickness_Spinner)
        leftColumnLWidget.layout.addStretch()
        leftColumnLWidget.addWidget(self.Debug_Button)
        leftColumnLWidget.layout.addStretch()
        leftColumnLWidget.addWidget(self.clear_Button)
        leftColumnLWidget.addWidget(self.simplificationMethod)

        rightColumnLWidget.addWidget(self.paintPanel)
        rightColumnLWidget.addWidget(self.slider)

        self.layout = QtGui.QHBoxLayout()
        self.layout.addWidget(leftColumnLWidget)
        self.layout.addWidget(rightColumnLWidget)
        self.setLayout(self.layout)

        self.establish_connections()
        self.thickness_Spinner.setValue(5)

        setBgCol(self.paintPanel, Colors.darkerGrey)

        self.setGeometry(100, 100, 1000, 800)


    def changeColour(self):
        col = QtGui.QColorDialog.getColor()
        if not col.isValid():
            col = QtGui.QColor(0,0,0)
        self.colorChanged.emit(col)


    def establish_connections(self):
        self.changeColour_Button.clicked.connect(self.changeColour)
        self.clear_Button.clicked.connect(self.paintPanel.clearSlate)
        self.thickness_Spinner.valueChanged.connect(self.paintPanel.setBrushWidth)
        self.colorChanged.connect(self.paintPanel.setBrushColor)
        self.Debug_Button.clicked.connect(self.debug)
        self.slider.sliderReleased.connect(self.onSliderRelease)
        self.slider.sliderMoved.connect(self.onSliderMoved)
        self.slider.valueChanged[int].connect(self.onValueChanged)
        self.simplificationMethod.currentIndexChanged[int].connect(self.onSimplificationMethodChanged)


    def debug(self):
        # self.paintPanel.drawSimplified = not self.paintPanel.drawSimplified
        self.paintPanel.debug()
        self.paintPanel.repaint()

    def onSliderRelease(self):
        pass
        # print 'onSliderRelease'

    def onSliderMoved(self):
        pass
    #     print 'onSliderMoved'

    def onValueChanged(self, value):
        # on traduit la valeur du slider en valeur qui va de 0.0 a 1.0
        valueNormalized = float(value)/float(self.slider.maximum())
        self.paintPanel.onAmountChanged(valueNormalized)

    def onSimplificationMethodChanged(self, method):
        self.paintPanel.onMethodChange(method)

def produceShape(shapeNum=1):
    points = []
    if shapeNum==1:
        points = [(100,100), (100,200), (200,100), (250,150), (400,120),
                  (410,150), (450,190), (500,200), (578,173), (680,206),
                  (759,194), (780,258), (755,346), (699,400), (758,447),
                  (810,456), (819,554), (770,599), (636, 608), (550, 708)]
    elif shapeNum == 2:
        points = [(253.0, 593.0), (253.0, 590.0), (254.0, 586.0), (255.0, 581.0),
                  (255.0, 574.0), (255.0, 557.0), (256.0, 541.0), (258.0, 522.0),
                  (260.0, 497.0), (263.0, 477.0), (276.0, 461.0), (285.0, 430.0),
                  # (302.0, 408.0), (322.0, 385.0), (344.0, 359.0), (362.0, 343.0),
                  # (382.0, 331.0), (398.0, 305.0), (422.0, 299.0), (442.0, 293.0),
                  # (458.0, 285.0), (470.0, 281.0), (490.0, 279.0), (500.0, 277.0),
                  # (518.0, 275.0), (526.0, 273.0), (542.0, 271.0), (547.0, 269.0),
                  # (566.0, 267.0), (575.0, 265.0), (585.0, 264.0), (601.0, 260.0),
                  # (620.0, 257.0), (634.0, 252.0), (651.0, 247.0), (664.0, 236.0),
                  # (679.0, 228.0), (695.0, 217.0), (709.0, 200.0), (725.0, 186.0),
                  # (737.0, 176.0), (743.0, 163.0), (753.0, 154.0), (757.0, 143.0),
                  # (761.0, 131.0), (762.0, 125.0), (764.0, 122.0),
                  ]
        mult = 3
        deltaX = points[0][0]*mult - points[0][0]
        deltaY = points[0][1]*mult - points[0][1]

        points = [((x*mult)-deltaX, (y*mult)-deltaY) for (x,y) in points]
        print 'points=', points
    shape = Shape(width=2)
    shape.points = [QtCore.QPointF(*p) for p in points]

    return shape


def main():
    ui=CurveSimplificationUI()
    return ui

if __name__=="__main__":
    # print(sys.version)
    # print(sys.path)

    app = QtGui.QApplication(sys.argv)
    ui = main()
    ui.show()

    sys.exit(app.exec_())


