# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SvgBubblDialog
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


from PyQt4 import QtGui, uic
from PyQt4 import QtCore
from PyQt4.QtCore import pyqtSlot,pyqtSignal
from qgis.gui import QgsFieldExpressionWidget,QgsMessageBar,QgsColorButton,QgsMapLayerComboBox
from qgis.core import QgsProject,QgsExpression,QgsMessageLog
from qgis.utils import iface

import os
import pickle
import json
from copy import deepcopy

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'svg_generator_dialog_base.ui'))
#from svg_generator_dialog_base import * 
#FORM_CLASS=Ui_SvgBubblDialogBase

#===============================================================================
# 
#===============================================================================
class PresetRow():
    def __init__(self
                 ,qgsfieldexpressionwidget=None
                 ,qgscolorbutton=None
                 ,qspinbox=None
                 ):
        self._qgsfieldexpressionwidget=qgsfieldexpressionwidget
        if qgsfieldexpressionwidget is None:
            self._qgsfieldexpressionwidget=QgsFieldExpressionWidget()
        self._qgscolorbutton=qgscolorbutton
        if qgscolorbutton is None:
            self._qgscolorbutton=QgsColorButton()
        self._qspinbox=qspinbox
        if qspinbox is None:
            self._qspinbox=QtGui.QSpinBox()
        self._last_feature=None
        
    def set_layer(self,layer_id):
        self._qgsfieldexpressionwidget.setLayer(layer_id)
    def __del__(self):
        self._qgsfieldexpressionwidget.deleteLater()
        self._qgsfieldexpressionwidget=None
        self._qgscolorbutton.deleteLater()
        self._qgscolorbutton=None
        self._qspinbox.deleteLater()
        self._qspinbox=None
    def __str__(self):
        return "{}-{}-{}".format(str(self._qgsfieldexpressionwidget)
                                 ,str(self._qgscolorbutton)
                                 ,str(self._qspinbox)
                                 )
    def __repr__(self):
        return self.__str__()
    def asLst(self):
        return self._qgscolorbutton,self._qgsfieldexpressionwidget,self._qspinbox
    @property
    def qgsfieldexp(self):
        return self._qgsfieldexpressionwidget
    @property
    def exp_txt(self):
        return self._qgsfieldexpressionwidget.currentText()

    @property
    def qgscolorbutton(self):
        return self._qgscolorbutton
    @property
    def qspinbox(self):
        return self._qspinbox
    @property
    def lvl(self):
        return self._qspinbox.value()
    def copy(self):
        field_expression_widget = QgsFieldExpressionWidget()
        field_expression_widget.setLayer(self._qgsfieldexpressionwidget.layer())
        field_expression_widget.setField(self._qgsfieldexpressionwidget.currentText())
        
        color_btn_widget = QgsColorButton()
        color_btn_widget.setColor(self._qgscolorbutton.color())
        spinbox=QtGui.QSpinBox()
        spinbox.setValue(self._qspinbox.value())
        return PresetRow(field_expression_widget, color_btn_widget, spinbox)
    #===========================================================================
    # 
    #===========================================================================
    def dump(self):
        exp=self._qgsfieldexpressionwidget.currentText()
        #color=self._qgscolorbutton.color().name() 
        color=self._qgscolorbutton.color().rgba() 
        idx=self._qspinbox.value()
        res={
             "exp":exp
             ,"color":color
             ,"idx":idx
         }
        return json.dumps(res)
    #=======================================================================
    # 
    #=======================================================================
    def load(self,str_dump):
        res=json.loads(str_dump)
        self._qgsfieldexpressionwidget.setField(res["exp"])
        #self._qgscolorbutton.color().setNamedColor(res["color"])
        qcolor=self._qgscolorbutton.color()
        qcolor.setRgba(res["color"])
        self._qgscolorbutton.setColor(qcolor) 
        self._qspinbox.setValue(res["idx"])
    @property
    def exp(self):
        return QgsExpression(self._qgsfieldexpressionwidget.asExpression())
    @property
    def qcolor(self):
        return self._qgscolorbutton.color() 
    @property
    def color_rgba(self):
        return self._qgscolorbutton.color().rgba()
    @property
    def color_hex(self):
        return self._qgscolorbutton.color().name() 
    
    def setFeature(self,feature):
        self._last_feature=feature
    def execute(self,feature=None):
        if feature is not None:
            self.setFeature(feature)
        if self._last_feature is None:return None
        else:  return self.exp.evaluate(self._last_feature)
    
    
#===============================================================================
# 
#===============================================================================
class PresetRows():
    def __init__(self
                 ,presets=None):
        self._presets=[]
        if not presets is None:
            self._presets=presets
    def add_preset(self,preset_row):
        self._presets.append(preset_row)
    def get_preset(self,idx):
        return self._presets[idx]
    def count(self):
        return len(self._presets)
    def set_preset_layer(self,layer_id):
        map(lambda x:x.set_layer(layer_id),self._presets)
    def pop(self):
        self._presets.pop()
    def clear(self):
        for preset in self._presets:
            preset.__del__()
            self._presets=[]
    def __str__(self):
        return "[{}]".format("],[".join(
                                 map(str,self._presets)
                                 ))
    def __iter__(self):
        for x in self._presets:
            yield x
    @property
    def qgsfieldexp_lst(self):
        return [x.qgsfieldexp for x in self._presets]
    @property
    def qgscolorbutton_lst(self):
        return [x.qgscolorbutton for x in self._presets]
    @property
    def qspinbox_lst(self):
        return [x.qspinbox for x in self._presets]
    @property
    def exp_lst(self):
        return [x.exp for x in self._presets]
     
    def copy(self):
        preset=[x.copy() for x in self._presets]
        return PresetRows(presets=preset)
    def dump(self):
        res=map(lambda x:x.dump(),self._presets)
        return json.dumps(res)
    def load(self,str_dump):
        res_lst=json.loads(str_dump)
        for row in res_lst:
            preset=PresetRow()
            preset.load(row)
            self._presets.append(preset)
    def asDict(self):
        """return dictionary of list 'preset' grouped by 'lvl' value
        """
        res={}
        for preset in self._presets:
            lvl=preset.lvl
            if lvl in res.keys():
                res[lvl].append(preset)
            else:
                res[lvl]=[preset]
        return res
    def setFeature(self,feature):
        for preset in self._presets:
            preset.setFeature(feature)
    def get_group(self,group_id):
        as_dict=self.asDict()
        res=None
        if group_id in as_dict:
            return as_dict[group_id]
        else: return None
    def exec_group_sum(self,group_id):
        group_presets=self.get_group(group_id)
        res=None
        if group_presets is not None:
            res=sum(map(lambda x:x.execute(),group_presets))
        return res
    def exec_group_max(self,group_id):
        group_presets=self.get_group(group_id)
        res=None
        if group_presets is not None:
            res=max(map(lambda x:x.execute(),group_presets))
        return res
        
        
        
#===============================================================================
# 
#===============================================================================
class SvgBubblDialog(QtGui.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(SvgBubblDialog, self).__init__(parent)
        path_prj=QgsProject.instance().readPath("./")
        self.CONF_PATH=os.path.join(path_prj,"svgbubbl.conf.json")
        self.MAX_SPINBOX=10000000
#         self._fields_lst=[]
#         self._color_lst=[]
        self._preset_rows=PresetRows()
        
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        #self.setFixedSize(self.size()) #---FIX MAIN WINDOW SIZE
        self.bar = QgsMessageBar()
        self.bar.setSizePolicy( QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed )
        self.lyrCombobox = QgsMapLayerComboBox()
        self.lyrCombobox.layerChanged.connect(self.action_lyr_update) # selected layer from combobox
        
        self.horizontalLayout.addWidget(self.lyrCombobox)
        self.configBox.currentIndexChanged.connect(self.action_config_set)
        self.configPlus.clicked.connect(self.action_config_add)
        self.configMinus.clicked.connect(self.action_config_remove)

        btnAdd = QtGui.QPushButton('Add expression', self)
        btnAdd.setToolTip('Tooltip <b>QPushButton</b> widget')
        btnAdd.clicked.connect(self.action_field_add) # connect btn action 'clicked()' and function add_field
        btnRem = QtGui.QPushButton('Remove expression', self)
        btnRem.clicked.connect(self.action_field_pop) # connect btn action 'clicked()' and function add_field
        self.horizontalLayout_2.addWidget(btnAdd,0)
        self.horizontalLayout_2.addWidget(btnRem,1)
        self.show_preset_window()
        self.finished.connect(self.config_dump)
        #read config presets
        if os.path.exists(path=self.CONF_PATH):
            self.config_load()
            self.action_config_set()
        QgsMessageLog.logMessage("main window loaded", tag="SvgBubble")
    #===================================================================
    # 
    #===================================================================
    def show_preset_window(self):
        self.mygroupbox = QtGui.QGroupBox('this is my groupbox')
        self.configPreset = QtGui.QFormLayout()
        self.mygroupbox.setLayout(self.configPreset)
        self.scroll = QtGui.QScrollArea()
        self.scroll.setWidget(self.mygroupbox)
        self.scroll.setWidgetResizable(True)
        self.verticalLayout.addWidget(self.scroll)
    def clear_preset_window(self):
        self.mygroupbox.deleteLater()
        self.configPreset.deleteLater()
        self.scroll.deleteLater()
        self.mygroupbox=None
        self.configPreset=None
        self.scroll=None
    #===========================================================================
    # load config
    #===========================================================================
    @pyqtSlot()
    def action_config_set(self):
        if self.configBox.count()>0:
            #self.bar.pushMessage("configBox", "currentIndexChanged", level=QgsMessageBar.INFO)
            presetrows=self.configBox.itemData(self.configBox.currentIndex())
            #self.bar.pushMessage("configBox", str(presetrows), level=QgsMessageBar.INFO)
            #self.bar.pushMessage("configBox", str(self._preset_rows), level=QgsMessageBar.INFO)
            self._preset_rows=presetrows.copy()
            self.redraw_fields()
            
    #===========================================================================
    # add config preset
    #===========================================================================
    @pyqtSlot()
    def action_config_add(self):
        text, ok = QtGui.QInputDialog.getText(self, 'Input Dialog', 'Enter config name:')
        if ok:
            #if preset exist then remove old 
            if self.configBox.findText(text)>=0:
                #self.configBox.removeItem(self.configBox.findText(text))
                self.configBox.setItemData(self.configBox.findText(text)
                                       ,self._preset_rows.copy())
            else:
                #store new preset
                self.configBox.addItem(text
                                       ,self._preset_rows.copy())
            #select current preset as active
            self.configBox.setCurrentIndex(self.configBox.findText(text))
    #===========================================================================
    # 
    #===========================================================================
    @pyqtSlot()
    def action_config_remove(self):
        self.configBox.removeItem(self.configBox.currentIndex())
        pass
    #=========================================================================
    # 
    #=========================================================================
    def config_dump(self):
        #self.bar.pushMessage("configBox", "config_dump", level=QgsMessageBar.INFO)
        texts = [(self.configBox.itemText(i), self.configBox.itemData(i).dump()) for i in range(self.configBox.count())]
        
        ou_f=open(self.CONF_PATH,mode="w")
        json.dump(texts,ou_f)
        ou_f.flush()
        ou_f.close()
        
        
#         texts = [(self.configBox.itemText(i), self.configBox.itemData(i)) for i in range(self.configBox.count())]
#         ou_f=open(self.CONF_PATH,mode="w")
#         #json.dump(texts,ou_f)
#         pickle.dump(texts, ou_f)
#         ou_f.flush()
#         ou_f.close()
         
    #=========================================================================
    # 
    #=========================================================================
    def config_load(self):
        texts=None
        try:
            texts=json.load(open(self.CONF_PATH))
        except:
            self.bar.pushMessage("Trigger", "Defaul preset not founded", level=QgsMessageBar.INFO)
            pass
        if texts is not None:
            for name,text in texts:
                #self.bar.pushMessage("Trigger", text, level=QgsMessageBar.INFO)
                
                preset_rows=PresetRows()
                preset_rows.load(text)
                if self.configBox.findText(name)>=0:
                    self.configBox.setItemData(self.configBox.findText(name)
                                           ,preset_rows)
                else:
                    self.configBox.addItem(name
                                           ,preset_rows)
            self.action_lyr_update()
#         try:
#             dump_texts=pickle.load(file=open(self.CONF_PATH))
#             self.configBox.clear()
#             for name,preset_rows in dump_texts:
#                self.configBox.addItem(name
#                                       ,preset_rows)
#         except:pass

      
    #===========================================================================
    # 
    #===========g================================================================
    @pyqtSlot()  
    def action_lyr_update(self):
        self._preset_rows.set_preset_layer(self.lyrCombobox.currentLayer())
    #===============================================================
    # 
    #===============================================================
    @pyqtSlot()  
    def action_field_add(self):
        #self.bar.pushMessage("Trigger", "signal received", level=QgsMessageBar.INFO)
        field_expression_widget = QgsFieldExpressionWidget()
        field_expression_widget.setLayer(self.lyrCombobox.currentLayer())
        color_btn_widget = QgsColorButton()
        spinbox=QtGui.QSpinBox()
        presetrow=PresetRow(qgsfieldexpressionwidget=field_expression_widget
                            , qgscolorbutton=color_btn_widget
                            , qspinbox=spinbox
                            )
        self._preset_rows.add_preset(presetrow)
        self.redraw_fields()
    #===================================================================
    # 
    #===================================================================
    @pyqtSlot()  
    def action_field_pop(self):
        self._preset_rows.pop()
        
    #===========================================================================
    # @param fields:    
    #            list of exprression string
    # @param colors:
    #            list of QColor 
    #===========================================================================
    def redraw_fields(self):
        #---neeed clear widgets on self.configPreset
        self.clear_preset_window()
        self.show_preset_window()
        for preset in self._preset_rows:
            #self.bar.pushMessage("Trigger", str(preset), level=QgsMessageBar.INFO)
            layout=QtGui.QHBoxLayout()
            layout.addWidget(preset.qgscolorbutton)
            layout.addWidget(preset.qgsfieldexp)
            layout.addWidget(preset.qspinbox)
            self.configPreset.addRow(layout)
    @property
    def preset_rows(self):
        return self._preset_rows
    @property                                     
    def expressions(self):
        return self._preset_rows.qgsfieldexp_lst
    @property
    def colors(self):
        return self._preset_rows.qgscolorbutton_lst


        
        
        
