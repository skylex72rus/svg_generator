#!/usr/local/bin/python2.7
# -*- coding: utf-8 -*-

'''
Created on 15.06.2017

@author: Alexey Russkikh
'''


import sys,os
import math
import matplotlib.pyplot as plt

#===============================================================================
# 
#===============================================================================
class logReplacer():
    def __init__(self):
        pass
    def logMessage(self,text,tag,lvl=0):
        print "{}:{}".format(tag,text)
        
try:
    from qgis.core import QgsMessageLog
except:
    QgsMessageLog=logReplacer()
#===============================================================================
# 
#===============================================================================
class ColorVal():
    def __init__(self
                 ,color
                 ,val):
        self._color=color
        self._val=val
    @property
    def val(self):
        return self._val
    @property
    def color(self):
        return self._color
    def __str__(self):
        return "{}:{}".format(str(self._color),str(self._val))
    def __repr__(self):
        return self.__str__()
    
#===============================================================================
# 
#===============================================================================
class ColorValLst():
    def __init__(self
                 ,colorval_lst=None
                 ,name=None
                 ):
        self._colorval_lst=[]
        if colorval_lst is not None:
            self._colorval_lst=colorval_lst
        self._name=None
        if name is not None:
            self._name=name
    def add_colorval(self,color,val):
        self._colorval_lst.append(ColorVal(color,val))
    @property 
    def color_lst(self):
        return map(lambda x:x.color,self._colorval_lst)
    @property 
    def val_lst(self):
        return map(lambda x:x.val,self._colorval_lst)
    @property
    def sum_val(self):
        return sum(self.val_lst)
    @property
    def max_val(self):
        return max(self.val_lst)
    def __str__(self):
        return "{}:[{}]".format(str(self._name)
                                ,"],[".join(map(str,self._colorval_lst))
                                )
    def __repr__(self):
        return self.__str__()
    
#===============================================================================
# 
#===============================================================================
class LstColorValLst():
    QGIS_COR=2.835
    def __init__(self):
        self._lst_colorvallst=[]
    def set_data(self,dict_of_lst_of_colorval):
        for key,lst_of_colorval in  dict_of_lst_of_colorval.items():
            cvl=ColorValLst(name=key)
            for (color,val) in lst_of_colorval: 
                cvl.add_colorval(color, val)
            self._lst_colorvallst.append(cvl)
    def set_dataRadiusFromSqare(self,dict_of_lst_of_colorval):
        for key,lst_of_colorval in  dict_of_lst_of_colorval.items():
            cvl=ColorValLst(name=key)
            for (color,val) in lst_of_colorval: 
                cvl.add_colorval(color, math.sqrt(val/math.pi))
            self._lst_colorvallst.append(cvl)

    def sorted_iter(self,reverse=False):
        for cvl in sorted(self._lst_colorvallst,key=lambda cvl: cvl.sum_val,reverse=reverse):
            yield cvl
    def __it__(self):
        for cvl in self._lst_colorvallst:
            yield cvl
    def __str__(self):
        return "[{}]".format("],[".join(map(str,self._lst_colorvallst)))
    def __repr__(self):
        return self.__str__()
    @property
    def max_val(self):
        return max(map(lambda cvl: cvl.sum_val,self._lst_colorvallst))
    @property
    def max_val_toQgis(self):
        return self.max_val*LstColorValLst.QGIS_COR
    

#     @property
#     def max_val_toRadius(self):
#         return math.sqrt(self.max_val/math.pi)
#     @property
#     def max_val_toRadiusQgis(self):
#         return self.max_val_toRadius*self.QGIS_COR
    
#===============================================================================
# 
#===============================================================================
#class LstColorValLst
#===============================================================================
# 
#===============================================================================
class SvgDrawer():
    def __init__(self
                 ,res_folder
                 ):
        self._path=res_folder
        self._idx=0
        self._plt=plt
        fig, ax = self._plt.subplots()
        fig.patch.set_visible(False)
        ax.axis('off')
        self._fix=fig
        self._ax=ax
        if not os.path.isdir(self.svg_folder):
            QgsMessageLog.logMessage("try create directory "+self.svg_folder, tag="SvgBubble")
            os.mkdir(self.svg_folder)
        
    @property
    def svg_name(self):
        res= r"{}.svg".format(str(self._idx))
        return res
    @property
    def svg_folder(self):
        return self._path
    @property
    def svg_path(self):
        res= r"{}\{}".format(self._path,self.svg_name)
        return res
    def save_plot(self,show_plot=False):
        if show_plot:self._plt.show()
        QgsMessageLog.logMessage("try saving to "+self.svg_path, tag="SvgBubble")
        self._plt.savefig(self.svg_path)
        self._plt.cla()
    def next_plot(self):
        self._idx+=1
    
    #===========================================================================
    # 
    #===========================================================================
    def to_multibubl_svg(self
                         ,dict_of_bubbles
                         ,show_plot=False
                         ,max_val_f=lambda f:f.max_val_toQgis
                         ):
        """
            @param dict_of_bubbles: dict of bubbles. Each bubble= name:[[color,val],[color,val]...]. 'val' is bubbl sqare,converted to radius
            @param show_plot: if True then plot showed and not saved to file
            @param max_val_f: function used for calc size_value. Look for LstColorValLst class functions
            @return :full path to svg, size_val
                            
        """
        self.next_plot()        
        bubbles=LstColorValLst()
        bubbles.set_dataRadiusFromSqare(dict_of_bubbles)
        for bubbl in bubbles.sorted_iter(reverse=True):
            colors=bubbl.color_lst
            values=bubbl.val_lst
            radius=bubbl.sum_val
            #colors =[[0.1,0.2,0.3] for i in range(len(colors)) ]
            #colors1 =[pd.np.random.rand(3,1) for i in range(len(colors))] 
            #colors =[pd.np.random.rand(3,1) for i in range(5)]
            if radius>0:
                patches, texts = self._ax.pie(values, colors=colors, shadow=False, startangle=90,radius=radius)
        if bubbles.max_val>0:
            self._plt.axis('equal')
            self._plt.tight_layout()
            #self._plt.axis([-1*radius, radius, -1*radius, radius])
            self.save_plot(show_plot=show_plot)
            return self.svg_name,max_val_f(bubbles)
        else:
            return None,None

#===============================================================================
# 
#===============================================================================
def test():
    drawer=SvgDrawer(res_folder=r"E:\_tmp\qgis\PDS_Wells20170615142011831")
    data={
          "a":[["#8b0a50",math.pow(0.5,2)*math.pi]
               ,["#ffcc00",math.pow(0.5,2)*math.pi]]
#            ,"b":[["#27c1ce",2]
#                  ,["#d4cece",2]]
#            ,"c":[["#8b0a50",4]
#                  ,["#7d4682",3]]
          }
    path,size=drawer.to_multibubl_svg(dict_of_bubbles=data,show_plot=False
                         ,max_val_f=lambda f:f.max_val_toQgis
                                      )
    print path
    print size
    print math.sqrt(size/math.pi)
#===============================================================================
# 
#===============================================================================
if __name__ == '__main__':
    test()
    
    
    
    
    