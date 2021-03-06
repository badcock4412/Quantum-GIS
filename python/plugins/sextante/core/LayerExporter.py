# -*- coding: utf-8 -*-

"""
***************************************************************************
    LayerExporter.py
    ---------------------
    Date                 : August 2012
    Copyright            : (C) 2012 by Victor Olaya
    Email                : volayaf at gmail dot com
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

__author__ = 'Victor Olaya'
__date__ = 'August 2012'
__copyright__ = '(C) 2012, Victor Olaya'
# This will get replaced with a git SHA1 when you do a git archive
__revision__ = '$Format:%H$'

from sextante.core.SextanteConfig import SextanteConfig
from sextante.core.SextanteUtils import SextanteUtils
from qgis.core import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from sextante.gdal.GdalUtils import GdalUtils

class LayerExporter():

    '''This class provides method to export layers so they can be used by third party applications.
    These method are used by the GeoAlgorithm class and allow the developer to use transparently
    any layer that is loaded into QGIS, without having to worry about its origin'''

    @staticmethod
    def exportVectorLayer(layer):
        '''Takes a QgsVectorLayer and returns the filename to refer to it, which allows external
        apps which support only file-based layers to use it. It performs the necessary export
        in case the input layer is not in a standard format suitable for most applications, it is
        a remote one or db-based (non-file based) one, or if there is a selection and it should be
        used, exporting just the selected features.
        Currently, the output is restricted to shapefiles, so anything that is not in a shapefile
        will get exported.
        It also export to a new file if the original one contains non-ascii characters'''
        settings = QSettings()
        systemEncoding = settings.value( "/UI/encoding", "System" ).toString()
        output = SextanteUtils.getTempFilename("shp")
        provider = layer.dataProvider()
        useSelection = SextanteConfig.getSetting(SextanteConfig.USE_SELECTED)
        if useSelection and layer.selectedFeatureCount() != 0:
            writer = QgsVectorFileWriter(output, systemEncoding, layer.pendingFields(), provider.geometryType(), provider.crs())
            selection = layer.selectedFeatures()
            for feat in selection:
                writer.addFeature(feat)
            del writer
            return output
        else:
            isASCII=True
            try:
                unicode(layer.source()).decode("ascii")
            except UnicodeEncodeError:
                isASCII=False
            if (not unicode(layer.source()).endswith("shp") or not isASCII):
                writer = QgsVectorFileWriter( output, systemEncoding, layer.pendingFields(), provider.geometryType(), provider.crs() )
                for feat in layer.getFeatures():
                    writer.addFeature(feat)
                del writer
                return output
            else:
                return unicode(layer.source())



    @staticmethod
    def exportRasterLayer(layer):
        '''Takes a QgsRasterLayer and returns the filename to refer to it, which allows external
        apps which support only file-based layers to use it. It performs the necessary export
        in case the input layer is not in a standard format suitable for most applications, it is
        a remote one or db-based (non-file based) one
        Currently, the output is restricted to geotiff, but not all other formats are exported.
        Only those formats not supported by GDAL are exported, so it is assumed that the external
        app uses GDAL to read the layer'''
        exts = GdalUtils.getSupportedRasterExtensions()
        for ext in exts:
            if (unicode(layer.source()).endswith(ext)):
                return unicode(layer.source())

        #TODO:Do the conversion here
        return unicode(layer.source())

    
    @staticmethod
    def exportTable( table):
        '''Takes a QgsVectorLayer and returns the filename to refer to its attributes table, 
        which allows external apps which support only file-based layers to use it. 
        It performs the necessary export in case the input layer is not in a standard format 
        suitable for most applications, it isa remote one or db-based (non-file based) one
        Currently, the output is restricted to dbf.
        It also export to a new file if the original one contains non-ascii characters'''
        settings = QSettings()
        systemEncoding = settings.value( "/UI/encoding", "System" ).toString()
        output = SextanteUtils.getTempFilename("dbf")
        provider = table.dataProvider()
        isASCII=True
        try:
            unicode(table.source()).decode("ascii")
        except UnicodeEncodeError:
            isASCII=False
        isDbf = unicode(table.source()).endswith("dbf") or unicode(table.source()).endswith("shp")
        if (not isDbf or not isASCII):
            writer = QgsVectorFileWriter( output, systemEncoding, provider.fields(), QGis.WKBNoGeometry, provider.crs() )
            for feat in table.getFeatures():
                writer.addFeature(feat)
            del writer
            return output
        else:
            filename = unicode(table.source())
            if unicode(table.source()).endswith("shp"):                 
                return filename[:-3] + "dbf"
            else:
                return filename
    
    


