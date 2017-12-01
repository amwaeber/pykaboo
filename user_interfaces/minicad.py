import os

import numpy as np
from PyQt5 import QtWidgets, QtGui

from helper_classes.dwg_xch_file import DwgXchFile
from helper_classes.stack import Stack
from plot_classes.color_plot import ColorPlot
from utility.config import paths


# noinspection PyAttributeOutsideInit
class MiniCAD(QtWidgets.QWidget):
    def __init__(self, logger, parent=None):
        super(MiniCAD, self).__init__(parent)
        self.logger = logger

        self.point_buffer = Stack()

        self.dxf_loaded = False
        self.mode = -1  # object selection mode

        self.local_menu = self.parent().bar.addMenu("MiniCAD")
        self.local_menu.addAction("Load *.dxf")
        self.local_menu.addAction("Save *.dxf")
        self.local_menu.addAction("Save *.png")
        self.local_menu.triggered[QtWidgets.QAction].connect(self.local_menu_windowaction)

        self.dxf_img = ColorPlot(self, width=4, height=4, dpi=100)
        self.dxf_img.mpl_connect('scroll_event', self.zoom_dxf)
        self.dxf_img.mpl_connect('button_release_event', self.dxf_mouse_released)

        self.color_btn = QtWidgets.QPushButton(self)
        self.color_btn.setStyleSheet("background-color: gray")
        self.color_btn.setIcon(QtGui.QIcon(os.path.join(paths['icons'], 'palette.png')))
        self.color_btn.setToolTip('Select color')
        self.color_btn.clicked.connect(self.select_color)
        self.color_btn.resize(self.color_btn.sizeHint())
        self.color_mode_btn = QtWidgets.QPushButton(self)
        self.color_mode_btn.setIcon(QtGui.QIcon(os.path.join(paths['icons'], 'brush.png')))
        self.color_mode_btn.setToolTip('Assign color to selected object')
        self.color_mode_btn.clicked.connect(lambda: self.set_mode('mark'))
        self.color_mode_btn.resize(self.color_mode_btn.sizeHint())
        self.measure_mode_btn = QtWidgets.QPushButton(self)
        self.measure_mode_btn.setIcon(QtGui.QIcon(os.path.join(paths['icons'], 'ruler.png')))
        self.measure_mode_btn.setToolTip('measure distance between selected objects')
        self.measure_mode_btn.clicked.connect(lambda: self.set_mode('measure'))
        self.measure_mode_btn.resize(self.measure_mode_btn.sizeHint())
        self.label_mode_btn = QtWidgets.QPushButton(self)
        self.label_mode_btn.setIcon(QtGui.QIcon(os.path.join(paths['icons'], 'text.png')))
        self.label_mode_btn.setToolTip('Label selected object')
        self.label_mode_btn.clicked.connect(lambda: self.set_mode('label'))
        self.label_mode_btn.resize(self.label_mode_btn.sizeHint())
        self.edt_text_label = QtWidgets.QLineEdit('00', self)

        self.load_dxf_btn = QtWidgets.QPushButton(self)
        self.load_dxf_btn.setIcon(QtGui.QIcon(os.path.join(paths['icons'], 'load.png')))
        self.load_dxf_btn.setToolTip('Load dxf file')
        self.load_dxf_btn.clicked.connect(lambda: self.load_dxf(update=False))  # add proper file management
        self.load_dxf_btn.resize(self.load_dxf_btn.sizeHint())
        self.save_dxf_btn = QtWidgets.QPushButton(self)
        self.save_dxf_btn.setIcon(QtGui.QIcon(os.path.join(paths['icons'], 'save.png')))
        self.save_dxf_btn.setToolTip('Save dxf file')
        self.save_dxf_btn.clicked.connect(self.save_dxf)
        self.save_dxf_btn.resize(self.save_dxf_btn.sizeHint())
        self.save_png_btn = QtWidgets.QPushButton(self)
        self.save_png_btn.setIcon(QtGui.QIcon(os.path.join(paths['icons'], 'save_img.png')))
        self.save_png_btn.setToolTip('Save current view as image')
        self.save_png_btn.clicked.connect(self.save_png)
        self.save_png_btn.resize(self.save_png_btn.sizeHint())

        hbox = QtWidgets.QHBoxLayout()
        hbox.setSpacing(10)
        hbox.addWidget(self.color_btn)
        hbox.addWidget(self.color_mode_btn)
        hbox.addWidget(self.measure_mode_btn)
        hbox.addWidget(self.label_mode_btn)
        hbox.addWidget(self.edt_text_label)
        hbox.addStretch(5)
        hbox.addWidget(self.load_dxf_btn)
        hbox.addWidget(self.save_dxf_btn)
        hbox.addWidget(self.save_png_btn)

        main_vbox = QtWidgets.QVBoxLayout(self)
        main_vbox.setSpacing(10)
        main_vbox.addWidget(self.dxf_img)
        main_vbox.addLayout(hbox)

        self.logger.add_to_log('Started MiniCAD.')

    def local_menu_windowaction(self, q):  # executes when file menu item selected
        if q.text() == "Load *.dxf":
            self.load_dxf()
        elif q.text() == "Save *.dxf":
            self.save_dxf()
        elif q.text() == "Save *.png":
            self.save_png()

    def select_color(self):
        color = QtWidgets.QColorDialog.getColor()
        self.color_btn.setStyleSheet("background-color: %s" % color.name())

    def set_mode(self, select_mode='none'):
        modes = {'none': -1,
                 'mark': 0,
                 'measure': 1,
                 'label': 2}
        self.mode = modes[select_mode]

    def load_dxf(self, update=False):
        if not update:
            fname = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', paths['registration'],
                                                          "Drawing interchange files (*.dxf)")[0]
            if not fname:  # capture cancel in dialog
                return
            self.logger.add_to_log('Loaded .dxf file ' + fname)
        else:
            fname = self.dxf_in.location
        self.dxf_in = DwgXchFile()
        self.dxf_in.load(fname, ['ALIGN', 'COORD', 'MAGNET'], ['POLYLINE', 'CIRCLE', 'POLYLINE'])
        self.dxf_img.x_lim = np.array([0, 100])
        self.dxf_img.y_lim = np.array([0, 100])
        self.dxf_img.cts_xy = []
        self.dxf_img.dxf_objects = self.dxf_in.patch_list
        self.dxf_img.draw_dxf()
        self.dxf_loaded = True

    def save_dxf(self):
        if self.dxf_loaded:
            fname = self.dxf_in.location
            self.dxf_in.save(fname)
            self.logger.add_to_log('Saved .dxf file.')

            self.dxf_img.select_nv = []
            self.point_buffer.empty()
            self.load_dxf(update=True)

    def save_png(self):
        fname = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File', paths['registration'],
                                                      "Portable network graphics (*.png)")[0]
        if not fname:  # capture cancel in dialog
            return
        elif not fname.endswith('.png'):
            fname += ".png"
        self.dxf_img.save(fname)

    def zoom_dxf(self, event):
        if self.dxf_loaded:
            if event.button == 'up':
                self.dxf_img.x_lim = np.array([(self.dxf_img.x_lim[0] - event.xdata) / 1.2 + event.xdata,
                                               (self.dxf_img.x_lim[1] - event.xdata) / 1.2 + event.xdata])
                self.dxf_img.y_lim = np.array([(self.dxf_img.y_lim[0] - event.ydata) / 1.2 + event.ydata,
                                               (self.dxf_img.y_lim[1] - event.ydata) / 1.2 + event.ydata])
            elif event.button == 'down':
                self.dxf_img.x_lim = np.array([(self.dxf_img.x_lim[0] - event.xdata) * 1.2 + event.xdata,
                                               (self.dxf_img.x_lim[1] - event.xdata) * 1.2 + event.xdata])
                self.dxf_img.y_lim = np.array([(self.dxf_img.y_lim[0] - event.ydata) * 1.2 + event.ydata,
                                               (self.dxf_img.y_lim[1] - event.ydata) * 1.2 + event.ydata])
            self.dxf_img.draw_dxf()

    def dxf_mouse_released(self, event):
        if any([event.xdata, event.ydata]) and self.dxf_loaded:
            if event.button == 1:
                x, y = event.xdata, event.ydata
                if not self.nv_select_mode:
                    all_coord_ctr = [entity.center[:-1] for entity in
                                     self.dxf_in.entities[1]]  # centres of coordinate points (list [1] in entities)
                    ds = [np.sqrt((x - coord[0]) ** 2 + (y - coord[1]) ** 2) for coord in all_coord_ctr]
                    if min(ds) < 0.3:
                        self.point_buffer.push(all_coord_ctr[ds.index(min(ds))])
                        self.dxf_img.select_coord.append(all_coord_ctr[ds.index(min(ds))])
                        self.dxf_img.draw_dxf()
            if event.button == 3 and not self.point_buffer.is_empty():
                if not self.nv_select_mode:
                    x, y = self.point_buffer.pop()
                    self.dxf_img.select_coord.pop()
                    self.dxf_img.draw_dxf()

