#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re

from sklearn.externals import joblib
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QDialog, QMessageBox
from PyQt5 import QtCore, uic
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QInputDialog
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QListWidgetItem
from PyQt5.QtWidgets import QTableWidgetItem
from sklearn.neighbors import KNeighborsClassifier
from modules.DataPreprocessing import calculate_all_angle_measure, special_normalization
from utils import getDirFromUserSelection, MeasureData, getFilenamesFromUserSelection, writeStringToFile
from windows.LabelEditWindow import LabelEditWindow


class ClassificatorLearningWindow(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi('windows/ClassificatorLearningWindow.ui', self)
        flags = Qt.Window | Qt.WindowSystemMenuHint | Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint
        self.setWindowFlags(flags)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.current_edit_classname = None
        self.neigh_classificator_data = None

        self.buttonAddFile.clicked.connect(self.on_button_add_file_clicked)
        self.buttonRemoveFile.clicked.connect(self.on_button_remove_file_clicked)

        self.buttonAddClass.clicked.connect(self.on_button_add_class_clicked)
        self.buttonRemoveClass.clicked.connect(self.on_button_remove_class_clicked)

        self.buttonChangeLabel.clicked.connect(self.on_button_change_label_clicked)
        self.buttonLoadLabelingInfo.clicked.connect(self.on_button_load_labeling_info_clicked)
        self.buttonSaveLabelingInfo.clicked.connect(self.on_button_save_labeling_info_clicked)

        self.buttonTrainClassificator.clicked.connect(self.on_button_train_classificator_clicked)
        self.buttonSaveClassificatorDump.clicked.connect(self.on_button_save_classificator_dump_clicked)


    def on_button_add_file_clicked(self):
        filenames = getFilenamesFromUserSelection('', 'Comma separated values file (*.csv)', self)
        for filename in filenames:
            item = QListWidgetItem(filename)
            self.listFiles.addItem(item)
        self.regenerate_table()

    def on_button_remove_file_clicked(self):
        items = self.listFiles.selectedItems()
        if not items:
            return
        for item in items:
            self.listFiles.takeItem(self.listFiles.row(item))
        self.regenerate_table()

    def on_button_add_class_clicked(self):
        (text, truth) = QInputDialog.getText(self, "Добавление класса", "Наименование класса:", QLineEdit.Normal, "")
        if truth:
            item = QListWidgetItem(text)
            self.listClasses.addItem(item)
            self.regenerate_table()

    def on_button_remove_class_clicked(self):
        items = self.listClasses.selectedItems()
        if not items:
            return
        for item in items:
            self.listClasses.takeItem(self.listClasses.row(item))
        self.regenerate_table()

    def regenerate_table(self):
        all_filenames = [self.listFiles.item(x).text() for x in range(self.listFiles.count())]
        all_classes = [self.listClasses.item(x).text() for x in range(self.listClasses.count())]

        for i in range(self.listLabels.count()):
            item = self.listLabels.item(i).text().split('==>')
            filename = item[0].strip()
            classname = item[1].strip()
            if filename in all_filenames:
                all_filenames.remove(filename)
            else:
                self.listLabels.takeItem(self.listLabels.row(self.listLabels.item(i)))

        for filename in all_filenames:
            item = QListWidgetItem(filename + ' ==> ?')
            self.listLabels.addItem(item)

        # Для свежих добавленных ставим класс ?
        for i in range(self.listLabels.count()):
            text = self.listLabels.item(i).text()
            item = text.split('==>')
            filename = item[0].strip()
            classname = item[1].strip()
            if classname not in all_classes:
                self.listLabels.item(i).setText(filename + ' ==> ?')



    def on_button_change_label_clicked(self):
        all_classes = [self.listClasses.item(x).text() for x in range(self.listClasses.count())]
        self.current_edit_classname = None

        items = self.listLabels.selectedItems()
        if items:
            item = items[0].text().split('==>')
            filename = item[0].strip()
            edit_window = LabelEditWindow(self, filename, all_classes)
            edit_window.exec()
            if self.current_edit_classname is not None:
                items[0].setText(filename + ' ==> ' + self.current_edit_classname)


    def on_button_load_labeling_info_clicked(self):
        filename = QFileDialog.getOpenFileName(self, 'Загрузка файла', filter = "Labeling information text file (*.lbinfo)")[0]
        if len(filename) > 0:
            classes = dict()
            filenames = dict()

            with open(filename, 'r') as file:
                self.listLabels.clear()
                self.listFiles.clear()
                self.listClasses.clear()

                for index, line in enumerate(file):
                    line = line.replace('\n', '')
                    if len(line) > 0 and (line.find('==>') > 0):
                        item = line.split('==>')
                        filename = item[0].strip()
                        filenames[filename] = 1
                        classname = item[1].strip()
                        classes[classname] = 1
                        item = QListWidgetItem(line)
                        self.listLabels.addItem(item)

                for filename in filenames.keys():
                        self.listFiles.addItem(QListWidgetItem(filename))

                for classname in classes.keys():
                    if classname != '?':
                        self.listClasses.addItem(QListWidgetItem(classname))
                QMessageBox.information(self, "Внимание", "Загрузка файла успешно завершена!")


    def on_button_save_labeling_info_clicked(self):
        filename = QFileDialog.getSaveFileName(self, 'Сохранение файла', filter = "Labeling information text file (*.lbinfo)")[0]
        if len(filename) > 0:
            result = ''
            for i in range(self.listLabels.count()):
                current_record = self.listLabels.item(i).text()
                result = result + current_record + '\n'
            result = result[:result.rfind('\n')]
            writeStringToFile(result, filename)



    def on_button_train_classificator_clicked(self):
        records = [self.listLabels.item(x).text() for x in range(self.listLabels.count())]
        filenames = []
        classes = []
        for record in records:
            item = record.split('==>')
            filename = item[0].strip()
            classname = item[1].strip()
            if classname != '?':
                filenames.append(filename)
                classes.append(classname)

        all_data = []

        for filename, classname in zip(filenames,classes):
            try:
                name = filename[filename.rfind('/')+1:filename.rfind('.')]
                measure_data = MeasureData(name)
                measure_data.classname = classname
                measure_data.loadFromFileByFullFilename(filename)
                measure_data.calculateMainValues()
                all_data.append(measure_data)
            except:
                print('FAIL TO LOAD:', filename)

        materials_data_list = special_normalization(all_data)
        materials_data_list = calculate_all_angle_measure(materials_data_list)
        train_data = []
        train_labels = []

        for material in materials_data_list:
            train_labels.append(material.classname)
            train_data.append(material.mixed_data_measure)

        self.neigh_classificator_data = KNeighborsClassifier(n_neighbors=3)
        self.neigh_classificator_data.fit(train_data, train_labels)

        QMessageBox.information(self, "Внимание", "Классификатор обучен!")


    def on_button_save_classificator_dump_clicked(self):
        if self.neigh_classificator_data is None:
            QMessageBox.information(self, "Внимание", "Сначала обучите классификатор!")
            return
        filename = QFileDialog.getSaveFileName(self, 'Сохранение файла', filter="Classificator dump (*.cdump)")[0]
        if len(filename) > 0:
            _ = joblib.dump(self.neigh_classificator_data, filename, compress=9)

