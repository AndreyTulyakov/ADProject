import pandas
from PyQt5.QtWidgets import QFileDialog
from pandas import DataFrame
import matplotlib.pyplot as plt
import math
import numpy as np


class MeasureData:

    def __init__(self, name):
        self.name = name
        self.table = DataFrame()
        self.channelMean = []
        self.channelMedian = []
        self.channelStd = []
        self.channelVar = []
        self.filename = ''
        self.normalized = False

    def loadFromFile(self, filename):
        self.filename = filename
        self.table = pandas.read_csv(self.filename, index_col=None)

    def loadFromFileByFullFilename(self, full_filename):
        self.filename = full_filename
        self.table = pandas.read_csv(full_filename, index_col=None)

    def calculateMainValues(self):
        self.channelMean = []
        self.channelMedian = []
        self.channelStd = []
        self.channelVar = []
        for channelIndex in range(1, 10):
            currentChannelName = 'CH' + str(channelIndex)
            self.channelMean.append(np.mean(self.table[currentChannelName]))
            self.channelMedian.append(np.median(self.table[currentChannelName]))
            self.channelStd.append(np.std(self.table[currentChannelName]))
            self.channelVar.append(np.var(self.table[currentChannelName]))

    def getShortFilename(self):
        return self.filename[self.filename.rfind('/')+1:]

class SubstanceGroup:
    def __init__(self, name, color):
        self.name = name
        self.color = color
        self.data_list = list()







def printDataMainValues(data):
    print('\nВещество:', data.filename)
    print('\tСреднее по каналу:', data.channelMean)
    print('\tМедиана по каналу:', data.channelMedian)
    print('\tСтандартное отклонение по каналу:', data.channelStd)
    print('\tДисперсия по каналу:', data.channelVar)


def calculateDistance(firstData, secondData):
    result = 0
    for i in range(9):
        value = abs(firstData.channelMean[i] - secondData.channelMean[i])
        result = result + (value * value)
    return math.sqrt(value)

def loadMeasureDataFromFileList(input_files, folder):
    result_data_list = []
    for filename in input_files:
        try:
            measure_data = MeasureData(filename)
            measure_data.loadFromFile(folder + '/' + filename)
            measure_data.calculateMainValues()
            result_data_list.append(measure_data)
        except:
            print('FAIL TO LOAD:', filename)

    return result_data_list



def showCorrelationAndMeans(materials_data_list):
    for i in range(0, len(materials_data_list)):
        channelsCorrelation = []

        firstMaterial = materials_data_list[i - 1]
        secondMaterial = materials_data_list[i]

        # Высчитываем показатели по каждому каналу 1-9
        for channelIndex in range(1, 10):
            currentChannelName = 'CH' + str(channelIndex)
            channelsCorrelation.append(
                np.corrcoef(firstMaterial.table[currentChannelName], secondMaterial.table[currentChannelName])[0, 1])

        print('Корреляции между каналами [' + firstMaterial.filename + '] и [' + secondMaterial.filename + ']')
        # print(channelsCorrelation)
        if (max(channelsCorrelation) < 0.5):
            print('Слабая корреляция', 'MAX:', max(channelsCorrelation))
        else:
            print('Сильная корреляция', 'MAX:', max(channelsCorrelation))

        if (i < 9):
            plt.subplot(3, 3, i + 1)
            plt.title('CORR[' + firstMaterial.filename + '-' + secondMaterial.filename + ']')
            plt.bar(range(1, 10), channelsCorrelation, 0.75, color="blue")
            plt.ylabel('VALUE')
            plt.grid(True)
    plt.show()

    for firstMaterial in materials_data_list:
        for secondMaterial in materials_data_list:
            print('Расстояние между центрами [' + firstMaterial.filename + '] и [' + secondMaterial.filename + ']',
                  calculateDistance(firstMaterial, secondMaterial))

    # Генерация графиков
    plt.subplot(2, 2, 1)
    plt.title('MEAN')
    for material in materials_data_list:
        plt.plot(range(1, 10), material.channelMean, 'o-')
    plt.ylabel('VALUE')
    plt.grid(True)

    plt.subplot(2, 2, 2)
    plt.title('MEDIAN')
    for material in materials_data_list:
        plt.plot(range(1, 10), material.channelMedian, 'o-')
    plt.ylabel('VALUE')
    plt.grid(True)

    plt.subplot(2, 2, 3)
    plt.title('STD')
    for material in materials_data_list:
        plt.plot(range(1, 10), material.channelStd, 'o')

    plt.ylabel('VALUE')
    plt.grid(True)
    plt.legend(loc='upper left', shadow=False, fontsize='medium')

    plt.subplot(2, 2, 4)
    plt.title('VAR (DISPER)')
    for material in materials_data_list:
        plt.plot(range(1, 10), material.channelVar, 'o', label=material.filename)

    plt.ylabel('VALUE')
    plt.grid(True)
    plt.legend(loc='upper left', shadow=False, fontsize='medium')

    plt.show()



def showMeansByChannel(materials_data_list):
    colors = ['green', 'blue', 'black']

    for channelIndex in range(1, 10):
        currentChannelName = 'CH' + str(channelIndex)

        plt.subplot(3, 3, channelIndex)
        plt.title('CH'+str(channelIndex))
        plt.ylabel('VALUE')
        plt.grid(True)
        #ax.set(ylim=[1, 200])

        for ind, mater in enumerate(materials_data_list):
            channel_data = np.mean(mater.table[currentChannelName])
            plt.bar([ind], channel_data, 0.75, color = colors[int(ind/3)])
            #plt.plot([ind], channel_data, 'o-')
    plt.show()


def show_measures_data(material):
    plt.title(material.filename)
    for index, row in material.table.iterrows():

        plt.plot(range(1, 10), row.tolist(), 'o-', label=material.filename, )#linestyle='dotted')
        plt.ylabel('VALUE')
        plt.grid(True)
    plt.show()


def filterDataByStd(materials_data_list, output_folder):
    for material in materials_data_list:
        material.calculateMainValues(material)

    for material in materials_data_list:
        for channelIndex in range(0, 9):
            currentChannelName = 'CH' + str(channelIndex + 1)
            max_value = (material.channelMedian[channelIndex] + material.channelStd[channelIndex] * 2)
            min_value = (material.channelMedian[channelIndex] - material.channelStd[channelIndex] * 2)
            material.table = material.table.query(currentChannelName + ' < ' + str(max_value))
            material.table = material.table.query(currentChannelName + ' > ' + str(min_value))
        if len(material.table.index) > 0 :
            if output_folder is not None:
                material.table.to_csv(output_folder + material.filename, index=False)
        else:
            materials_data_list.remove(material)

    for material in materials_data_list:
        material.calculateMainValues(material)
    return materials_data_list

def angle_point(a, b, c):
    x1 = a[0] - b[0]
    x2 = c[0] - b[0]
    y1 = a[1] - b[1]
    y2 = c[1] - b[1]
    d1 = np.sqrt(x1 * x1 + y1 * y1)
    d2 = np.sqrt(x2 * x2 + y2 * y2)
    return np.arccos((x1 * x2 + y1 * y2) / (d1 * d2))

def calculateAnglesFromMeans(mean_values):
    result = []

    for i in range(-2, len(mean_values)-2):
        angle = angle_point([i, mean_values[i]], [i+1, mean_values[i+1]], [i+2, mean_values[i+2]])
        result.append(angle)
    return result


def getDirFromUserSelection(path = '', parent = None):
    dir_name = QFileDialog.getExistingDirectory(parent, "Выбрать каталог", path)
    if (len(dir_name) > 0):
        return dir_name
    else:
        return None

def getFilenamesFromUserSelection(path = '', filename_mask = "Text Files (*.txt)", parent = None):
    filenames, _ = QFileDialog.getOpenFileNames(parent, "Выбрать файлы", path, filename_mask, None)
    return filenames


# Записывает/перезаписывает строку любой длины c переносами (data_str) в файл (filename)
def writeStringToFile(data_str, filename, strict_utf8_encoding=False):
    try:
        if(strict_utf8_encoding):
            with open(filename, 'w', encoding='utf-8') as out_text_file:
                out_text_file.write(data_str)
        else:
            with open(filename, 'w') as out_text_file:
                out_text_file.write(data_str)
    except PermissionError:
        print("ERROR!", "NO ACCESS TO FILE:", filename, ' - CLOSE OTHER APPLICATIONS')
        exit(-1)