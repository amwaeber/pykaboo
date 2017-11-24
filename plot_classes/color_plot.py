import numpy as np
import scipy.io

import tum_jet
from plot_classes.my_mpl_canvas import MyMplCanvas


class ColorPlot(MyMplCanvas):
    """A canvas that updates itself every second with a new plot."""

    def __init__(self, *args, **kwargs):
        MyMplCanvas.__init__(self, *args, **kwargs)

    def compute_initial_figure(self):
        self.graph = []
        self.select_coord = []
        self.select_nv = []
        self.dxf_objects = []
        self.cts_xy = np.random.random((100, 100))
        self.x_axis = np.arange(0, 10, 0.1)
        self.y_axis = np.arange(0, 10, 0.1)
        self.x_lim = [0, 10]
        self.y_lim = [0, 10]
        self.cts_vmin = 0
        self.cts_vmax = 10
        self.axes.imshow(self.cts_xy, extent=(self.x_axis[0], self.x_axis[-1], self.y_axis[0], self.y_axis[-1]),
                         cmap=tum_jet.tum_jet, vmin=self.cts_vmin, vmax=self.cts_vmax)

    def load_mat(self, filename):
        self.graph = scipy.io.loadmat(filename)
        self.select_coord = []
        self.select_nv = []
        if 'result_sec_chan' in self.graph.keys():
            self.cts_xy = np.reshape(2 * self.graph['result_sec_chan'].ravel() - self.graph['result'].ravel(),
                                     (len(self.graph['result']), len(self.graph['result'])))
        else:
            self.cts_xy = self.graph['result']
        self.x_axis = self.graph['x'][0]
        self.y_axis = self.graph['y'][0]
        self.axes.cla()
        self.axes.imshow(self.cts_xy, extent=(self.x_axis[0], self.x_axis[-1],
                                              self.y_axis[0], self.y_axis[-1]), cmap=tum_jet.tum_jet,
                         vmin=self.cts_vmin, vmax=self.cts_vmax)
        self.draw()

    def draw_dxf(self):
        self.axes.cla()
        if len(self.cts_xy):
            self.axes.imshow(self.cts_xy, extent=(self.x_axis[0], self.x_axis[-1], self.y_axis[0], self.y_axis[-1]),
                             cmap=tum_jet.tum_jet, vmin=self.cts_vmin, vmax=self.cts_vmax)
        if len(self.dxf_objects):
            for patch in self.dxf_objects:
                self.axes.add_patch(patch)
        if len(self.select_coord):
            self.axes.plot([pt[0] for pt in self.select_coord], [pt[1] for pt in self.select_coord], ls='None',
                           marker='o', markerfacecolor='None', markeredgecolor='r')
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
                                              self.y_axis[0], self.y_axis[-1]), cmap=tum_jet.tum_jet,
                         vmin=self.cts_vmin, vmax=self.cts_vmax)
        if len(self.select_coord):
            self.axes.plot([pt[0] for pt in self.select_coord], [pt[1] for pt in self.select_coord], ls='None',
                           marker='o', markerfacecolor='None', markeredgecolor='k')
        if len(self.select_nv):
            self.axes.plot([pt[0] for pt in self.select_nv], [pt[1] for pt in self.select_nv], ls='None', marker='o',
                           markerfacecolor='r', markeredgecolor='w')
        self.draw()

    def save(self, fname):
        self.fig.savefig(fname)


