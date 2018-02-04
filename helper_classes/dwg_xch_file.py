from PyQt5 import QtWidgets

import dxfgrabber
import io
from dxfwrite import DXFEngine as dxf
from dxfwrite import const

from utility.config import paths


# noinspection PyArgumentList
class DwgXchFile:
    def __init__(self):
        self.file_name = ''
        self.file_type = 'standard'
        self.drawing = dxfgrabber.read(io.StringIO())

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
        self.drawing = dxfgrabber.readfile(self.file_name)

    def save(self, parent, overwrite=True):
        if any([not overwrite, not self.file_name, not self.file_type == 'standard']):
            fname = QtWidgets.QFileDialog.getSaveFileName(parent, 'Save File', paths['registration'],
                                                          "Drawing interchange files (*.dxf)")[0]
            if not fname:  # capture cancel in dialog
                return
            self.file_name = fname
            self.file_type = 'standard'
        save_drawing = dxf.drawing(self.file_name)
        for l in self.drawing.layers:
            save_drawing.add_layer(name=l.name, color=l.color, linetype=l.linetype)
        for s in self.drawing.styles:
            save_drawing.add_style(name=s.name, height=s.height, width=s.width, oblique=s.oblique,
                                   font=s.font, bigfont=s.big_font)
        for e in self.drawing.entities:
            if e.dxftype == 'LINE':
                line = dxf.line(start=e.start, end=e.end, layer=e.layer, color=e.color)
                save_drawing.add(line)
            elif e.dxftype == 'CIRCLE':
                circle = dxf.circle(radius=e.radius, center=e.center, layer=e.layer, color=e.color)
                save_drawing.add(circle)
            elif e.dxftype == 'POLYLINE':
                pline = dxf.polyline(points=e.points, layer=e.layer, color=e.color)
                if e.is_closed:
                    pline.close()
                save_drawing.add(pline)
            elif e.dxftype == 'TEXT':
                if e.is_backwards:
                    m_flag = const.MIRROR_X
                elif e.is_upside_down:
                    m_flag = const.MIRROR_Y
                else:
                    m_flag = 0
                text = dxf.circle(text=e.text, insert=e.insert, height=e.height, width=e.width,
                                  oblique=e.oblique, rotation=e.rotation, style=e.style, halign=e.halign,
                                  valign=e.valign, mirror=m_flag, layer=e.layer, color=e.color)
                save_drawing.add(text)
        save_drawing.save()
