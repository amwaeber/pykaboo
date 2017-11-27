from PyQt5 import QtGui, QtWidgets

from utility.config import paths


# noinspection PyAttributeOutsideInit
class Logger(QtWidgets.QWidget):

    def __init__(self, parent = None):
        super(Logger, self).__init__(parent)

        self.edt_log = QtWidgets.QTextEdit('Log: \n', self)
        self.save_btn = QtWidgets.QPushButton('Save', self)
        self.save_btn.setToolTip('Save log file')
        self.save_btn.setObjectName('log_save')
        self.save_btn.clicked.connect(self.save)
        self.save_btn.resize(self.save_btn.sizeHint())
        self.clear_btn = QtWidgets.QPushButton('Clear', self)
        self.clear_btn.setToolTip('Clear log')
        self.clear_btn.setObjectName('log_clear')
        self.clear_btn.clicked.connect(self.clear)
        self.clear_btn.resize(self.clear_btn.sizeHint())

        vbox1 = QtWidgets.QVBoxLayout()
        vbox1.addWidget(self.save_btn)
        vbox1.addWidget(self.clear_btn)
        main_hbox = QtWidgets.QHBoxLayout(self)
        main_hbox.setSpacing(10)
        main_hbox.addWidget(self.edt_log)
        main_hbox.addLayout(vbox1)

    def save(self):
        fname = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File', paths['registration'], "Text files (*.txt)")[0]
        if not fname.endswith('.txt'):
            fname += ".txt"
        with open(fname, 'w') as file:
            file.write(self.edt_log.toPlainText())

    def add_to_log(self, entry):
        self.edt_log.append(entry)
        self.edt_log.moveCursor(QtGui.QTextCursor.End)

    def clear(self):
        self.edt_log.setText('Log: ')

    def closeEvent(self, event):
        event.ignore()
