#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QMessageBox
from PyQt5 import QtCore, uic
from PyQt5.QtWidgets import QListWidgetItem
from matplotlib.figure import Figure
import matplotlib.pyplot as plt


from modules.DataPreprocessing import special_normalization, calculate_all_angle_measure, \
    generate_angle_measure_dataframe
import matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import (FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar)

from utils import MeasureData
from utils import getFilenamesFromUserSelection
from utils import writeStringToFile
matplotlib.use('Qt5Agg')
from modules.ClasteringFunctions import *


class ClasterizationWindow(QDialog):

    def __init__(self):
        super().__init__()
        uic.loadUi('windows/ClasterizationWindow.ui', self)
        flags = Qt.Window | Qt.WindowSystemMenuHint | Qt.WindowMinimizeButtonHint  |  Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint
        self.setWindowFlags(flags)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.data_preprocessed = False

        fig = Figure()
        self.addmpl(fig)

        self.on_change_method()

        self.buttonSelectInputFiles.clicked.connect(self.on_button_select_input_files_clicked)
        self.buttonRemoveInputFiles.clicked.connect(self.on_button_remove_input_files_clicked)
        self.buttonClastering.clicked.connect(self.on_button_clastering_clicked)

        self.radioButtonMeanShift.toggled.connect(self.on_change_method)
        self.radioButtonWard.toggled.connect(self.on_change_method)
        self.radioButtonDBSCAN.toggled.connect(self.on_change_method)

        self.tabWidget.setCurrentIndex(0)

    # Команды для построения графиков
    def addfig(self, fig):
        self.rmmpl()
        self.addmpl(fig)

    def addmpl(self, fig):
        self.canvas = FigureCanvas(fig)
        self.mplvl.addWidget(self.canvas)
        self.canvas.draw()
        self.toolbar = NavigationToolbar(self.canvas, self.mplwindow, coordinates=True)
        self.GraphicsLayout.addWidget(self.toolbar)

    def rmmpl(self, ):
        self.mplvl.removeWidget(self.canvas)
        self.canvas.close()
        self.mplvl.removeWidget(self.toolbar)
        self.toolbar.close()

    # Нажатие на кнопку добавления входных файлов
    def on_button_select_input_files_clicked(self):
        filenames = getFilenamesFromUserSelection('', 'Comma separated values (*.csv)', self)
        self.buttonSelectInputFiles.setText('Добавить файлы...')
        for filename in filenames:
            try:
                name = filename[filename.rfind('/')+1:filename.rfind('.')]
                measure_data = MeasureData(name)
                measure_data.loadFromFileByFullFilename(filename)
                measure_data.calculateMainValues()

                item = QListWidgetItem(measure_data.getShortFilename())
                item.setData(QtCore.Qt.UserRole, measure_data)
                self.listFilenames.addItem(item)
            except:
                print('FAIL TO LOAD:', filename)

    # Нажатие на кнопку удаления входных файлов
    def on_button_remove_input_files_clicked(self):
        items = self.listFilenames.selectedItems();
        if not items:
            return
        for item in items:
            self.listFilenames.takeItem(self.listFilenames.row(item))

    # Выбор другого метода кластеризации
    def on_change_method(self):
        self.settingPanelMeanShift.setVisible(self.radioButtonMeanShift.isChecked())
        self.settingPanelWard.setVisible(self.radioButtonWard.isChecked())
        self.settingPanelDBSCAN.setVisible(self.radioButtonDBSCAN.isChecked())

    # Нажатие на кнопку кластеризации
    def on_button_clastering_clicked(self):
        self.tabWidget.setCurrentIndex(2)
        self.textEdit.append('Запуск процесса кластеризации...')

        plt.cla()
        plt.clf()
        self.textEdit.setText('')

        if not self.data_preprocessed:
            self.all_data = [self.listFilenames.item(x).data(QtCore.Qt.UserRole) for x in range(self.listFilenames.count())]
            self.textEdit.append('Нормализация...')
            self.materials_data_list = special_normalization(self.all_data)
            self.textEdit.append('Рассчет новых мер...')
            self.materials_data_list = calculate_all_angle_measure(self.materials_data_list)
            self.textEdit.append('Формирование данных...')
            self.all_mean_angles = generate_angle_measure_dataframe(self.materials_data_list)
            self.data_preprocessed = True
        else:
            self.textEdit.append('Использование предыдущих результатов препроцессинга...')

        filenames = [material.getShortFilename() for material in self.materials_data_list]

        if self.radioButtonMeanShift.isChecked():
            self.textEdit.append('Кластеризация методом MeanShift...')
            quantile = self.spinBoxMeanShiftQuantile.value()
            result = makeMeanShiftClasterizationByAngles(filenames, self.all_mean_angles, quantile)
            self.textEdit.append(str(result))

        if self.radioButtonWard.isChecked():
            self.textEdit.append('Кластеризация методом Ward...')
            clusters_count = self.spinBoxWardClustersCount.value()
            neighbors_count = self.spinBoxWardNeighborsCount.value()
            result = makeWardClasterizationByAngles(filenames, self.all_mean_angles, clusters_count, neighbors_count)
            self.textEdit.append(str(result))


        if self.radioButtonDBSCAN.isChecked():
            self.textEdit.append('Кластеризация методом DBSCAN...')
            eps = self.SpinBoxDBSCAN_Eps.value()
            result = makeDBSCANClasterizationByAngles(filenames, self.all_mean_angles, eps)
            self.textEdit.append(str(result))

        writeStringToFile(self.textEdit.toPlainText(), 'output/clasterization_results.txt')



        self.addfig(plt.gcf())
        self.textEdit.append('Завершено')








