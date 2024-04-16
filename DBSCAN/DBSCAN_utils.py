import numpy as np
from fastdtw import fastdtw
from scipy.spatial.distance import euclidean
import matplotlib.pyplot as plt
import os
from sklearn.cluster import DBSCAN
from concurrent.futures import ProcessPoolExecutor
import concurrent.futures
import pickle

def data_importation(year=2018, month=1, day=1):
    # Constructs the path to a numpy data file based on year, month, and day
    # and loads it as an array while converting negative values to NaN.
    path = os.path.join(os.path.dirname(os.path.dirname(os.getcwd())), 'data', '{:04d}'.format(year))
    file = 'RR_IDF300x300_{:04d}{:02d}{:02d}.npy'.format(year, month, day)
    file = os.path.join(path, file)
    RR = np.load(file) / 100.0
    RR[RR < 0] = np.nan  # Replace negative values with NaN
    return RR

def dtw_distance(x, y):
    # Calculates the Dynamic Time Warping distance between two time series x and y.
    distance, _ = fastdtw(x, y)
    return distance

def calculate_distance_matrix(RR, x_start=0, x_end=10, y_start=0, y_end=10, distance_function=dtw_distance):
    # Validates the specified indices and calculates a distance matrix for the subsection of RR
    # using the specified distance function (default is DTW).
    if x_end > 300 or y_end > 300 or x_start < 0 or y_start < 0:
        print("Index problem: Check the boundaries.")
        return None
    selected_data = RR[:, x_start:x_end, y_start:y_end]
    num_series = selected_data.shape[1] * selected_data.shape[2]
    distance_matrix = np.zeros((num_series, num_series))
    for i in range(num_series):
        for j in range(i + 1, num_series):
            x_i, y_i = divmod(i, selected_data.shape[2])
            x_j, y_j = divmod(j, selected_data.shape[2])
            ts1 = selected_data[:, x_i, y_i]
            ts2 = selected_data[:, x_j, y_j]
            distance = distance_function(ts1, ts2)
            distance_matrix[i, j] = distance_matrix[j, i] = distance
    return distance_matrix

def DBSCAN_Slinding_Window(RR, longitude_max=2, latitude_max=2, step=9, width=10, eps=10, min_samples=2, metric=dtw_distance):
    # Applies DBSCAN clustering to data within a sliding window across the dataset RR.
    # Returns dictionaries mapping cluster information, labels, and core points indices.
    dbscan = DBSCAN(eps=eps, min_samples=min_samples, metric=metric)
    dict_clusters = {}
    dict_labels = {}
    core_points = {}
    for i in range(longitude_max):
        for j in range(latitude_max):
            data = RR[:, i*step:width+i*step, j*step:width+j*step].reshape(-1, 288)
            dbscan.fit(data)
            cluster_key = f"cluster({i},{j})"
            label_key = f"labels({i},{j})"
            core_points_key = f"core_points({i},{j})"
            dict_clusters[cluster_key] = dbscan
            dict_labels[label_key] = dbscan.labels_.reshape(width, width)
            core_points[core_points_key] = dbscan.core_sample_indices_
    return dict_clusters, dict_labels, core_points

def DBSCAN_DP(longitude_max=2, latitude_max=2, step=9, width=10, eps=10, min_samples=2):
    # Loads precomputed distance matrices and applies DBSCAN clustering.
    # Returns dictionaries with clustering results, labels, and core points indices.
    dbscan = DBSCAN(eps=eps, min_samples=min_samples, metric='precomputed')
    with open(f'distance_matrices_width={width}_step={step}.pkl', 'rb') as f:
        d_loaded = pickle.load(f)
    dict_clusters = {}
    dict_labels = {}
    core_points = {}
    for i in range(longitude_max):
        for j in range(latitude_max):
            matrix_key = f"distance_matrix{i},{j}"
            if matrix_key in d_loaded:
                dbscan.fit(d_loaded[matrix_key])
                cluster_key = f"cluster({i},{j})"
                label_key = f"labels({i},{j})"
                core_points_key = f"core_points({i},{j})"
                dict_clusters[cluster_key] = dbscan
                dict_labels[label_key] = dbscan.labels_.reshape(width, width)
                core_points[core_points_key] = dbscan.core_sample_indices_
    return dict_clusters, dict_labels, core_points

def affichage_clusters(dict_labels, longitude_max, latitude_max):
    # Creates a subplot grid for displaying clustering results based on the provided labels dictionary.
    _, axs = plt.subplots(longitude_max, latitude_max)
    for i in range(longitude_max):
        for j in range(latitude_max):
            axs[i, j].imshow(dict_labels[f"labels({i},{j})"])
            axs[i, j].set_title(f'clusters({i},{j})')
            axs[i, j].axis('off')
    plt.show()

def traduction_core_points_map(step, width, i, j, core_points):
    # Translates core points indices to their respective positions in the subgroup and on the overall map.
    points_groupe = []
    points_map = []
    for point in core_points:
        points_groupe.append({"x_groupe": point % width, "y_groupe": point // width})
        points_map.append({"x_map": i * step + point % width, "y_map": j * step + point // width})
    return points_groupe, points_map




######################## suite a revoir

def merge_clusters_if_shared_core_point(i1, j1, i2, j2, core_points, dict, step, width, running_max_label, processed_labels):
    """
    Merges clusters between two sections of data if they share common core points. This function is used
    to ensure that clusters which are spatially or temporally close and share core points are considered as one.
    
    Args:
    i1, j1, i2, j2: Indices of the sections being compared.
    core_points: Dictionary containing core points indices.
    dict: Dictionary containing cluster labels.
    step: The step size used in the sliding window approach.
    width: The width of the window.
    running_max_label: The current maximum label used in re-labeling to ensure uniqueness across merged clusters.
    processed_labels: Set to track labels that have been processed to avoid duplication.
    
    Returns:
    running_max_label: Updated maximum label after processing this merge.
    dict: Updated dictionary with merged labels.
    """

    # Retrieve core points and labels for both sections
    core_points_1 = core_points[f"core_points({i1},{j1})"]
    core_points_2 = core_points[f"core_points({i2},{j2})"]
    labels_1 = dict[f"labels({i1},{j1})"]
    labels_2 = dict[f"labels({i2},{j2})"]

    # Translate core points to map coordinates to handle them in a unified coordinate system
    _, points_map1 = traduction_core_points_map(step, width, i1, j1, core_points_1)
    _, points_map2 = traduction_core_points_map(step, width, i2, j2, core_points_2)

    # Find common core points between the two sections
    set_core_points1 = {tuple(point.values()) for point in points_map1}
    set_core_points2 = {tuple(point.values()) for point in points_map2}
    common_core_points = set_core_points1.intersection(set_core_points2)

    # Relabel clusters based on shared core points
    for point in common_core_points:
        point_group1 = (point[0] - i1 * step, point[1] - j1 * step)
        point_group2 = (point[0] - i2 * step, point[1] - j2 * step)
        label_1 = labels_1[point_group1[0], point_group1[1]]
        label_2 = labels_2[point_group2[0], point_group2[1]]
        if label_1 != label_2 and label_1 is not None and label_2 is not None:
            for i in range(labels_2.shape[0]):
                for j in range(labels_2.shape[1]):
                    if labels_2[i, j] == label_2:
                        labels_2[i, j] = label_1
            processed_labels.add(label_1)

    # Relabel the remaining points in the second section to ensure they remain unique
    for point in set_core_points2 - common_core_points:
        point_group = (point[0] - i2 * step, point[1] - j2 * step)
        label_to_change = labels_2[point_group[0], point_group[1]]
        if label_to_change not in processed_labels:
            for i in range(labels_2.shape[0]):
                for j in range(labels_2.shape[1]):
                    if labels_2[i, j] == label_to_change:
                        labels_2[i, j] = running_max_label
            processed_labels.add(label_to_change)
            running_max_label += 1

    # Update the labels in the dictionary for both sections
    dict[f"labels({i1},{j1})"] = labels_1
    dict[f"labels({i2},{j2})"] = labels_2

    return running_max_label, dict
