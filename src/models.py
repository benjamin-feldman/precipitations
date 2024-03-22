import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans, AgglomerativeClustering, DBSCAN
from sklearn.pipeline import make_pipeline
from sklearn.metrics import silhouette_score

FEATURES = ['duration', 'max_intensity', 'mean_intensity', 'variance', 'percentage_null']