#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QDialog, QMessageBox
from PyQt5 import QtCore, uic
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QListWidgetItem
from sklearn.externals import joblib
from sklearn.neighbors import KNeighborsClassifier

from modules.DataPreprocessing import calculate_all_angle_measure, special_normalization
from utils import getDirFromUserSelection, MeasureData, getFilenamesFromUserSelection, writeStringToFile


class ClassificationWindow(QDialog):

    def __init__(self):
        super().__init__()
        uic.loadUi('windows/ClassificationWindow.ui', self)
        flags = Qt.Window | Qt.WindowSystemMenuHint | Qt.WindowMinimizeButtonHint |  Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint
        self.setWindowFlags(flags)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.classificator = None

        self.buttonAddFile.clicked.connect(self.on_button_add_file_clicked)
        self.buttonRemoveFile.clicked.connect(self.on_button_remove_file_clicked)
        self.buttonSelectDump.clicked.connect(self.on_button_select_dump_clicked)
        self.buttonClassify.clicked.connect(self.on_button_classify_clicked)


    def on_button_add_file_clicked(self):
        filenames = getFilenamesFromUserSelection('', 'Comma separated values file (*.csv)', self)
        for filename in filenames:
            item = QListWidgetItem(filename)
            self.listFilenames.addItem(item)

    def on_button_remove_file_clicked(self):
        items = self.listFilenames.selectedItems()
        if not items:
            return
        for item in items:
            self.listFilenames.takeItem(self.listFilenames.row(item))

    def on_button_select_dump_clicked(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Выбрать файл с дампом", '', "Classificator dump (*.cdump)", None)
        if len(filename) > 0:
            self.classificator = joblib.load(filename)
            self.labelClassificatorDumpFilename.setText(filename)


    def on_button_classify_clicked(self):
        if self.classificator is None:
            QMessageBox.information(self, "Внимание", "Сначала загрузите дамп\n обученного классификатора!")
            return

        filenames = [self.listFilenames.item(x).text() for x in range(self.listFilenames.count())]
        if len(filenames) < 1:
            QMessageBox.information(self, "Внимание", "Нет данных для классификации.\n Загрузите хотя бы один файл.")
            return

        self.tabWidget.setCurrentIndex(1)

        all_data = []

        for filename in filenames:
            try:
                name = filename[filename.rfind('/')+1:filename.rfind('.')]
                measure_data = MeasureData(name)
                measure_data.loadFromFileByFullFilename(filename)
                measure_data.calculateMainValues()
                all_data.append(measure_data)
            except:
                print('FAIL TO LOAD:', filename)

        self.textEdit.append('Нормализация...')
        materials_data_list = special_normalization(all_data)
        self.textEdit.append('Рассчет новых мер...')
        materials_data_list = calculate_all_angle_measure(materials_data_list)
        self.textEdit.append('Формирование данных...')

        materials_test_list = [material.mixed_data_measure for material in materials_data_list]
        results = self.classificator.predict(materials_test_list)
        results_proba = self.classificator.predict_proba(materials_test_list)

        for index, (result, result_proba) in enumerate(zip(results, results_proba)):
            self.textEdit.append("Файл:" + materials_data_list[index].filename)
            self.textEdit.append("    Классифицирован: " + str(result))
            self.textEdit.append("    Вероятностная классификация:")
            for proba, classname in zip(result_proba, self.classificator.classes_):
                self.textEdit.append('        > ' + str(classname) + ': ' + str(proba))
            self.textEdit.append('')

        writeStringToFile(self.textEdit.toPlainText(), 'output/classification_results.txt')






