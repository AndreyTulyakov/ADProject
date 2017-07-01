#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog
from PyQt5 import QtCore, uic
from PyQt5.QtWidgets import QMessageBox

from modules.MConverter import MConverter
from utils import getDirFromUserSelection


class MConverterWindow(QDialog):

    def __init__(self):
        super().__init__()
        uic.loadUi('windows/MConverterWindow.ui', self)
        self.setWindowFlags(Qt.Window | Qt.WindowSystemMenuHint | Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.buttonSelectInputPath.clicked.connect(self.button_select_input_path_clicked)
        self.buttonSelectOutputPath.clicked.connect(self.button_select_output_path_clicked)
        self.buttonConvert.clicked.connect(self.button_convert_clicked)

    def button_select_input_path_clicked(self):
        input_dir = getDirFromUserSelection('', self)
        if input_dir:
            self.lineInputPath.setText(input_dir)

    def button_select_output_path_clicked(self):
        output_dir = getDirFromUserSelection('', self)
        if output_dir:
            self.lineOutputPath.setText(output_dir)

    def button_convert_clicked(self):

        if len(self.lineInputPath.text()) < 1:
            QMessageBox.information(self, "Внимание", "Укажите входной каталог!")
            return

        if len(self.lineOutputPath.text()) < 1:
            QMessageBox.information(self, "Внимание", "Укажите выходной каталог!")
            return

        self.buttonSelectInputPath.setEnabled(False)
        self.buttonSelectOutputPath.setEnabled(False)
        self.buttonConvert.setEnabled(False)

        input_filenames_list = os.listdir(self.lineInputPath.text())
        input_filenames_list = [filename for filename in input_filenames_list if filename.endswith('.m') or filename.endswith('.M')]

        self.textEdit.append('Всего обнаружено *.m файлов:' + str(len(input_filenames_list)))

        for input_filename in input_filenames_list:
            input_filename = self.lineInputPath.text() + '/' + input_filename
            output_filename = input_filename[input_filename.rfind('/')+1:]
            self.textEdit.append('Обработка файла: ' + output_filename)
            output_filename = output_filename[:output_filename.rfind('.')] + '.csv'
            output_filename = self.lineOutputPath.text() + '/' + output_filename
            MConverter.convert_m_to_csv(input_filename, output_filename)

        self.textEdit.append('Успешно завершено.')
        self.buttonSelectInputPath.setEnabled(True)
        self.buttonSelectOutputPath.setEnabled(True)
        self.buttonConvert.setEnabled(True)

        QMessageBox.information(self, "Внимание", "Процесс успешно окончен!\nКонвертировано файлов:" + str(len(input_filenames_list)))




        

