#!python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 27 11:07:11 2017

@author: Andreas.Waeber
"""
###############
### IMPORTS ###
###############

import sys
import os
from PyQt5 import QtCore, QtWidgets
#from PyQt5.QtGui import QMdiArea, QMdiSubWindow
import matplotlib
matplotlib.use('Qt5Agg') # Make sure that we are using QT5
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
#import matplotlib.pyplot as plt
from matplotlib.path import Path
import matplotlib.patches as patches
import numpy as np
import scipy.io # to read and write .mat files
import scipy.optimize as opt
from scipy.interpolate import griddata

import dxfgrabber
from dxfwrite import DXFEngine as dxf

os.chdir("C:/DOCS/Python/MyPy") # set current directory to MyPy
import tum_jet # definition of TUM colours

###############
### GLOBALS ###
###############

progname = 'Pyk-A-Boo'
progversion = "0.5.2"

def test():
    pass

def twoD_Gaussian_sym(xy, amplitude, xo, yo, sigma, offset):
    xo = float(xo)
    yo = float(yo)
    g = offset + amplitude*np.exp( - (((xy[0]-xo)**2) + ((xy[1]-yo)**2))/(2*sigma**2))
    return g.ravel()

def affine_trafo(raw_coords, real_coords):
    primary = np.array(raw_coords)
    secondary = np.array(real_coords)

    # Pad the data with ones, so that our transformation can do translations too
    if primary.shape[0] >= 3:
        pad = lambda x: np.hstack([x, np.ones((x.shape[0], 1))])
#        unpad = lambda x: x[:,:-1]
        X = pad(primary)
        Y = pad(secondary)
        A, res, rank, s = np.linalg.lstsq(X, Y, rcond = 1e-4)
#        transform = lambda x: unpad(np.dot(pad(x), A))
        return A
    else:
        return []

def flatten_list(lst):
    return [item for sublist in lst for item in sublist]

######################
### HELPER CLASSES ###
######################

class Stack:
     def __init__(self):
         self.items = []

     def empty(self):
        self.__init__()

     def isEmpty(self):
         return self.items == []

     def push(self, item):
         self.items.append(item)

     def pop(self):
         return self.items.pop()

     def peek(self):
         return self.items[len(self.items)-1]

     def size(self):
         return len(self.items)


class DwgXchFile:
    def __init__(self):
        self.location = None
        self.entities = []
        self.new_entities = []
        self.layers = []
        self.shapes = []
        self.patch_list = []
        self.new_patch_list = []

    def load(self, fname, flayers, fshapes):
        self.location = fname
        self.layers = flayers
        self.shapes = fshapes
        dwg_in = dxfgrabber.readfile(fname)
        for l in range(len(self.layers)):
            all_layer_cont = [entity for entity in dwg_in.entities if entity.layer == self.layers[l]]
            if self.shapes[l] == 'POLYLINE':
                for entity in all_layer_cont:
                    if not(entity.points[0] == entity.points[-1]):
                        entity.points.append(entity.points[0])
            self.entities.append(all_layer_cont)

        for l in range(len(self.layers)):
            if self.layers[l] == 'ALIGN':
                for entity in self.entities[l]:
                    codes = [Path.MOVETO] + [Path.LINETO for i in range(len(entity.points)-2)] +[Path.CLOSEPOLY]
                    path = Path([p[:-1] for p in entity.points], codes)
                    self.patch_list.append(patches.PathPatch(path, fill=False, color = 'c'))
            elif self.layers[l] == 'COORD':
                for entity in self.entities[l]:
                    self.patch_list.append(patches.Circle(entity.center[:-1],entity.radius, fill=False, color = 'g'))
            elif self.layers[l] == 'MAGNET':
                for entity in self.entities[l]:
                    codes = [Path.MOVETO] + [Path.LINETO for i in range(len(entity.points)-2)] +[Path.CLOSEPOLY]
                    path = Path([p[:-1] for p in entity.points], codes)
                    self.patch_list.append(patches.PathPatch(path, fill=False, color = 'r'))

    def add(self, magnet_name, pos):
        dwg_mag = dxfgrabber.readfile('C:/DOCS/Python/MyPy/dxf/' + magnet_name + '.dxf')
        all_layer_cont = [entity for entity in dwg_mag.entities if entity.layer == 'MAGNET']
        for entity in all_layer_cont:
            entity.points = [(pt[0]+470+pos[0],pt[1]+470+pos[1]) for pt in entity.points]
            if not(entity.points[0] == entity.points[-1]):
                entity.points.append(entity.points[0])
        self.new_entities.append(all_layer_cont)
        added_patches = []
        for entity in self.new_entities[-1]:
            codes = [Path.MOVETO] + [Path.LINETO for i in range(len(entity.points)-2)] +[Path.CLOSEPOLY]
            path = Path(entity.points, codes)
            added_patches.append(patches.PathPatch(path, fill=False, color = 'y'))
        self.new_patch_list.append(added_patches)

    def remove_last(self):
        self.new_entities.pop()
        self.new_patch_list.pop()

    def save(self, fname):
        dwg_out = dxf.drawing(fname)
        for ind, layer in enumerate(self.layers):
            dwg_out.add_layer(layer, color=ind+1)
        for align in self.entities[0]:
            pline = dxf.polyline(align.points, color=256, layer='ALIGN')
            pline.close()
            dwg_out.add(pline)
        for coord in self.entities[1]:
            dwg_out.add(dxf.circle(coord.radius, coord.center, color=256, layer='COORD'))
        for mag in self.entities[2]:
            pline = dxf.polyline(mag.points, color=256, layer='MAGNET')
            pline.close()
            dwg_out.add(pline)
        for mag in flatten_list(self.new_entities):
            pline = dxf.polyline(mag.points, color=256, layer='MAGNET')
            pline.close()
            dwg_out.add(pline)
        dwg_out.save()


####################
### Plot Classes ###
####################
class MyMplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""

    def __init__(self, parent=None, width=4, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        self.compute_initial_figure()

        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QtWidgets.QSizePolicy.Expanding,
                                   QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)


class ColorPlot(MyMplCanvas):
    """A canvas that updates itself every second with a new plot."""

    def __init__(self, *args, **kwargs):
        MyMplCanvas.__init__(self, *args, **kwargs)

    def compute_initial_figure(self):
        self.graph = []
        self.select_coord = []
        self.select_nv = []
        self.dxf_objects = []
        self.cts_xy = np.random.random((100,100))
        self.x_axis = np.arange(0,10,0.1)
        self.y_axis = np.arange(0,10,0.1)
        self.x_lim = [0,10]
        self.y_lim = [0,10]
        self.cts_vmin = 0
        self.cts_vmax = 10
        self.axes.imshow(self.cts_xy, extent=(self.x_axis[0], self.x_axis[-1], self.y_axis[0], self.y_axis[-1]),
                         cmap=tum_jet.tum_jet, vmin = self.cts_vmin, vmax = self.cts_vmax)

    def load_mat(self, filename):
        self.graph = scipy.io.loadmat(filename)
        self.select_coord = []
        self.select_nv = []
        if 'result_sec_chan' in self.graph.keys():
            self.cts_xy = np.reshape(2*self.graph['result_sec_chan'].ravel()-self.graph['result'].ravel(),(len(self.graph['result']),len(self.graph['result'])))
        else:
            self.cts_xy = self.graph['result']
        self.x_axis = self.graph['x'][0]
        self.y_axis = self.graph['y'][0]
        self.axes.cla()
        self.axes.imshow(self.cts_xy, extent=(self.x_axis[0], self.x_axis[-1],
                     self.y_axis[0], self.y_axis[-1]), cmap=tum_jet.tum_jet, vmin = self.cts_vmin, vmax = self.cts_vmax)
        self.draw()

    def draw_dxf(self):
        self.axes.cla()
        if len(self.cts_xy):
            self.axes.imshow(self.cts_xy, extent=(self.x_axis[0], self.x_axis[-1], self.y_axis[0], self.y_axis[-1]),
                         cmap=tum_jet.tum_jet, vmin = self.cts_vmin, vmax = self.cts_vmax)
        if len(self.dxf_objects):
            for patch in self.dxf_objects:
                self.axes.add_patch(patch)
        if len(self.select_coord):
            self.axes.plot([pt[0] for pt in self.select_coord], [pt[1] for pt in self.select_coord], ls = 'None', marker = 'o', markerfacecolor = 'None', markeredgecolor = 'r')
        if len(self.select_nv):
            for patch in self.select_nv:
                self.axes.add_patch(patch)
        self.axes.set_xlim(self.x_lim[0], self.x_lim[-1])
        self.axes.set_ylim(self.y_lim[0], self.y_lim[-1])
        self.draw()

    def redraw(self, **kwargs):
        self.cts_vmin = kwargs.get('cts_vmin', self.cts_vmin)
        self.cts_vmax = kwargs.get('cts_vmax', self.cts_vmax)
        self.select_coord = kwargs.get('scatter', self.select_coord)
        self.select_nv = kwargs.get('sel_scatter', self.select_nv)
        self.axes.cla()
        self.axes.imshow(self.cts_xy, extent=(self.x_axis[0], self.x_axis[-1],
                     self.y_axis[0], self.y_axis[-1]), cmap=tum_jet.tum_jet, vmin = self.cts_vmin, vmax = self.cts_vmax)
        if len(self.select_coord):
            self.axes.plot([pt[0] for pt in self.select_coord], [pt[1] for pt in self.select_coord], ls = 'None', marker = 'o', markerfacecolor = 'None', markeredgecolor = 'k')
        if len(self.select_nv):
            self.axes.plot([pt[0] for pt in self.select_nv], [pt[1] for pt in self.select_nv], ls = 'None', marker = 'o', markerfacecolor = 'r', markeredgecolor = 'w')
        self.draw()

    def save(self, fname):
        self.fig.savefig(fname)


###################
### Main Window ###
###################

class MainWindow(QtWidgets.QMainWindow):
    count = 0 #number of opened windows
    nvloc_isopen = False #status of NV Localiser widget
#    log_isopen = False #status of NV Localiser widget

    def __init__(self, parent = None):
        super(MainWindow, self).__init__(parent)

        self.mdi = QtWidgets.QMdiArea() #create multiple document interface widget
        self.setCentralWidget(self.mdi)

        self.bar = self.menuBar()

        task = self.bar.addMenu("Task")  #menu with different tasks (fitting, finding NVs,...)
        task.addAction("NV Localiser")
        task.triggered[QtWidgets.QAction].connect(self.task_windowaction)

        file = self.bar.addMenu("File") #menu with file tasks (open, load, close, new,...) Currently dummy
        file.addAction("New")
        file.addAction("Cascade")
        file.addAction("Tiled")
        file.triggered[QtWidgets.QAction].connect(self.file_windowaction)

        self.setWindowTitle("%s %s" % (progname,progversion))

#        MainWindow.log_isopen = True
#        self.log_widget = QtWidgets.QMdiSubWindow()
#        self.log_widget.setWidget(Logger(self))
#        self.log_widget.setWindowTitle("Logger")
#        self.log_widget.setObjectName('WIN_LOG')
#        self.mdi.addSubWindow(self.log_widget)
#        self.log_widget.show()


    def task_windowaction(self, q): #executes when task menu item selected

        if q.text() == "NV Localiser":
            if MainWindow.nvloc_isopen == False: #no nvloc window yet
                MainWindow.count = MainWindow.count+2
                MainWindow.nvloc_isopen = True

                self.nvloc_widget = QtWidgets.QMdiSubWindow()
                self.nvloc_widget.setWidget(NVLocaliser(self))
                self.nvloc_widget.setWindowTitle("NV Localiser")
                self.nvloc_widget.setObjectName('WIN_NVLOC')
                self.mdi.addSubWindow(self.nvloc_widget)
                self.nvloc_widget.show()

            else:
                pass

        else:
            pass


    def file_windowaction(self, q): #executes when file menu item selected

        if q.text() == "New":
            MainWindow.count = MainWindow.count+1
            sub = QtWidgets.QMdiSubWindow()
            sub.setWidget(QtWidgets.QTextEdit())
            sub.setWindowTitle("subwindow"+str(MainWindow.count))
            self.mdi.addSubWindow(sub)
            sub.show()

        elif q.text() == "Cascade":
            self.mdi.cascadeSubWindows()

        elif q.text() == "Tiled":
            self.mdi.tileSubWindows()

        else:
            pass


###############
#### Logger ###
###############
#
#class Logger(QtWidgets.QWidget):
#
#    def __init__(self, parent = None):
#        super(Logger, self).__init__(parent)
#
#        self.edt_log = QtWidgets.QTextEdit('Log: \n', self)
#        self.save_btn = QtWidgets.QPushButton('Save', self)
#        self.save_btn.setToolTip('Save log file')
#        self.save_btn.setObjectName('-1')
#        self.save_btn.clicked.connect(self.save_log)
#        self.save_btn.resize(self.save_btn.sizeHint())
#
#        main_vbox = QtWidgets.QVBoxLayout(self)
#        main_vbox.setSpacing(10)
#        main_vbox.addWidget(self.edt_log)
#        main_vbox.addWidget(self.save_btn)
#
#    def save_log(self):
#        fname = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File', 'C:\\DATA\\NV Characterisation\\Registration',"Text files (*.txt)")[0]
#        if not fname.endswith('.txt'):
#            fname += ".txt"
#        file = open(fname,'w')
#        file.write(self.edt_log.toPlainText())
#        file.close()


####################
### NV Localiser ###
####################

class NVLocaliser(QtWidgets.QWidget):

    def __init__(self, parent = None):
        super(NVLocaliser, self).__init__(parent)

        self.raw_buffer = Stack()
        self.dxf_buffer = Stack()

        self.dxf_loaded = False
        self.raw_loaded = False
        self.nv_select_mode = False

        self.local_menu = self.parent().bar.addMenu("NV Localiser")  #menu with different tasks (fitting, finding NVs,...)
        self.local_menu.addAction("Load *.mat")
        self.local_menu.addAction("Load *.dxf")
        self.local_menu.addAction("New *.dxf")
        self.local_menu.triggered[QtWidgets.QAction].connect(self.local_menu_windowaction)

        self.setGeometry(300, 300, 300, 220)
        self.raw_img = ColorPlot(self, width=4, height=4, dpi=100)
        self.raw_img.mpl_connect('button_release_event', self.raw_mouse_released)
        self.dxf_img = ColorPlot(self, width=4, height=4, dpi=100)
        self.dxf_img.mpl_connect('scroll_event', self.zoom_dxf)
        self.dxf_img.mpl_connect('button_release_event', self.dxf_mouse_released)

        self.bwd_btn = QtWidgets.QPushButton('<< Last', self)
        self.bwd_btn.setToolTip('Load previous image')
        self.bwd_btn.setObjectName('-1')
        self.bwd_btn.clicked.connect(self.file_crawl)
        self.bwd_btn.resize(self.bwd_btn.sizeHint())
        self.fwd_btn = QtWidgets.QPushButton('Next >>', self)
        self.fwd_btn.setToolTip('Load next image')
        self.fwd_btn.setObjectName('1')
        self.fwd_btn.clicked.connect(self.file_crawl)
        self.fwd_btn.resize(self.fwd_btn.sizeHint())
        self.edt_curr_file = QtWidgets.QLineEdit('n/a', self)
        self.edt_curr_file.setReadOnly(True)
        self.lbl_max = QtWidgets.QLabel('Max. Cts.:', self)
        self.edt_max = QtWidgets.QLineEdit('5e5', self)
        self.edt_max.returnPressed.connect(self.changeCts)
        self.lbl_min = QtWidgets.QLabel('Min. Cts.:', self)
        self.edt_min = QtWidgets.QLineEdit('3e4', self)
        self.edt_min.returnPressed.connect(self.changeCts)
        self.magnets_cb = QtWidgets.QComboBox()
#        self.magnets_cb.addItems(['windmill_s', 'mercedes_s', 'sierpinski_s', 'hazard_s', 'hazard2_s', 'holey_s', 'flag_s', 'cross_s',
#                          'mitsubishi_s', 'windmill_b', 'mercedes_b', 'hazard_b', 'hazard2_b', 'holey_b', 'flag_b', 'cross_b',
#                          'mitsubishi_b'])
#        self.magnets_cb.addItems(['mitsubishi_b', 'windmill_b', 'hazard_b'])#, 'nuclear_b', 'nuclear2_b'])
#        self.magnets_cb.addItems(['mitsubishi_xp', 'mitsubishi_xm', 'mitsubishi_yp', 'mitsubishi_ym', 'windmill_xp', 'windmill_xm', 'windmill_yp', 'windmill_ym'])
        self.magnets_cb.addItems(['mitsubishi5','windmill_5B1','mitsubishi5xp', 'mitsubishi5xm', 'mitsubishi5yp', 'mitsubishi5ym', 'windmill5xp', 'windmill5xm', 'windmill5yp', 'windmill5ym'])
        self.trafo_btn = QtWidgets.QPushButton('Transform', self)
        self.trafo_btn.setToolTip('Transform raw image into coordinate system')
        self.trafo_btn.clicked.connect(self.trafo)
        self.trafo_btn.resize(self.trafo_btn.sizeHint())
        self.save_dxf_btn = QtWidgets.QPushButton('Save dxf', self)
        self.save_dxf_btn.setToolTip('Add selection to dxf')
        self.save_dxf_btn.clicked.connect(self.save_dxf)
        self.save_dxf_btn.resize(self.save_dxf_btn.sizeHint())
        self.save_png_btn = QtWidgets.QPushButton('Save png', self)
        self.save_png_btn.setToolTip('Save current view as image')
        self.save_png_btn.clicked.connect(self.save_png)
        self.save_png_btn.resize(self.save_png_btn.sizeHint())
        self.overwrite_cb = QtWidgets.QCheckBox('Overwrite dxf', self)
        self.overwrite_cb.setChecked(False)

        hbox = QtWidgets.QHBoxLayout()
        hbox.setSpacing(30)
        hbox.addWidget(self.raw_img)
        hbox.addWidget(self.dxf_img)

        hbox1 = QtWidgets.QHBoxLayout()
        hbox1.setSpacing(10)
        hbox1.addWidget(self.bwd_btn)
        hbox1.addWidget(self.fwd_btn)
        hbox1.addStretch(5)
        hbox1.addWidget(self.magnets_cb)
        hbox1.addStretch(1)
        hbox1.addWidget(self.trafo_btn)
        hbox1.addWidget(self.save_dxf_btn)
        hbox1.addWidget(self.save_png_btn)

        hbox2 = QtWidgets.QHBoxLayout()
        hbox2.setSpacing(10)
        hbox2.addWidget(self.edt_curr_file)
        hbox2.addStretch(1)
        hbox2.addWidget(self.lbl_max)
        hbox2.addWidget(self.edt_max)
        hbox2.addWidget(self.lbl_min)
        hbox2.addWidget(self.edt_min)
        hbox2.addStretch(5)
        hbox2.addWidget(self.overwrite_cb)

        main_vbox = QtWidgets.QVBoxLayout(self)
        main_vbox.setSpacing(10)
        main_vbox.addLayout(hbox)
        main_vbox.addLayout(hbox1)
        main_vbox.addLayout(hbox2)

    def local_menu_windowaction(self, q): #executes when file menu item selected

        if q.text() == "Load *.mat":
            self.load_raw()

        elif q.text() == "Load *.dxf":
            fname = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', 'C:\\DATA\\NV Characterisation\\Registration',"Drawing interchange files (*.dxf)")[0]
            self.load_dxf(fname)

        elif q.text() == "New *.dxf":
#            fname = 'C:/DOCS/Python/MyPy/dxf/coords.dxf'
            fname = 'C:/DOCS/Python/MyPy/dxf/coords_new.dxf'
            self.load_dxf(fname)

        else:
            pass

    def load_raw(self):
        self.dir_name = QtWidgets.QFileDialog.getExistingDirectory(self, 'Open folder', 'C:\\DATA\\NV Characterisation\\Registration')
        self.dir_content = [f for f in os.listdir(self.dir_name) if (f.startswith('scan') or f.startswith('field')) and f.endswith('.mat')]
#        self.dir_content = [f for f in os.listdir(self.dir_name) if (f.startswith('field') and f.endswith('.mat'))]
        try:
            self.raw_img.load_mat(os.path.join(self.dir_name,self.dir_content[0]))
            self.changeCts()
            self.edt_curr_file.setText(self.dir_content[0])
            self.raw_loaded = True
        except:
            pass

    def file_crawl(self):
        up_down = self.sender()
        if self.raw_loaded:
            if (self.dir_content.index(self.edt_curr_file.text()) == 0 and int(up_down.objectName()) == -1) or (self.dir_content.index(self.edt_curr_file.text()) == len(self.dir_content)-1 and int(up_down.objectName()) == 1):
                pass
            else:
                self.edt_curr_file.setText(self.dir_content[self.dir_content.index(self.edt_curr_file.text()) + int(up_down.objectName())])
                self.raw_img.load_mat(os.path.join(self.dir_name,self.edt_curr_file.text()))
                self.raw_img.select_coord=[]
                self.raw_buffer.empty()
                if self.dxf_loaded:
                    self.dxf_img.select_coord=[]
                    self.dxf_buffer.empty()
                    self.dxf_img.cts_xy = []
                    self.dxf_img.draw_dxf()
                self.nv_select_mode = False
        else:
            pass

    def raw_mouse_released(self, event):
        if any([event.xdata, event.ydata]):
            if event.button == 1:

                x_ax = self.raw_img.x_axis
                y_ax = self.raw_img.y_axis[::-1]
                x_ax, y_ax = np.meshgrid(x_ax, y_ax)

                initial_guess = (self.raw_img.cts_vmax, event.xdata, event.ydata, 0.2, min(self.raw_img.cts_xy.ravel()))# self.raw_img.cts_vmax/2) # amplitude, x0, y0, sigma, offset
                param_bounds = ([0,event.xdata-1,event.ydata-1,0,-np.inf],[np.inf,event.xdata+1,event.ydata+1,np.inf,np.inf])
                popt, pcov = opt.curve_fit(twoD_Gaussian_sym, [x_ax,y_ax], self.raw_img.cts_xy.ravel(), p0 = initial_guess, bounds = param_bounds)
                print(str(popt))
                print(str(np.sqrt(pcov[1,1]**2 + pcov[2,2]**2)))
                self.raw_buffer.push([popt[1],popt[2]])
                if self.nv_select_mode == False:
                    self.raw_img.select_coord.append([popt[1],popt[2]])
                else:
                    self.raw_img.select_nv.append([popt[1],popt[2]])
                    trafo_coords =  np.dot(np.array([self.raw_img.select_nv[-1][0], self.raw_img.select_nv[-1][1], 1]), self.trafo_matrix)[:-1]
                    self.dxf_in.add(self.magnets_cb.currentText(), trafo_coords)
                    self.dxf_img.select_nv = flatten_list(self.dxf_in.new_patch_list)
                    self.dxf_img.draw_dxf()
                self.raw_img.redraw()
            if event.button == 2: #manually select point by pressing wheel
                self.raw_buffer.push([event.xdata, event.ydata])
                if self.nv_select_mode == False:
                    self.raw_img.select_coord.append([event.xdata, event.ydata])
                else:
                    self.raw_img.select_nv.append([event.xdata, event.ydata])
                    trafo_coords =  np.dot(np.array([self.raw_img.select_nv[-1][0], self.raw_img.select_nv[-1][1], 1]), self.trafo_matrix)[:-1]
                    self.dxf_in.add(self.magnets_cb.currentText(), trafo_coords)
                    self.dxf_img.select_nv = flatten_list(self.dxf_in.new_patch_list)
                    self.dxf_img.draw_dxf()
                self.raw_img.redraw()
            if (event.button == 3 and not self.raw_buffer.isEmpty()):
                x,y = self.raw_buffer.pop()
                if self.nv_select_mode == False:
                    self.raw_img.select_coord.pop()
                else:
                    self.raw_img.select_nv.pop()
                    self.dxf_in.remove_last()
                    self.dxf_img.select_nv = flatten_list(self.dxf_in.new_patch_list)
                    self.dxf_img.draw_dxf()
                self.raw_img.redraw()

    def trafo(self):
        if (len(self.raw_img.select_coord) == len(self.dxf_img.select_coord) and len(self.raw_img.select_coord) >= 3):
            self.trafo_matrix = affine_trafo(self.raw_img.select_coord, self.dxf_img.select_coord)
            if np.trace(self.trafo_matrix) < 2.85:
                print(str(self.trafo_matrix))
            elif len(self.trafo_matrix):
                print(str(self.trafo_matrix))
                x_ax = self.raw_img.x_axis
                y_ax = self.raw_img.y_axis[::-1]
                x_ax, y_ax = np.meshgrid(x_ax, y_ax)
                x_ax, y_ax, _ = np.dot(np.array([x_ax, y_ax, 1]), self.trafo_matrix)
                x_ax, y_ax = x_ax.ravel(), y_ax.ravel()

                nx, ny = 300, 300
                # Generate a regular grid to interpolate the data.
                xi = np.linspace(min(x_ax), max(x_ax), nx)
                yi = np.linspace(min(y_ax), max(y_ax), ny)
                xi, yi = np.meshgrid(xi, yi)
                # Interpolate using linear triangularization
                self.raw_img.cts_xy = self.raw_img.graph['result'] # when using LP580 technique, switch to full image at this point
                self.dxf_img.cts_xy = griddata((x_ax, y_ax), self.raw_img.cts_xy.ravel(), (xi, yi), method='linear',fill_value=min(self.raw_img.cts_xy.ravel()))[::-1]
#                self.raw_img.cts_xy = ctsi.filled(min(self.raw_img.cts_xy.ravel()))
                self.dxf_img.x_axis = xi[0]
                self.dxf_img.y_axis = yi.transpose()[0]
                self.dxf_img.cts_vmin = self.raw_img.cts_vmin
                self.dxf_img.cts_vmax = self.raw_img.cts_vmax
                self.dxf_img.select_coord=[]
                self.raw_img.select_coord=[]
                self.dxf_buffer.empty()
                self.raw_buffer.empty()
                self.dxf_img.draw_dxf()
#                self.raw_img.cts_xy = self.raw_img.graph['result'] # when using LP580 technique, switch to full image at this point
                self.raw_img.redraw()
                self.nv_select_mode = True
            else:
                pass
        else:
            pass

    def changeCts(self):
        try:
            self.raw_img.cts_vmin = float(self.edt_min.text())
            self.dxf_img.cts_vmin = float(self.edt_min.text())
        except:
            pass
        try:
            self.raw_img.cts_vmax = float(self.edt_max.text())
            self.dxf_img.cts_vmax = float(self.edt_max.text())
        except:
            pass
        self.raw_img.redraw()
        if len(self.dxf_img.cts_xy):
            self.dxf_img.draw_dxf()

    def load_dxf(self, fname):
        self.dxf_in = DwgXchFile()
        self.dxf_in.load(fname, ['ALIGN', 'COORD', 'MAGNET'], ['POLYLINE', 'CIRCLE', 'POLYLINE'])
        self.dxf_img.x_lim = np.array([0,100])
        self.dxf_img.y_lim = np.array([0,100])
        self.dxf_img.cts_xy = []
        self.dxf_img.dxf_objects = self.dxf_in.patch_list
        self.dxf_img.draw_dxf()
        self.dxf_loaded = True

    def save_dxf(self):
        if self.overwrite_cb.isChecked() == False:
            fname = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File', 'C:\\DATA\\NV Characterisation\\Registration',"Drawing interchange files (*.dxf)")[0]
            if not fname.endswith('.dxf'):
                fname += ".dxf"
        elif self.overwrite_cb.isChecked() == True:
            fname = self.dxf_in.location
        else:
            print('Checkbox isn\'t working')
            fname = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File', 'C:\\DATA\\NV Characterisation\\Registration',"Drawing interchange files (*.dxf)")[0]
            if not fname.endswith('.dxf'):
                fname += ".dxf"
        self.dxf_in.save(fname)

        self.dxf_img.select_nv=[]
        self.dxf_buffer.empty()
        self.load_dxf(fname)

        self.raw_img.select_nv=[]
        self.raw_buffer.empty()
        self.raw_img.redraw()

    def zoom_dxf(self, event):
        if self.dxf_loaded:
            if event.button == 'up':
                self.dxf_img.x_lim = np.array([(self.dxf_img.x_lim[0]-event.xdata)/1.2+event.xdata,(self.dxf_img.x_lim[1]-event.xdata)/1.2+event.xdata])
                self.dxf_img.y_lim = np.array([(self.dxf_img.y_lim[0]-event.ydata)/1.2+event.ydata,(self.dxf_img.y_lim[1]-event.ydata)/1.2+event.ydata])
            elif event.button == 'down':
                self.dxf_img.x_lim = np.array([(self.dxf_img.x_lim[0]-event.xdata)*1.2+event.xdata,(self.dxf_img.x_lim[1]-event.xdata)*1.2+event.xdata])
                self.dxf_img.y_lim = np.array([(self.dxf_img.y_lim[0]-event.ydata)*1.2+event.ydata,(self.dxf_img.y_lim[1]-event.ydata)*1.2+event.ydata])
            self.dxf_img.draw_dxf()
        else:
            print('you are at ', event.xdata, event.ydata, 'and something went wrong')

    def dxf_mouse_released(self, event):
        if any([event.xdata, event.ydata]):
            if event.button == 1:
                x,y = event.xdata, event.ydata
                if self.nv_select_mode == False:
                    all_COORD_ctr = [entity.center[:-1] for entity in self.dxf_in.entities[1]] # centres of coordinate points (list [1] in entities)
                    ds = [np.sqrt((x-coord[0])**2+(y-coord[1])**2) for coord in all_COORD_ctr]
                    if min(ds) < 0.3:
                        print(str(all_COORD_ctr[ds.index(min(ds))]))
                        self.dxf_buffer.push(all_COORD_ctr[ds.index(min(ds))])
                        self.dxf_img.select_coord.append(all_COORD_ctr[ds.index(min(ds))])
                        self.dxf_img.draw_dxf()
                else:
                    pass
            if (event.button == 3 and not self.dxf_buffer.isEmpty()):
                if self.nv_select_mode == False:
                    x,y = self.dxf_buffer.pop()
                    self.dxf_img.select_coord.pop()
                    self.dxf_img.draw_dxf()
                else:
                    pass

    def save_png(self):
        fname = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File', 'C:\\DATA\\NV Characterisation\\Registration',"Portable network graphics (*.png)")[0]
        if not fname.endswith('.png'):
            fname += ".png"
        self.dxf_img.save(fname)


#    close subwindow and remove menu entry - not working yet!
#    def closeEvent(self, event):
#        self.parent().bar.removeAction(self.local_menu.menuAction())
#        event.accept() # let the window close




#####################
### start program ###
#####################

def main():
    app = QtWidgets.QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__': #runs only if file is executed, not when it's imported
    main()
