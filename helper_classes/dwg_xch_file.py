from PyQt5 import QtWidgets

import ezdxf

from utility.config import paths


# noinspection PyArgumentList
class DwgXchFile:
    def __init__(self):
        self.file_name = ''
        self.file_type = 'standard'
        self.drawing = ezdxf.new('R2010')

    def load(self, parent, file_type='standard', **kwargs):
        self.file_name = kwargs.get('file_name', self.file_name)
        self.file_type = file_type
        if self.file_type == 'standard':
            fname = QtWidgets.QFileDialog.getOpenFileName(parent, 'Open file', paths['registration'],
                                                          "Drawing interchange files (*.dxf)")[0]
        elif self.file_type == 'template':
            fname = QtWidgets.QFileDialog.getOpenFileName(parent, 'Open file', paths['templates'],
                                                          "Drawing interchange files (*.dxf)")[0]
        elif self.file_type == 'stencil' and not self.file_name:
            fname = QtWidgets.QFileDialog.getOpenFileName(parent, 'Open file', paths['stencils'],
                                                          "Drawing interchange files (*.dxf)")[0]
        elif self.file_type == 'stencil':
            fname = self.file_name
        else:
            fname = None
        if not fname:  # capture cancel in dialog
            return
        self.file_name = fname
        self.drawing = ezdxf.readfile(self.file_name)

    def save(self, parent, overwrite=True):
        if any([not overwrite, not self.file_name, not self.file_type == 'standard']):
            fname = QtWidgets.QFileDialog.getSaveFileName(parent, 'Save File', paths['registration'],
                                                          "Drawing interchange files (*.dxf)")[0]
            if not fname:  # capture cancel in dialog
                return
            self.file_name = fname
            self.file_type = 'standard'
            self.drawing.saveas(self.file_name)
        else:
            self.drawing.save()
