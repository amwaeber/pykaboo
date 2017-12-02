from PyQt5 import QtWidgets

from plot_classes.color_plot import ColorPlot
from helper_classes.dwg_xch_file import DwgXchFile


# noinspection PyAttributeOutsideInit
class CADWidget(QtWidgets.QWidget):
    def __init__(self, action, window_number, logger, parent=None):
        super(CADWidget, self).__init__(parent)
        self.window_number = window_number
        self.logger = logger

        self.canvas = ColorPlot(self)
        self.canvas.mpl_connect('scroll_event', self.mouse_wheel)
        self.canvas.mpl_connect('button_release_event', self.mouse_released)
        box = QtWidgets.QGridLayout()
        box.addWidget(self.canvas)
        self.setLayout(box)

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

    def mouse_wheel(self, event):
        if event.button == 'up':
            plot_lims = [[(self.canvas.plot_limits[0][0] - event.xdata) / 1.2 + event.xdata,
                          (self.canvas.plot_limits[0][1] - event.xdata) / 1.2 + event.xdata],
                         [(self.canvas.plot_limits[1][0] - event.ydata) / 1.2 + event.ydata,
                          (self.canvas.plot_limits[1][1] - event.ydata) / 1.2 + event.ydata]]
            self.canvas.draw_canvas(plot_limits=plot_lims)
        elif event.button == 'down':
            plot_lims = [[(self.canvas.plot_limits[0][0] - event.xdata) * 1.2 + event.xdata,
                          (self.canvas.plot_limits[0][1] - event.xdata) * 1.2 + event.xdata],
                         [(self.canvas.plot_limits[1][0] - event.ydata) * 1.2 + event.ydata,
                          (self.canvas.plot_limits[1][1] - event.ydata) * 1.2 + event.ydata]]
            self.canvas.draw_canvas(plot_limits=plot_lims)

    def mouse_released(self, event):
        pass



