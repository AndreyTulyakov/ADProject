#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pandas import DataFrame
import numpy as np

from utils import calculateAnglesFromMeans


def special_normalization(materials_data_list):
    for index, material in enumerate(materials_data_list):
        # TODO: Двойная и тройная нормализация могут улучшить кластерные кучи но по хорошему их нужно отключить.
        #if material.normalized == True:
        #    continue
        for i in range(-2, len(material.channelMean) - 2):
            norma = np.linalg.norm([material.channelMean[i], material.channelMean[i + 1], material.channelMean[i + 2]])
            material.channelMean[i + 1] = material.channelMean[i + 1] / norma
            material.normalized = True
    for material in materials_data_list:
        material.channelMean[0] = 0
    return materials_data_list

def calculate_all_angle_measure(materials_data_list):
    for index, material in enumerate(materials_data_list):
        material.mean_angles = calculateAnglesFromMeans(material.channelMean)
        current_row = [b + a / 10 for a, b in zip(material.channelMean, material.mean_angles)]
        material.mixed_data_measure = current_row
    return materials_data_list

def generate_angle_measure_dataframe(materials_data_list):
    columns = [str('A' + str(i + 1)) for i in range(len(materials_data_list[0].mean_angles))]
    all_mean_angles = DataFrame(columns=columns)
    for index, material in enumerate(materials_data_list):
        all_mean_angles.loc[index] = material.mixed_data_measure
    return all_mean_angles

def show_measures_means(materials_data_list, plt):
    for ind, material in enumerate(materials_data_list):

        if material.filename.startswith('N'):
            plt.plot(range(1, 10), material.channelMean, 'ro-', label=material.filename)

        if material.filename.startswith('TOK'):
            plt.plot(range(1, 10), material.channelMean, 'go-', label=material.filename)

        if material.filename.startswith('AS'):
            plt.plot(range(1, 10), material.channelMean, 'bo-', label=material.filename)

        if material.filename.startswith('G'):
            plt.plot(range(1, 10), material.channelMean, 'yo-', label=material.filename)

    plt.ylabel('VALUE')
    plt.xlabel('CHANNEL')
    plt.grid(True)
    plt.show()
