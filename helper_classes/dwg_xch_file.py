from PyQt5 import QtWidgets

import ezdxf

from utility.config import paths
from helper_classes.dxf_point import DXFPoint


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

    def points(self):
        pt_list = DXFPoint()
        for e in self.drawing.entities:
            if e.dxftype() == 'CIRCLE':
                pt_list.add(e.dxf.center[:-1], e.dxf.handle)
            elif e.dxftype() == 'POLYLINE':
                for pt in e.points():
                    pt_list.add(pt[:-1], e.dxf.handle)
            elif e.dxftype() == 'LWPOLYLINE':  # TODO: Test 'LWPOLYLINE'
                for pt in e.get_rstrip_points():
                    pt_list.add(pt, e.dxf.handle)
        return pt_list
