# -*- coding: utf-8 -*-
"""
/***************************************************************************
 IDEPBH
                                 A QGIS plugin
 IDEPBH
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2019-04-16
        git sha              : $Format:%H$
        copyright            : (C) 2019 by IDEPBH
        email                : tiago.cnorberto@pbh.gov.br
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
Refencias https://pypi.org/project/OWSLib/

https://github.com/eswright/cgdi-qgis-services/blob/master/CanadianWebServices/canadian_web_services.py#L357

"""
from PyQt5.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction ,QTableWidget,QTableWidgetItem, QMessageBox, QAbstractItemView

from owslib.wms import WebMapService
from owslib.wfs import WebFeatureService

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .IDEPBH_dialog import IDEPBHDialog
import os.path

from qgis.core import QgsRasterLayer, QgsProject, QgsVectorLayer,  QgsMessageLog

"""
Para alterar o icone e necessario utilizar o comando pb_tool compile
"""

class IDEPBH:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'IDEPBH_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&IDEPBH')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('IDEPBH', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/IDEPBH/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'IDEPBH WMS/WFS'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&IDEPBH'),
                action)
            self.iface.removeToolBarIcon(action)


    def run(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            self.dlg = IDEPBHDialog()

        # setar a selecao por linha
        self.dlg.tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.dlg.tableWidget_2.setSelectionBehavior(QAbstractItemView.SelectRows)

        # setar a alteracao no campo de texto
        self.dlg.lineLayerName.textChanged.connect(self.filterLayer)

        # conectar o link na tabela com as funcoes para carregar a camada
        self.dlg.tableWidget.itemSelectionChanged.connect(self.selectLayer)
        self.dlg.tableWidget_2.itemSelectionChanged.connect(self.selectLayerWFS)
        
        # buscar camadas de WMS
        self.findLayerWMS()
        # buscar camadas de WFS
        self.findLayerWFS()

        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass


    def findLayerWMS(self):
        """"
        Buscar as camadas utilizando WMS
        """
        try:
            service_url = "http://bhmapogcbase.pbh.gov.br/bhmapogcbase/ows"

            wms = WebMapService(service_url) 

            listLayer = list(wms.contents)   # creates a list of the names of each layer in the service
            listFilter =  list(filter(lambda k: 'ide_bhgeo:' in k, listLayer))

            self.dlg.tableWidget.setRowCount(len(listFilter)) 

            i = 0
            for layer in listFilter:
                self.dlg.tableWidget.setItem(i,1, QTableWidgetItem(wms[layer].name))
                self.dlg.tableWidget.setItem(i,0, QTableWidgetItem(wms[layer].title))
                i = i +1
        except Exception as e:
            QgsMessageLog.logMessage("Ocorreu um erro "+str(e))
            QMessageBox.critical(None,"Mensagem de erro","Ocorreu um erro, verifique a sua conexão com a internet \n Descrição: "+str(e))
            self.dlg.close()

    def findLayerWFS(self):
        """"Buscar as camadas utilizando WFS
        """

        try:
            service_url = "http://bhmapogcbase.pbh.gov.br/bhmapogcbase/wfs"

            wfs = WebFeatureService(service_url) 

            listLayer = list(wfs.contents)   # creates a list of the names of each layer in the service
            listFilter =  list(filter(lambda k: 'ide_bhgeo:' in k, listLayer))

            self.dlg.tableWidget_2.setRowCount(len(listFilter)) 

            i = 0
            for layer in listFilter:
                self.dlg.tableWidget_2.setItem(i,1, QTableWidgetItem(wfs[layer].id))
                self.dlg.tableWidget_2.setItem(i,0, QTableWidgetItem(wfs[layer].title))
                i = i +1
        
        except  Exception as e:
            QgsMessageLog.logMessage("Ocorreu um erro "+str(e))
            QMessageBox.critical(None,"Mensagem de erro","correu um erro, verifique a sua conexão com a internet \n Descrição:"+str(e))
            self.dlg.close()


    def selectLayer(self):
        serv = self.getSelectedServices()

        if self.checkisLayersExist(serv) == "true":
            return

        service_url = "http://bhmapogcbase.pbh.gov.br/bhmapogcbase/ows"

        urlWithParams1 = 'url='+str(service_url)+'&format=image/png&layers='
        urlWithParams2 = '&styles=&crs=EPSG:'+str("31983")
        urlWithParams = urlWithParams1 + serv + urlWithParams2

        # create the layer and add it to the map
        rlayer = QgsRasterLayer(urlWithParams, "WMS_"+str(serv), "wms")

        if not rlayer.isValid(): # set service Errors to True if any layers can't be loaded
            serviceErrors = True

        QgsProject.instance().addMapLayer(rlayer)


    def selectLayerWFS(self):
        serv = self.getSelectedServicesWFS()

        if self.checkisLayersExist(serv) == "true":
            return

        service_url = "http://bhmapogcbase.pbh.gov.br/bhmapogcbase/ows"

        urlWithParams1 = 'http://bhmapogcbase.pbh.gov.br/bhmapogcbase'+'/ows'
        urlWithParams2 = '?service=WFS&version=2.0.0&typename='
        urlWithParams = urlWithParams1 + urlWithParams2+ str(serv)

        #print(serv)
        # create the layer and add it to the map
        vlayer = QgsVectorLayer(urlWithParams, "WFS_"+str(serv), "WFS")

        if not vlayer.isValid(): # set service Errors to True if any layers can't be loaded
            serviceErrors = True

        QgsProject.instance().addMapLayer(vlayer)

    def getSelectedServices(self):
        rowNums = []
        selected = self.dlg.tableWidget.selectedItems()
        return selected[1].text()

    
    def getSelectedServicesWFS(self):
        rowNums = []
        selected = self.dlg.tableWidget_2.selectedItems()
        return selected[1].text()

    
    def checkisLayersExist(self, name):
        for lyr in QgsProject.instance().mapLayers().values():
            layerName = lyr.name()
            if layerName == name :
                return "true"  
        return "false"

    
    def filterLayer(self, text):
        """
        Filtrar as linhas da tabela se acordo com o texto digitado
        Para cada evento de teclado esconder ou mostrar as linhas das tabelas
        """
        allRows = self.dlg.tableWidget.rowCount()
        for row in range(0,allRows):
            name = self.dlg.tableWidget.item(row,0)
            if text.upper() in name.text().upper():
                self.dlg.tableWidget.showRow(row)
            else:
                self.dlg.tableWidget.hideRow(row)

        allRows = self.dlg.tableWidget_2.rowCount()
        for row in range(0,allRows):
            name = self.dlg.tableWidget_2.item(row,0)
            if text.upper() in name.text().upper():
                self.dlg.tableWidget_2.showRow(row)
            else:
                self.dlg.tableWidget_2.hideRow(row)