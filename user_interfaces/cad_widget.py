import copy
import numpy as np
import os
from PyQt5 import QtWidgets, QtGui, QtCore

from plot_classes.color_plot import ColorPlot
from helper_classes.dwg_xch_file import DwgXchFile
from helper_classes.stack import Stack
from utility.config import paths
from utility.utility_functions import affine_trafo, kd_nearest
from user_interfaces.grid_dialog import GridDialog
from user_interfaces.props_dialog import PropsDialog
from user_interfaces.stencil_dialog import StencilDialog


# noinspection PyAttributeOutsideInit
# noinspection PyArgumentList
class CADWidget(QtWidgets.QWidget):
    def __init__(self, action, window_number, logger, parent=None):
        super(CADWidget, self).__init__(parent)
        self.window_number = window_number
        self.logger = logger
        self.grid = [False, 1, 0.1]
        self.pick_stack = Stack()
        self.object_stack = Stack()
        self.stencil = None
        self.layer = None
        self.mode = 'pick_pt'
        self.mat = None

        draw_line_btn = QtWidgets.QAction(QtGui.QIcon(os.path.join(paths['icons'], 'line.png')),
                                          'Line tool', self)
        draw_line_btn.triggered.connect(self.draw_line)
        draw_rectangle_btn = QtWidgets.QAction(QtGui.QIcon(os.path.join(paths['icons'], 'rectangle.png')),
                                               'Rectangle tool', self)
        draw_rectangle_btn.triggered.connect(self.draw_rectangle)
        draw_circle_btn = QtWidgets.QAction(QtGui.QIcon(os.path.join(paths['icons'], 'circle.png')),
                                            'Circle tool', self)
        draw_circle_btn.triggered.connect(self.draw_circle)
        draw_polyline_btn = QtWidgets.QAction(QtGui.QIcon(os.path.join(paths['icons'], 'polyline.png')),
                                              'Polyline tool', self)
        draw_polyline_btn.triggered.connect(self.draw_polyline)
        text_btn = QtWidgets.QAction(QtGui.QIcon(os.path.join(paths['icons'], 'text.png')),
                                     'Add text', self)
        text_btn.triggered.connect(self.add_text)
        stencil_btn = QtWidgets.QAction(QtGui.QIcon(os.path.join(paths['icons'], 'stencil.png')),
                                        'Stencil tool', self)
        stencil_btn.triggered.connect(self.use_stencil)
        pick_btn = QtWidgets.QAction(QtGui.QIcon(os.path.join(paths['icons'], 'pick.png')),
                                     'Pick object', self)
        pick_btn.triggered.connect(self.pick_point)
        grid_btn = QtWidgets.QAction(QtGui.QIcon(os.path.join(paths['icons'], 'grid.png')),
                                     'Show grid lines', self)
        grid_btn.triggered.connect(self.set_grid)
        measure_btn = QtWidgets.QAction(QtGui.QIcon(os.path.join(paths['icons'], 'measure.png')),
                                        'Measure', self)
        measure_btn.triggered.connect(self.measure)
        color_btn = QtWidgets.QAction(QtGui.QIcon(os.path.join(paths['icons'], 'palette.png')),
                                      'Select color', self)
        color_btn.triggered.connect(self.select_color)
        sel_stencil_btn = QtWidgets.QAction(QtGui.QIcon(os.path.join(paths['icons'], 'select_stencil.png')),
                                            'Select stencil', self)
        sel_stencil_btn.triggered.connect(self.select_stencil)
        properties_btn = QtWidgets.QAction(QtGui.QIcon(os.path.join(paths['icons'], 'properties.png')),
                                           'Set properties (layer, block)', self)
        properties_btn.triggered.connect(self.set_properties)
        view_btn = QtWidgets.QAction(QtGui.QIcon(os.path.join(paths['icons'], 'view.png')),
                                     'View properties', self)
        view_btn.triggered.connect(self.view_properties)
        transform_btn = QtWidgets.QAction(QtGui.QIcon(os.path.join(paths['icons'], 'transform.png')),
                                          'Transform', self)
        transform_btn.triggered.connect(self.transform)

        self.toolbar = QtWidgets.QToolBar("Draw")
        self.toolbar.addAction(draw_line_btn)
        self.toolbar.addAction(draw_rectangle_btn)
        self.toolbar.addAction(draw_circle_btn)
        self.toolbar.addAction(draw_polyline_btn)
        self.toolbar.addAction(text_btn)
        self.toolbar.addAction(stencil_btn)
        self.toolbar.addSeparator()
        self.toolbar.addAction(pick_btn)
        self.toolbar.addAction(grid_btn)
        self.toolbar.addAction(measure_btn)
        self.toolbar.addSeparator()
        self.toolbar.addAction(color_btn)
        self.toolbar.addAction(sel_stencil_btn)
        self.toolbar.addAction(properties_btn)
        self.toolbar.addAction(view_btn)
        self.toolbar.addSeparator()
        self.toolbar.addAction(transform_btn)

        self.canvas = ColorPlot(self)
        self.canvas.mpl_connect('scroll_event', self.mouse_wheel)
        self.canvas.mpl_connect('button_release_event', self.mouse_released)
        self.canvas.mpl_connect('motion_notify_event', self.mouse_moved)

        self.status_bar = QtWidgets.QStatusBar()

        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.toolbar)
        vbox.addWidget(self.canvas)
        vbox.addWidget(self.status_bar)
        self.setLayout(vbox)

        if action == "New":
            self.dxf_file = DwgXchFile()
            self.canvas.draw_canvas(dxf=self.dxf_file)
            self.logger.add_to_log("New dxf.")
        elif action == "Open":
            self.dxf_file = DwgXchFile()
            self.dxf_file.load(self, file_type='standard')
            self.canvas.draw_canvas(dxf=self.dxf_file)
            self.logger.add_to_log("Open dxf.")
        elif action == "Open Template":
            self.dxf_file = DwgXchFile()
            self.dxf_file.load(self, file_type='template')
            self.canvas.draw_canvas(dxf=self.dxf_file)
            self.logger.add_to_log("Open Template.")

    def draw_line(self):
        pass

    def draw_rectangle(self):
        pass

    def draw_circle(self):
        pass

    def draw_polyline(self):
        pass

    def add_text(self):
        pass

    def use_stencil(self):
        if not self.stencil:  # if no stencil has been selected yet, open dialog first
            self.stencil = StencilDialog(self.stencil, self).exec_()
            self.logger.add_to_log("Active stencil: {0}".format(self.stencil))
        pass

    def pick_point(self):
        self.pick_stack.empty()
        self.object_stack.empty()
        self.canvas.draw_canvas(markers=self.pick_stack.items)
        self.mode = 'pick_pt'

    def set_grid(self):
        self.grid = GridDialog(self.grid, self).exec_()
        if self.grid[0]:
            self.logger.add_to_log("Grid active. Primary spacing {0}, alternative spacing {1}".
                                   format(self.grid[1], self.grid[2]))
        else:
            self.logger.add_to_log("Grid not active.")

    def measure(self):
        pass

    def select_color(self):
        self.color = QtWidgets.QColorDialog.getColor().name()
        self.logger.add_to_log("Set color: {0}".format(self.color))

    def select_stencil(self):
        self.stencil = StencilDialog(self.stencil, self).exec_()
        self.logger.add_to_log("Active stencil: {0}".format(self.stencil))

    def set_properties(self):
        self.layer = PropsDialog(self.layer, self.dxf_file, self).exec_()
        self.logger.add_to_log("Active layer: {0}".format(self.layer))

    def view_properties(self):
        pass

    def transform(self):
        try:
            mat_pick_stack = self.mat.pick_stack
        except AttributeError:
            self.logger.add_to_log("No .mat file found.")
            pass
        else:
            if self.pick_stack.size() == mat_pick_stack.size() and self.pick_stack.size() >= 3:
                self.logger.add_to_log("Cool!")
                self.trafo_matrix = affine_trafo(mat_pick_stack.items, self.pick_stack.items)
                self.logger.add_to_log('Affine transformation successful. Trace: {0:.2f}'.
                                       format(np.trace(self.trafo_matrix)))
                self.mat_file = copy.deepcopy(self.mat.mat_file)
                self.mat_file.transform(self.trafo_matrix)

                #     self.dxf_img.cts_vmin = self.raw_img.cts_vmin self.mat.canvas.count_limits & fixed
                #     self.dxf_img.cts_vmax = self.raw_img.cts_vmax
                self.pick_stack.empty()
                self.canvas.draw_canvas(mat=self.mat_file, markers=self.pick_stack.items)
            else:
                self.logger.add_to_log("For trafo select at least three data points in mat and dxf each.\n"
                                       "Ensure that the same number of points is selected in each.")

    def mouse_wheel(self, event):
        position = self.get_coordinates(event, use_grid=False)
        if event.button == 'up' and any(position):
            plot_lims = [[(self.canvas.plot_limits[0][0] - position[0]) / 1.2 + position[0],
                          (self.canvas.plot_limits[0][1] - position[0]) / 1.2 + position[0]],
                         [(self.canvas.plot_limits[1][0] - position[1]) / 1.2 + position[1],
                          (self.canvas.plot_limits[1][1] - position[1]) / 1.2 + position[1]]]
            self.canvas.plot_limits_fixed = True
            self.canvas.draw_canvas(plot_limits=plot_lims)
        elif event.button == 'down' and any(position):
            plot_lims = [[(self.canvas.plot_limits[0][0] - position[0]) * 1.2 + position[0],
                          (self.canvas.plot_limits[0][1] - position[0]) * 1.2 + position[0]],
                         [(self.canvas.plot_limits[1][0] - position[1]) * 1.2 + position[1],
                          (self.canvas.plot_limits[1][1] - position[1]) * 1.2 + position[1]]]
            self.canvas.plot_limits_fixed = True
            self.canvas.draw_canvas(plot_limits=plot_lims)

    def mouse_moved(self, event):
        position = self.get_coordinates(event, use_grid=True)
        if any(position):
            self.status_bar.showMessage("X={0:.3f}, Y={1:.3f}".format(*position))

    def mouse_released(self, event):
        position = self.get_coordinates(event, use_grid=True)
        if any(position):
            if event.button == 1:
                if self.mode == 'pick_pt':
                    obj_index, position = kd_nearest(self.dxf_file.points().coordinates(), position)
                    self.pick_stack.push(position)
                else:
                    self.pick_stack.push(position)
                self.canvas.draw_canvas(markers=self.pick_stack.items)
            elif event.button == 3 and not self.pick_stack.is_empty():
                self.pick_stack.pop()
                if self.mode == 'pick_pt':
                    self.canvas.draw_canvas(markers=self.pick_stack.items)

    def get_coordinates(self, event, use_grid):
        if any([event.xdata, event.ydata]):
            if use_grid and self.grid[0]:
                if QtWidgets.QApplication.keyboardModifiers() == QtCore.Qt.ControlModifier:
                    return [round(event.xdata / self.grid[2]) * self.grid[2],
                            round(event.ydata / self.grid[2]) * self.grid[2]]
                else:
                    return [round(event.xdata/self.grid[1])*self.grid[1],
                            round(event.ydata / self.grid[1]) * self.grid[1]]
            else:
                return [event.xdata, event.ydata]
        else:
            return [None, None]

    def set_mat(self, mat):
        self.mat = mat
