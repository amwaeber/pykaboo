from PyQt5 import QtWidgets


# noinspection PyAttributeOutsideInit, PyArgumentList
class MinMaxDialog(QtWidgets.QDialog):
    def __init__(self, count_limits, parent=None):
        super(MinMaxDialog, self).__init__(parent)
        self.count_limits = count_limits

        self.lbl_min = QtWidgets.QLabel("Min. Cts.:", self)
        self.edt_min = QtWidgets.QLineEdit(str(self.count_limits[0]), self)
        self.lbl_max = QtWidgets.QLabel("Max. Cts.:", self)
        self.edt_max = QtWidgets.QLineEdit(str(self.count_limits[1]), self)
        self.btns = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel, self)
        self.btns.accepted.connect(self.accept)
        self.btns.rejected.connect(self.reject)

        hbox1 = QtWidgets.QHBoxLayout()
        hbox1.setSpacing(10)
        hbox1.addWidget(self.lbl_min)
        hbox1.addWidget(self.edt_min)

        hbox2 = QtWidgets.QHBoxLayout()
        hbox2.setSpacing(10)
        hbox2.addWidget(self.lbl_max)
        hbox2.addWidget(self.edt_max)

        vbox = QtWidgets.QVBoxLayout(self)
        vbox.setSpacing(10)
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)
        vbox.addSpacing(5)
        vbox.addWidget(self.btns)

    def exec_(self):
        super(MinMaxDialog, self).exec_()
        return [float(self.edt_min.text()), float(self.edt_max.text())]
