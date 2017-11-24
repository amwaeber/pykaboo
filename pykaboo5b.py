#!python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 27 11:07:11 2017

@author: Andreas.Waeber
"""
###############
### IMPORTS ###
###############

import sys

import matplotlib
from PyQt5 import QtWidgets

from user_interfaces.main_window import MainWindow

matplotlib.use('Qt5Agg')  # Make sure that we are using QT5

###############
### GLOBALS ###
###############

progname = 'Pyk-A-Boo'
progversion = "0.5.2"


#####################
### start program ###
#####################

def main():
    app = QtWidgets.QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())


if __name__ == '__main__':  # runs only if file is executed, not when it's imported
    main()
