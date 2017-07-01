import pandas
from pandas import DataFrame
import matplotlib.pyplot as plt
from itertools import cycle

from sklearn.cluster import AgglomerativeClustering
from sklearn.cluster import MeanShift, estimate_bandwidth, DBSCAN
import numpy as np
import time
from sklearn.neighbors import kneighbors_graph
from sklearn.preprocessing import StandardScaler


def makeMeanShiftClasterization(materials_data_list):
    commonSourceMeasureDataFrame = materials_data_list[0].table.copy()

    for i in range(1, len(materials_data_list)):
        commonSourceMeasureDataFrame = pandas.concat([commonSourceMeasureDataFrame, materials_data_list[i].table],axis=0,ignore_index=True)

    X = commonSourceMeasureDataFrame.values
    print('Ada:',X)
    bandwidth = estimate_bandwidth(X, quantile=0.10, n_samples=X.shape[0])

    ms = MeanShift(bandwidth=bandwidth, bin_seeding=True)
    ms.fit(X)
    labels = ms.labels_
    cluster_centers = ms.cluster_centers_
    for ind, center in enumerate(cluster_centers):
        print("Cluster:"+str(ind), center)

    labels_unique = np.unique(labels)
    n_clusters_ = len(labels_unique)

    print("number of estimated clusters : %d" % n_clusters_)

    plt.figure(1)
    plt.clf()

    colors = cycle('bgrcmykbgrcmykbgrcmykbgrcmyk')
    for k, col in zip(range(n_clusters_), colors):
        my_members = labels == k
        cluster_center = cluster_centers[k]
        plt.plot(X[my_members, 0], X[my_members, 1], col + '.')
        plt.plot(cluster_center[0], cluster_center[1], 'o', markerfacecolor=col,
                 markeredgecolor='k', markersize=14)
    # plt.title('Estimated number of clusters: %d' % n_clusters_)
    # plt.show()


def makeMeanShiftClasterizationByAngles(filenames, commonSourceMeasureDataFrame, quantile=0.25):
    x = commonSourceMeasureDataFrame.values
    bandwidth = estimate_bandwidth(x, quantile=quantile, n_samples=x.shape[0])

    ms = MeanShift(bandwidth=bandwidth, bin_seeding=True)
    ms.fit(x)
    labels = ms.labels_
    cluster_centers = ms.cluster_centers_
    labels_unique = np.unique(labels)
    n_clusters_ = len(labels_unique)

    plt.figure(1)
    plt.clf()

    colors = cycle('bgrcmykbgrcmykbgrcmykbgrcmyk')
    for k, col in zip(range(n_clusters_), colors):
        my_members = labels == k
        cluster_center = cluster_centers[k]
        plt.plot(x[my_members, 0], x[my_members, 1], col + '.')
        plt.plot(cluster_center[0], cluster_center[1], 'o', markerfacecolor=col,
                 markeredgecolor='k', markersize=20)

    for label, x, y in zip(filenames, x[:, 0], x[:, 1]):
        plt.annotate(
            label,
            xy=(x, y), xytext=(0, 10),
            textcoords='offset points', ha='center', va='bottom')

    result_string = ''
    if hasattr(ms, 'cluster_centers_'):
        centers = ms.cluster_centers_
        result_string = 'Предсказанное количество кластеров:' + str(len(centers)) + '\n'
        result_string += 'Центры кластеров:\n'
        for index, center in enumerate(centers):
            result_string += ' ' + str(index) + ') X: ' + str(center[0]) + ', Y:' + str(center[1]) + '\n'
    return result_string





def makeDBSCANClasterizationByAngles(filenames, commonSourceMeasureDataFrame, eps = 0.1):

    X = StandardScaler().fit_transform(commonSourceMeasureDataFrame.values)
    dbscan = DBSCAN(eps=eps)
    t0 = time.time()
    dbscan.fit(X)
    t1 = time.time()
    if hasattr(dbscan, 'labels_'):
        y_pred = dbscan.labels_.astype(np.int)
    else:
        y_pred = dbscan.predict(X)

    plt.subplot(111)
    colors = np.array([x for x in 'bgrcmykbgrcmykbgrcmykbgrcmyk'])
    colors = np.hstack([colors] * 20)
    plt.scatter(X[:, 0], X[:, 1], color=colors[y_pred].tolist(), s=50)

    if hasattr(dbscan, 'cluster_centers_'):
        centers = dbscan.cluster_centers_
        center_colors = colors[:len(centers)]
        plt.scatter(centers[:, 0], centers[:, 1], s=100, c=center_colors)
    # plt.xlim(-2, 2)
    # plt.ylim(-2, 2)


    for label, x, y in zip(filenames, X[:, 0], X[:, 1]):
        plt.annotate(
            label,
            xy=(x, y), xytext=(0, 10),
            textcoords='offset points', ha='center', va='bottom')

    plt.xticks(())
    plt.yticks(())
    plt.text(.99, .01, ('%.2fs' % (t1 - t0)).lstrip('0'),
             transform=plt.gca().transAxes, size=15,
             horizontalalignment='right')

    result_string = ''
    if hasattr(dbscan, 'cluster_centers_'):
        centers = dbscan.cluster_centers_
        result_string = 'Предсказанное количество кластеров:' + str(len(centers)) + '\n'
        result_string += 'Центры кластеров:\n'
        for index, center in enumerate(centers):
            result_string += ' ' + str(index) + ') X: ' + str(center[0]) + ', Y:' + str(center[1]) + '\n'
    return result_string




def makeWardClasterizationByAngles(filenames, commonSourceMeasureDataFrame, clasters, n_neighbors = 5):

    X = StandardScaler().fit_transform(commonSourceMeasureDataFrame.values)

    # connectivity matrix for structured Ward
    connectivity = kneighbors_graph(X, n_neighbors=n_neighbors, include_self=False)
    # make connectivity symmetric
    connectivity = 0.5 * (connectivity + connectivity.T)

    ward = AgglomerativeClustering(n_clusters=clasters, linkage='ward', connectivity=connectivity)
    t0 = time.time()
    ward.fit(X)
    t1 = time.time()
    if hasattr(ward, 'labels_'):
        y_pred = ward.labels_.astype(np.int)
    else:
        y_pred = ward.predict(X)

    plt.subplot(111)
    colors = np.array([x for x in 'bgrcmykbgrcmykbgrcmykbgrcmyk'])
    colors = np.hstack([colors] * 20)

    plt.scatter(X[:, 0], X[:, 1], color=colors[y_pred].tolist(), s=100)


    if hasattr(ward, 'cluster_centers_'):
        centers = ward.cluster_centers_
        center_colors = colors[:len(centers)]
        plt.scatter(centers[:, 0], centers[:, 1], s=100, c=center_colors)
    plt.xlim(-2, 2)
    plt.ylim(-2, 2)
    plt.xticks(())
    plt.yticks(())
    plt.text(.99, .01, ('%.2fs' % (t1 - t0)).lstrip('0'),
             transform=plt.gca().transAxes, size=15,
             horizontalalignment='right')


    for label, x, y in zip(filenames, X[:, 0], X[:, 1]):
        plt.annotate(
            label,
            xy=(x, y), xytext=(0, 10),
            textcoords='offset points', ha='center', va='bottom')

    result_string = ''
    if hasattr(ward, 'cluster_centers_'):
        centers = ward.cluster_centers_
        result_string = 'Предсказанное количество кластеров:' + str(len(centers)) + '\n'
        result_string += 'Центры кластеров:\n'
        for index, center in enumerate(centers):
            result_string += ' ' + str(index) + ') X: ' + str(center[0]) + ', Y:' + str(center[1]) + '\n'
    return result_string


