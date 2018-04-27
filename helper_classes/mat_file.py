from PyQt5 import QtWidgets
import numpy as np
import scipy.io
from scipy.interpolate import griddata

from utility.config import paths


# noinspection PyArgumentList
class MatFile:
    """ Class containing basic information of imported mat file.

        Class attributes are initialised to default values in __init__.

        Attributes:
            file_name (string): Name of mat file including path.
            graph (dict of np.array): Contains actual image information. Keys are:
                N (np.array): 2d array containing dimensions of x,y, and z values. Default np.array([[100, 100, 1]]).
                x (np.array): 2d array containing x axis coordinates. Default np.array([np.linspace(0, 10, 100)]).
                y (np.array): 2d array containing y axis coordinates. Default np.array([np.linspace(0, 10, 100)]).
                z (np.array): 2d array containing z axis coordinates. Default np.array([[0.]]).
                result (np.array): 2d array containing intensity values. Default np.zeros((100, 100)).
    """
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
        y_ax = self.graph['y'][0][::-1]
        x_ax, y_ax = np.meshgrid(x_ax, y_ax)
        x_ax, y_ax, _ = np.dot(np.array([x_ax, y_ax, 1]), trafo_matrix)
        x_ax, y_ax = x_ax.ravel(), y_ax.ravel()

        self.graph['N'] = np.array([[300, 300, 1]])
        # Generate a regular grid to interpolate the data.
        xi = np.linspace(min(x_ax), max(x_ax), self.graph['N'][0, 0])
        yi = np.linspace(min(y_ax), max(y_ax), self.graph['N'][0, 1])
        xi, yi = np.meshgrid(xi, yi)

        # Interpolate using linear triangularization
        self.graph['result'] = griddata((x_ax, y_ax), self.graph['result'].ravel(), (xi, yi),
                                        method='linear', fill_value=0)[::-1]
        self.graph['x'] = np.array([xi[0]])
        self.graph['y'] = np.array([yi.T[0]])
