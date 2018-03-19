from matplotlib import patches as patches
from matplotlib.path import Path
from PyQt5 import QtWidgets

from plot_classes.my_mpl_canvas import MyMplCanvas
from utility import tum_jet
from utility.xterm_hex_conv import xterm_to_hex
from utility.config import paths


# noinspection PyAttributeOutsideInit, PyArgumentList
class ColorPlot(MyMplCanvas):

    def __init__(self, *args, **kwargs):
        MyMplCanvas.__init__(self, *args, **kwargs)

    def compute_initial_figure(self):
        self.plot_limits = [[0, 100], [0, 100]]
        self.plot_limits_fixed = False
        self.count_limits = [0, 1e5]
        self.count_limits_fixed = False
        self.mat = None
        self.dxf = None
        self.markers = None
        self.axes.cla()

    def draw_mat(self, mat_file):
        if not self.count_limits_fixed:
            cts = mat_file.graph['result'].ravel()
            self.count_limits = [min(cts), max(cts)]
        if not self.plot_limits_fixed:
            self.plot_limits = [[mat_file.graph['x'][0, 0], mat_file.graph['x'][0, -1]],
                                [mat_file.graph['y'][0, 0], mat_file.graph['y'][0, -1]]]
        self.axes.imshow(mat_file.graph['result'], extent=(mat_file.graph['x'][0, 0], mat_file.graph['x'][0, -1],
                                                           mat_file.graph['y'][0, 0], mat_file.graph['y'][0, -1]),
                         cmap=tum_jet.tum_jet, vmin=self.count_limits[0], vmax=self.count_limits[1])

    def draw_dxf(self, dxf_file, **kwargs):
        for patch in self.patches(dxf_file, **kwargs):
            if patch:
                self.axes.add_patch(patch)

    def draw_markers(self, markers):
        self.axes.plot([pt[0] for pt in markers], [pt[1] for pt in markers], ls='None',
                       marker='+', markeredgecolor='k', markersize=15)

    def draw_canvas(self, **kwargs):
        self.plot_limits = kwargs.get('plot_limits', self.plot_limits)
        self.mat = kwargs.get('mat', self.mat)
        self.dxf = kwargs.get('dxf', self.dxf)
        self.markers = kwargs.get('markers', self.markers)
        dxf_color = kwargs.get('dxf_color', None)
        show_axes = kwargs.get('show_axes', True)
        self.axes.cla()
        if self.mat:
            self.draw_mat(self.mat)
        if self.dxf:
            self.draw_dxf(self.dxf, dxf_color=dxf_color)
        if self.markers:
            self.draw_markers(self.markers)
        self.axes.set_xlim(self.plot_limits[0][0], self.plot_limits[0][1])
        self.axes.set_ylim(self.plot_limits[1][0], self.plot_limits[1][1])
        self.axes.get_xaxis().set_visible(show_axes)
        self.axes.get_yaxis().set_visible(show_axes)
        self.draw()

    def update_canvas(self, **kwargs):  # TODO: Change canvas methods to partial updates
        pass

    def save(self, parent):
        fname = QtWidgets.QFileDialog.getSaveFileName(parent, 'Save File', paths['registration'],
                                                      "Portable network graphics (*.png)")[0]
        if not fname:  # capture cancel in dialog
            return
        self.fig.savefig(fname, bbox_inches='tight')

    @staticmethod
    def patches(dxf_file, **kwargs):
        dxf_color = kwargs.get('dxf_color', None)
        for e in dxf_file.drawing.entities:
            if dxf_color:
                c = dxf_color
            elif e.dxf.color < 256:
                c = e.dxf.color
            else:
                c = dxf_file.drawing.layers.get(e.dxf.layer).get_color()
            if e.dxftype() == 'CIRCLE':
                yield patches.Circle(e.dxf.center[:-1], e.dxf.radius, fill=False, color=xterm_to_hex(c))
            elif e.dxftype() == 'POLYLINE':
                codes = [Path.MOVETO] + [Path.LINETO for _ in range(e.__len__() - 1)] + [Path.CLOSEPOLY]
                pts = [p[:-1] for p in e.points()]
                path = Path(pts + [pts[0]], codes)
                yield patches.PathPatch(path, fill=False, color=xterm_to_hex(c))
            elif e.dxftype() == 'LWPOLYLINE':  # TODO: Test 'LWPOLYLINE'
                codes = [Path.MOVETO] + [Path.LINETO for _ in range(e.__len__() - 1)] + [Path.CLOSEPOLY]
                path = Path(e.get_rstrip_points() + [e.get_rstrip_points()[0]], codes)
                yield patches.PathPatch(path, fill=False, color=xterm_to_hex(c))
