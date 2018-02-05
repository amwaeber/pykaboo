from PyQt5 import QtWidgets
import os

from plot_classes.color_plot import ColorPlot
from utility.config import paths
from helper_classes.dwg_xch_file import DwgXchFile


# noinspection PyAttributeOutsideInit
# noinspection PyArgumentList
class StencilDialog(QtWidgets.QDialog):
    def __init__(self, stencil, parent=None):
        super(StencilDialog, self).__init__(parent)
        self.stencil = stencil

        self.stencil_list = [f for f in os.listdir(paths['stencils']) if f.endswith('.dxf')]
        self.stencil_btns = [QtWidgets.QPushButton(st, self) for st in self.stencil_list]
        for btn in self.stencil_btns:
            btn.setObjectName(btn.text())
            btn.clicked.connect(self.set_stencil)

        self.dxf_file_list = [DwgXchFile() for _ in self.stencil_list]
        for idxf, dxf_file in enumerate(self.dxf_file_list):
            dxf_file.load(self, file_type='stencil', file_name=os.path.join(paths['stencils'],
                                                                            self.stencil_list[idxf]))
        self.previews = [ColorPlot(self) for _ in self.stencil_list]
        for icanvas, canvas in enumerate(self.previews):
            canvas.draw_canvas(dxf=self.dxf_file_list[icanvas], dxf_color=1, plot_limits=[[-1, 1], [-1, 1]],
                               show_axes=False)
        self.btns = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel, self)
        self.btns.accepted.connect(self.accept)
        self.btns.rejected.connect(self.reject)

        self.scroll = QtWidgets.QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFixedHeight(600)
        self.scrollContents = QtWidgets.QWidget()
        glay = QtWidgets.QGridLayout(self.scrollContents)
        for ist, st in enumerate(self.previews):
            glay.addWidget(st, 2 * (ist // 4), ist % 4)
            glay.addWidget(self.stencil_btns[ist], 2 * (ist // 4) + 1, ist % 4)
        self.scroll.setWidget(self.scrollContents)

        vbox = QtWidgets.QVBoxLayout(self)
        vbox.setSpacing(10)
        vbox.addWidget(self.scroll)
        vbox.addSpacing(5)
        vbox.addWidget(self.btns)

    def set_stencil(self):
        sel_stencil = self.sender()
        self.stencil = str(sel_stencil.objectName())

    def exec_(self):
        super(StencilDialog, self).exec_()
        return self.stencil
