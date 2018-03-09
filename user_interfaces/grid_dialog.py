from PyQt5 import QtWidgets


# noinspection PyAttributeOutsideInit, PyArgumentList
class GridDialog(QtWidgets.QDialog):
    def __init__(self, grid, parent=None):
        super(GridDialog, self).__init__(parent)
        self.grid = grid

        self.lbl_active = QtWidgets.QLabel("Primary Grid active", self)
        self.cb_primary = QtWidgets.QCheckBox(self)
        self.cb_primary.setChecked(self.grid[0])
        self.lbl_primary = QtWidgets.QLabel("Primary Grid:", self)
        self.edt_primary = QtWidgets.QLineEdit(str(self.grid[1]), self)
        self.lbl_alt = QtWidgets.QLabel("Alternative Grid:", self)
        self.edt_alt = QtWidgets.QLineEdit(str(self.grid[2]), self)
        self.btns = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel, self)
        self.btns.accepted.connect(self.accept)
        self.btns.rejected.connect(self.reject)

        hbox1 = QtWidgets.QHBoxLayout()
        hbox1.setSpacing(10)
        hbox1.addWidget(self.lbl_active)
        hbox1.addWidget(self.cb_primary)

        hbox2 = QtWidgets.QHBoxLayout()
        hbox2.setSpacing(10)
        hbox2.addWidget(self.lbl_primary)
        hbox2.addWidget(self.edt_primary)

        hbox3 = QtWidgets.QHBoxLayout()
        hbox3.setSpacing(10)
        hbox3.addWidget(self.lbl_alt)
        hbox3.addWidget(self.edt_alt)

        vbox = QtWidgets.QVBoxLayout(self)
        vbox.setSpacing(10)
        vbox.addLayout(hbox1)
        vbox.addSpacing(5)
        vbox.addLayout(hbox2)
        vbox.addLayout(hbox3)
        vbox.addSpacing(5)
        vbox.addWidget(self.btns)

    def exec_(self):
        super(GridDialog, self).exec_()
        return [self.cb_primary.isChecked(), float(self.edt_primary.text()), float(self.edt_alt.text())]
