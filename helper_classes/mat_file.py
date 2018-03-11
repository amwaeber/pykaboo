from PyQt5 import QtWidgets
import numpy as np
import scipy.io

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
        pass