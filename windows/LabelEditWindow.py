#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QDialog, QMessageBox
from PyQt5 import QtCore, uic
from PyQt5.QtWidgets import QInputDialog
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QListWidgetItem
from PyQt5.QtWidgets import QTableWidgetItem
from sklearn.neighbors import KNeighborsClassifier
from modules.DataPreprocessing import calculate_all_angle_measure, special_normalization
from utils import getDirFromUserSelection, MeasureData, getFilenamesFromUserSelection


class LabelEditWindow(QDialog):
    def __init__(self, requester, filename, classes):
        super().__init__()
        uic.loadUi('windows/LabelEditWindow.ui', self)
        flags = Qt.Window | Qt.WindowSystemMenuHint | Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint
        self.setWindowFlags(flags)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.requester = requester
        self.lineFilename.setText(filename)
        self.comboBoxClassname.addItems(classes)
        self.buttonSave.clicked.connect(self.on_button_save_clicked)


    def on_button_save_clicked(self):
        self.requester.current_edit_classname = self.comboBoxClassname.currentText()
        self.close()
