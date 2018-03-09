from PyQt5 import QtWidgets

from utility.xterm_hex_conv import xterm_to_hex


# noinspection PyAttributeOutsideInit, PyArgumentList
class PropsDialog(QtWidgets.QDialog):
    def __init__(self, layer, dxf_file, parent=None):
        super(PropsDialog, self).__init__(parent)
        self.active_layer = layer

        self.layer_color_btns = [QtWidgets.QPushButton(self) for _ in dxf_file.drawing.layers]
        self.layer_select_cbs = [QtWidgets.QCheckBox(self) for _ in dxf_file.drawing.layers]
        self.layer_cbgp = QtWidgets.QButtonGroup()
        for il, l in enumerate(dxf_file.drawing.layers):
            self.layer_color_btns[il].setStyleSheet("background-color: %s" % xterm_to_hex(l.get_color()))
            self.layer_color_btns[il].resize(self.layer_color_btns[il].sizeHint())
            self.layer_color_btns[il].clicked.connect(self.set_color)
            self.layer_select_cbs[il].setObjectName(str(il))
            self.layer_cbgp.addButton(self.layer_select_cbs[il], il)
        self.layer_cbgp.buttonClicked.connect(self.set_layer)
        self.layer_name_edts = [QtWidgets.QLineEdit(l.dxf.name, self) for l in dxf_file.drawing.layers]

        self.btns = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel, self)
        self.btns.accepted.connect(self.accept)
        self.btns.rejected.connect(self.reject)

        vbox = QtWidgets.QVBoxLayout(self)
        vbox.setSpacing(10)
        hboxes = [QtWidgets.QHBoxLayout() for _ in self.layer_color_btns]
        for il, hbox in enumerate(hboxes):
            hbox.setSpacing(10)
            hbox.addWidget(self.layer_select_cbs[il])
            hbox.addWidget(self.layer_color_btns[il])
            hbox.addWidget(self.layer_name_edts[il])
            vbox.addLayout(hbox)
        vbox.addSpacing(5)
        vbox.addWidget(self.btns)

    def set_layer(self, cb_selected):
        self.active_layer = int(cb_selected.objectName())

    def set_color(self):
        sel_color_btn = self.sender()
        color = QtWidgets.QColorDialog.getColor()
        sel_color_btn.setStyleSheet("background-color: %s" % color.name())

    def exec_(self):
        super(PropsDialog, self).exec_()
        return self.active_layer
