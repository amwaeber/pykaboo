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
        self.drawing = dxfgrabber.read(io.StringIO())

    def load(self, parent, file_type='standard'):
        if file_type == 'standard':
            self.file_name = QtWidgets.QFileDialog.getOpenFileName(parent, 'Open file', paths['registration'],
                                                                   "Drawing interchange files (*.dxf)")[0]
        elif file_type == 'template':
            self.file_name = QtWidgets.QFileDialog.getOpenFileName(parent, 'Open file', paths['templates'],
                                                                   "Drawing interchange files (*.dxf)")[0]
        elif file_type == 'stencil':
            self.file_name = QtWidgets.QFileDialog.getOpenFileName(parent, 'Open file', paths['stencils'],
                                                                   "Drawing interchange files (*.dxf)")[0]
        self.drawing = dxfgrabber.readfile(self.file_name)

    def save(self, parent, overwrite=True):
        if not overwrite:
            self.file_name = QtWidgets.QFileDialog.getSaveFileName(parent, 'Save File', paths['registration'],
                                                                   "Drawing interchange files (*.dxf)")[0]
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
