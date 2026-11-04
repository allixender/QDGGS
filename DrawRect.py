from qgis.gui import QgsRubberBand, QgsMapToolEmitPoint, QgsMapTool
from PyQt5 import QtGui
from qgis.core import QgsWkbTypes, QgsRectangle, QgsPointXY
from qgis.core import QgsProject, QgsCoordinateReferenceSystem, QgsCoordinateTransform


def extentToWgs84(rect, crs):
    # returns minx, maxx, miny, maxy (ogr envelope order)
    xform = QgsCoordinateTransform(crs, QgsCoordinateReferenceSystem("EPSG:4326"), QgsProject.instance())
    r = xform.transformBoundingBox(rect)
    return r.xMinimum(), r.xMaximum(), r.yMinimum(), r.yMaximum()


class RectangleMapTool(QgsMapToolEmitPoint):
    def __init__(self, canvas, dlg):
        self.canvas = canvas
        QgsMapToolEmitPoint.__init__(self, self.canvas)
        self.rubberBand = QgsRubberBand(self.canvas, QgsWkbTypes.PolygonGeometry)
        self.rubberBand.setColor(QtGui.QColor(0, 0, 255))
        self.rubberBand.setFillColor(QtGui.QColor(0, 0, 255, 50))
        self.rubberBand.setWidth(1)
        self.reset()
        self.dlg = dlg
    
    def reset(self):
        self.startPoint = self.endPoint = None
        self.isEmittingPoint = False
        self.rubberBand.reset(QgsWkbTypes.PolygonGeometry)
    
    def canvasPressEvent(self, e):
        self.startPoint = self.toMapCoordinates(e.pos())
        self.endPoint = self.startPoint
        self.isEmittingPoint = True
        self.showRect(self.startPoint, self.endPoint)

    def canvasReleaseEvent(self, e):
        self.isEmittingPoint = False
        r = self.rectangle()
        if r is not None:
            self.deactivate()
            self.reset()
            self.canvas.unsetMapTool(self)
            self.canvas.refresh()
            self.dlg.showNormal()
            
            """ ------------------ """
            minx, maxx, miny, maxy = extentToWgs84(r, QgsProject.instance().crs())
                    
            self.dlg.sb_extent_minx.setValue(minx)
            self.dlg.sb_extent_miny.setValue(miny)
            self.dlg.sb_extent_maxx.setValue(maxx)
            self.dlg.sb_extent_maxy.setValue(maxy)
            
            """ ------------------ """
            
    def canvasMoveEvent(self, e):
        if not self.isEmittingPoint:
            return
    
        self.endPoint = self.toMapCoordinates(e.pos())
        self.showRect(self.startPoint, self.endPoint)
    
    def showRect(self, startPoint, endPoint):
        self.rubberBand.reset(QgsWkbTypes.PolygonGeometry)
        if startPoint.x() == endPoint.x() or startPoint.y() == endPoint.y():
            return
      
        self.point1 = QgsPointXY(startPoint.x(), startPoint.y())
        self.point2 = QgsPointXY(startPoint.x(), endPoint.y())
        self.point3 = QgsPointXY(endPoint.x(), endPoint.y())
        self.point4 = QgsPointXY(endPoint.x(), startPoint.y())
      
        self.rubberBand.addPoint(self.point1, False)
        self.rubberBand.addPoint(self.point2, False)
        self.rubberBand.addPoint(self.point3, False)
        self.rubberBand.addPoint(self.point4, False)
        self.rubberBand.addPoint(self.point1, True)    # true to update canvas
        
        self.rubberBand.show()

    def rectangle(self):
        if self.startPoint is None or self.endPoint is None:
            return None
        elif (self.startPoint.x() == self.endPoint.x() or self.startPoint.y() == self.endPoint.y()):
            return None
        return QgsRectangle(self.startPoint, self.endPoint)
    
    def deactivate(self):
        QgsMapTool.deactivate(self)
        self.deactivated.emit()