#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QMainWindow, QSizePolicy, QSpacerItem, QFileDialog, QPushButton


# Класс главного окна
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QWidget

from windows.ClassificationWindow import ClassificationWindow
from windows.ClassificatorLearningWindow import ClassificatorLearningWindow
from windows.ClasterizationWindow import ClasterizationWindow
from windows.MConverterWindow import MConverterWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.texts = []

    def initUI(self):

        button_classification_learn = QPushButton("Обучение классификатора")
        button_classification_learn.setMinimumHeight(32)
        button_classification_learn.clicked.connect(self.classification_learn)

        button_classification = QPushButton("Классификация")
        button_classification.setMinimumHeight(32)
        button_classification.clicked.connect(self.classification)

        button_clasterization = QPushButton("Кластеризация")
        button_clasterization.setMinimumHeight(32)
        button_clasterization.clicked.connect(self.clasterization)

        button_convert_to_csv = QPushButton("Конвертирование m-данных в CSV")
        button_convert_to_csv.setMinimumHeight(32)
        button_convert_to_csv.clicked.connect(self.convert_to_csv)

        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        vbox = QVBoxLayout()

        vbox.addWidget(button_classification_learn)
        vbox.addWidget(button_classification)
        vbox.addWidget(button_clasterization)
        vbox.addWidget(button_convert_to_csv)
        vbox.addItem(spacer)

        widget = QWidget();
        widget.setLayout(vbox);
        self.setCentralWidget(widget);
        self.setGeometry(300, 300, 480, 320)
        self.setWindowTitle('Анализатор спектрофотометрических результатов')
        self.show()

    def common_dialog_start_procedure(self, dialog):
        self.hide()
        dialog.destroyed.connect(self.show)
        dialog.exec_()

    def classification_learn(self):
        self.common_dialog_start_procedure(ClassificatorLearningWindow())

    def classification(self):
        self.common_dialog_start_procedure(ClassificationWindow())

    def clasterization(self):
        self.common_dialog_start_procedure(ClasterizationWindow())

    def convert_to_csv(self):
        self.common_dialog_start_procedure(MConverterWindow())