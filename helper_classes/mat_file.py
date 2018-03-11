from PyQt5 import QtWidgets
import numpy as np
import scipy.io
from scipy.interpolate import griddata

from utility.config import paths


# noinspection PyArgumentList
class MatFile:
    def __init__(self):
        self.file_name = ''
        self.graph = {'N': np.array([[100, 100, 1]]),
                      'x': np.array([np.linspace(0, 10, 100)]),
                      'y': np.array([np.linspace(0, 10, 100)]),
                      'z': np.array([[0.]]),
                      'result': np.zeros((100, 100))}

    def load(self, parent, **kwargs):
        dialog = kwargs.get('dialog', False)
        self.file_name = kwargs.get('file_name', self.file_name)
        if dialog or not self.file_name:
            fname = QtWidgets.QFileDialog.getOpenFileName(parent, 'Open file', paths['registration'],
                                                          "Matlab data file (*.mat)")[0]
            if not fname:  # capture cancel in dialog
                return
            self.file_name = fname
        self.graph = scipy.io.loadmat(self.file_name)
        parent.pick_stack.empty()

    def transform(self, trafo_matrix):
        x_ax = self.graph['x'][0]
        y_ax = self.graph['y'][0]
        x_ax, y_ax = np.meshgrid(x_ax, y_ax)
        x_ax, y_ax, _ = np.dot(np.array([x_ax, y_ax, 1]), trafo_matrix)
        x_ax, y_ax = x_ax.ravel(), y_ax.ravel()

        self.graph['N'] = np.array([[200, 200, 1]])
        # nx, ny = 200, 200
        # Generate a regular grid to interpolate the data.
        xi = np.linspace(min(x_ax), max(x_ax), self.graph['N'][0, 0])
        yi = np.linspace(min(y_ax), max(y_ax), self.graph['N'][0, 1])
        xi, yi = np.meshgrid(xi, yi)

        # Interpolate using linear triangularization
        self.graph['result'] = griddata((x_ax, y_ax), self.graph['result'].ravel(), (xi, yi),
                                        method='linear', fill_value=min(self.graph['result'].ravel()))
        self.graph['x'][0] = xi[0]
        self.graph['y'][0] = yi.T[0]
