#!python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 27 11:07:11 2017

@author: Andreas.Waeber aka webmaster3000
"""
import sys

from PyQt5 import QtWidgets

from user_interfaces.main_window import MainWindow


def main():
    app = QtWidgets.QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())


if __name__ == '__main__':  # runs only if file is executed, not when it's imported
    main()
