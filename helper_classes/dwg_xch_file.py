from PyQt5 import QtWidgets

import ezdxf

from utility.config import paths
from helper_classes.dxf_point import DXFPoint
from helper_classes.stack import Stack


# noinspection PyArgumentList
class DwgXchFile:
    def __init__(self):
        self.file_name = ''
        self.file_type = 'standard'
        self.drawing = ezdxf.new('R2010')
        self.added_objects = Stack()

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

    def add_stencil(self, stencil, position):  # TODO: Change all DXF formats to beyond R12! Then implement Import Fct
        msp = self.drawing.modelspace()
        n_entities = len(self.drawing.entities)  # TODO: Clean way for undoing dxf insertion
        for e in stencil.drawing.entities:
            if e.dxf.layer not in self.drawing.layers:
                self.drawing.layers.new(name=e.dxf.layer,
                                        dxfattribs={'linetype': 'CONTINUOUS', 'color': self.drawing.layers.__len__()})
            if e.dxftype() == 'CIRCLE':
                center = (e.dxf.center[0] + position[0], e.dxf.center[1] + position[1], e.dxf.center[2])
                msp.add_circle(center, e.dxf.radius)
                print('circle', dxfattribs={'layer': e.dxf.layer})
            elif e.dxftype() == 'POLYLINE':
                pt_list = [(p[0] + position[0], p[1] + position[1], p[2]) for p in e.points()]
                msp.add_polyline3d(pt_list, dxfattribs={'layer': e.dxf.layer})
            elif e.dxftype() == 'LWPOLYLINE':  # TODO: Test 'LWPOLYLINE'
                pt_list = [(p[0] + position[0], p[1] + position[1]) for p in e.get_rstrip_points()]
                self.drawing.modelspace().add_lwpolyline(pt_list, dxfattribs={'layer': e.dxf.layer})
        self.added_objects.push(len(self.drawing.entities) - n_entities)

    def undo_add_stencil(self):
        if not self.added_objects.is_empty():
            msp = self.drawing.modelspace()
            for e in msp.query()[-self.added_objects.pop():]:
                msp.delete_entity(e)
