import os
from PyQt5 import QtWidgets, QtGui

from plot_classes.color_plot import ColorPlot
from helper_classes.dwg_xch_file import DwgXchFile
from utility.config import paths


# noinspection PyAttributeOutsideInit
# noinspection PyArgumentList
class CADWidget(QtWidgets.QWidget):
    def __init__(self, action, window_number, logger, parent=None):
        super(CADWidget, self).__init__(parent)
        self.window_number = window_number
        self.logger = logger

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
        stencil_btn.triggered.connect(self.select_stencil)
        pick_btn = QtWidgets.QAction(QtGui.QIcon(os.path.join(paths['icons'], 'pick.png')),
                                     'Pick object', self)
        pick_btn.triggered.connect(self.pick_object)
        grid_btn = QtWidgets.QAction(QtGui.QIcon(os.path.join(paths['icons'], 'grid.png')),
                                     'Show grid lines', self)
        grid_btn.triggered.connect(self.show_grid)
        measure_btn = QtWidgets.QAction(QtGui.QIcon(os.path.join(paths['icons'], 'measure.png')),
                                        'Measure', self)
        measure_btn.triggered.connect(self.measure)
        color_btn = QtWidgets.QAction(QtGui.QIcon(os.path.join(paths['icons'], 'palette.png')),
                                      'Select color', self)
        color_btn.triggered.connect(self.select_color)
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

    def select_stencil(self):
        pass

    def pick_object(self):
        pass

    def show_grid(self):
        pass

    def measure(self):
        pass

    def select_color(self):
        pass

    def set_properties(self):
        pass

    def view_properties(self):
        pass

    def transform(self):
        pass

    def mouse_wheel(self, event):
        if event.button == 'up':
            plot_lims = [[(self.canvas.plot_limits[0][0] - event.xdata) / 1.2 + event.xdata,
                          (self.canvas.plot_limits[0][1] - event.xdata) / 1.2 + event.xdata],
                         [(self.canvas.plot_limits[1][0] - event.ydata) / 1.2 + event.ydata,
                          (self.canvas.plot_limits[1][1] - event.ydata) / 1.2 + event.ydata]]
            self.canvas.plot_limits_fixed = True
            self.canvas.draw_canvas(plot_limits=plot_lims)
        elif event.button == 'down':
            plot_lims = [[(self.canvas.plot_limits[0][0] - event.xdata) * 1.2 + event.xdata,
                          (self.canvas.plot_limits[0][1] - event.xdata) * 1.2 + event.xdata],
                         [(self.canvas.plot_limits[1][0] - event.ydata) * 1.2 + event.ydata,
                          (self.canvas.plot_limits[1][1] - event.ydata) * 1.2 + event.ydata]]
            self.canvas.plot_limits_fixed = True
            self.canvas.draw_canvas(plot_limits=plot_lims)

    def mouse_moved(self, event):
        if any([event.xdata, event.ydata]):
            self.status_bar.showMessage("X={0:.3f}, Y={1:.3f}".format(event.xdata, event.ydata))

    def mouse_released(self, event):
        pass
