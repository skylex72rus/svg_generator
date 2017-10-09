# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SvgBubbl
                                 A QGIS plugin
 create svg images from vector layer
                              -------------------
        begin                : 2017-06-18
        git sha              : $Format:%H$
        copyright            : (C) 2017 by Alex Russkikh. 
        email                : skylex72rus@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, QVariant
from PyQt4.QtGui import QAction, QIcon,QHBoxLayout, QMessageBox
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from svg_generator_dialog import SvgBubblDialog
import os.path
#from qgis.core import QgsLabelingEngineV2
from qgis.core import QgsField,QgsExpression,QgsExpressionContext,QgsMessageLog,QgsSymbolV2,QgsRuleBasedRendererV2,QgsSvgMarkerSymbolLayerV2
from qgis.core import QgsExpressionFieldBuffer,QgsRendererCategoryV2,QgsCategorizedSymbolRendererV2,QgsSingleSymbolRendererV2,QgsProject
from svg_matplot import SvgDrawer

C_SVG_PATH="bubbl_svg"
C_SVG_RADIUS="bubbl_size"
C_SVG_NAME="bubbl_svg_name"

class SvgBubbl:
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
            'SvgBubbl_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)


        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Svg Image Generator')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'SvgBubbl')
        self.toolbar.setObjectName(u'SvgBubbl')


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
        return QCoreApplication.translate('SvgBubbl', message)


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

        # Create the dialog (after translation) and keep reference
        self.dlg = SvgBubblDialog()
        

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/SvgBubbl/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'generating svg images'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Svg Image Generator'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar


    def run(self):
        """Run method that performs all the real work"""

        #field_expression_widget.show()
        self.dlg.show()
        #set in combobox layer to active layer
        try:
            QgsMessageLog.logMessage("changing layer to selected in legend", tag="SvgBubble")
            selectedLayer = self.iface.activeLayer()#iface.legendInterface().selectedLayers()
            self.dlg.lyrCombobox.setLayer(selectedLayer)
        except:
            QgsMessageLog.logMessage("cant set selected layer", tag="SvgBubble")

        
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            QgsMessageLog.logMessage("Start calculate values", tag="SvgBubble")
            layer = self.dlg.lyrCombobox.currentLayer()  
            self.iface.setActiveLayer(layer)
            LAYER_NAME = layer.id()#.name()
            PROJECT_PATH = QgsProject.instance().readPath("./")
            QgsMessageLog.logMessage("Folder={} Layer={}".format(PROJECT_PATH,LAYER_NAME), tag="SvgBubble")
            provider= layer.dataProvider()
            #QMessageBox.information(None, "Layer info", ",".join(map(lambda x:x.currentText(),exprs)))
            # Add new column to layer
            idx = provider.fieldNameIndex(C_SVG_NAME)
            if idx == -1:
                QgsMessageLog.logMessage("Create field={}".format(C_SVG_NAME), tag="SvgBubble") 
                provider.addAttributes([QgsField(C_SVG_NAME, QVariant.String)])
            idx = provider.fieldNameIndex(C_SVG_RADIUS)
            if idx == -1:
                QgsMessageLog.logMessage("Create field={}".format(C_SVG_RADIUS), tag="SvgBubble") 
                provider.addAttributes([QgsField(C_SVG_RADIUS, QVariant.Double,'double',20,2)])
            layer.updateFields()
            ##############  UPDATE VIRTUAL FIELD
            QgsMessageLog.logMessage("Create field={}".format(C_SVG_PATH), tag="SvgBubble")
            caps_string = layer.dataProvider().capabilitiesString()
            QgsMessageLog.logMessage("Layer capabilities={}".format(caps_string), tag="SvgBubble")
            
            isExpPresent=False
            field = QgsField( C_SVG_PATH, QVariant.String )
            field_exp="eval('@project_folder')+'/{}/'+ \"{}\"".format(LAYER_NAME,C_SVG_NAME)
            for _idx,atr in enumerate(layer.pendingFields()):
                QgsMessageLog.logMessage("All fields=[{}]{}".format(str(_idx),str(atr.name())), tag="SvgBubble")
                if atr.name()==C_SVG_PATH:
                    QgsMessageLog.logMessage("Old layer idx={}".format(str(_idx)), tag="SvgBubble")
                    #layer.removeExpressionField(_idx) #not work
                    #layer.deleteAttribute(_idx)       #not work on expression
                    layer.updateExpressionField(_idx,field_exp)
                    isExpPresent=True
                    QgsMessageLog.logMessage("Field {} updated".format(C_SVG_PATH), tag="SvgBubble")
                    break
            if not isExpPresent:
                layer.addExpressionField(field_exp , field )
                QgsMessageLog.logMessage("Field {} created".format(C_SVG_PATH), tag="SvgBubble")
            QgsMessageLog.logMessage("Field func={}".format(field_exp), tag="SvgBubble")
            layer.updateFields()
            #############   start edit layer feature
            layer.startEditing()
            # Set new column value
            QgsMessageLog.logMessage("Start updating table data", tag="SvgBubble")
            preset_rows=self.dlg.preset_rows
            svg_drawer=SvgDrawer("{}/{}".format(PROJECT_PATH,LAYER_NAME))
            for f in layer.getFeatures():
                #well_idx = layer.fieldNameIndex('well_id')
                #QgsMessageLog.logMessage(str(f.attributes()[well_idx]), tag="SvgBubble")
                #values=map(lambda x:x.evaluate(f),exp_lst)#exp.evaluate(f)
                #QMessageBox.information(None, "Layer info",str(values))  #!!!!!DEBUG
                preset_rows.setFeature(f)
                bubles={}
                for key,presets in preset_rows.asDict().items():
                    bubl_parts=[]
                    for preset in presets:
                        QgsMessageLog.logMessage(str(preset.exp_txt), tag="SvgBubble",level=3)
                        val=preset.execute()
                        QgsMessageLog.logMessage(str(val), tag="SvgBubble",level=3)
                        color=preset.color_hex
                        if val is None:continue
                        else:bubl_parts.append([color,val])
                        #QMessageBox.information(None, "execute info","{}:{}".format(key,str(bubl_parts)))  #!!!!!DEBUG
                    if len(bubl_parts)>0:
                        bubles[key]=bubl_parts
                    else:
                        pass
                QgsMessageLog.logMessage(str(bubles), tag="SvgBubble",level=3)
                svg_name,svg_size=svg_drawer.to_multibubl_svg(bubles)
                QgsMessageLog.logMessage(str(svg_name), tag="SvgBubble",level=2)
                #QMessageBox.information(None, "Execute result saved to",str(res_path))  #!!!!!DEBUG
                if not svg_name is None:
                    layer.changeAttributeValue(f.id(), layer.fieldNameIndex(C_SVG_NAME), svg_name)
                    layer.changeAttributeValue(f.id(), layer.fieldNameIndex(C_SVG_RADIUS),svg_size)
            QgsMessageLog.logMessage("End feature iterator", tag="SvgBubble")
            layer.commitChanges()        
            # create a new rule-based renderer
            # get the "root" rule
            svgStyle = {}
            svgStyle['name'] = '"bubbl"'
            svgStyle["name_dd_active"] ="1"
            svgStyle["name_dd_expression"]=""
            svgStyle['name_dd_field'] = C_SVG_PATH
            svgStyle['name_dd_useexpr'] = "0"
            svgStyle["offset"]="0.0"
            svgStyle["scale_method"]="diameter"
            svgStyle["size"]="1"
            svgStyle["size_dd_active"]="1"
            svgStyle["size_dd_expression"]='"{}"/1000'.format(C_SVG_RADIUS)
            svgStyle['size_dd_field'] = ''
            svgStyle['size_dd_useexpr'] = "1"
            svgStyle['idx'] = "bubbl_layer"
            symbol_layer = QgsSvgMarkerSymbolLayerV2.create(svgStyle)
            symbol = QgsSymbolV2.defaultSymbol(layer.geometryType())
                
            renderer = QgsSingleSymbolRendererV2(symbol)                
            QgsMessageLog.logMessage("set renderer", tag="SvgBubble")
            # assign the created renderer to the layer
            isSvgVisible=False
            for _idx_sym,preset_sym in enumerate(layer.rendererV2().symbols()):
                for _idx_symlyr,preset_symlyr in enumerate(preset_sym.symbolLayers()):
                    lyr_type=preset_symlyr.layerType()
                    lyr_prop=preset_symlyr.properties()
                    if lyr_type=="SvgMarker" and lyr_prop["name_dd_field"]==C_SVG_PATH:
                        QgsMessageLog.logMessage("symbollayer properties="+str(lyr_prop), tag="SvgBubble")
                        QgsMessageLog.logMessage("symbollayer type="+str(lyr_type), tag="SvgBubble")
                        #renderer.symbols()[_idx_sym].changeSymbolLayer(_idx_symlyr, symbol_layer)
                        isSvgVisible=True
                        break
            if not isSvgVisible:
                #layer.rendererV2().symbols()[0].appendSymbolLayer(symbol_layer)
                layer.rendererV2().symbols()[0].insertSymbolLayer(0,symbol_layer)
                
                #renderer.symbols()[0].changeSymbolLayer(0, symbol_layer)
            #if renderer is not None:   layer.setRendererV2(renderer)
            #layer.setRendererV2(renderer)
            QgsMessageLog.logMessage("repaint", tag="SvgBubble")
            layer.triggerRepaint()
            QgsMessageLog.logMessage("Finished", tag="SvgBubble")
            
            
            pass
