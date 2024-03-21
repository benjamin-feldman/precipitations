import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans, AgglomerativeClustering, DBSCAN
from sklearn.pipeline import make_pipeline
from sklearn.metrics import silhouette_score

# Constants
N_CLUSTERS = 3
FEATURES = ['duration', 'max_intensity', 'mean_intensity', 'variance', 'percentage_null']

# Data Preprocessing
def preprocess_data(df, features):
    X = df[features]
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    return X_scaled

def apply_kmeans(X, n_clusters):
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    labels = kmeans.fit_predict(X)
    return labels

def apply_agglomerative(X, n_clusters):
    agglomerative = AgglomerativeClustering(n_clusters=n_clusters)
    labels = agglomerative.fit_predict(X)
    return labels

def apply_dbscan(X, eps=0.5, min_samples=5):
    dbscan = DBSCAN(eps=eps, min_samples=min_samples)
    labels = dbscan.fit_predict(X)
    return labels

# Evaluation
def evaluate_clustering(X, labels):
    silhouette_avg = silhouette_score(X, labels)
    print(f'Silhouette Score: {silhouette_avg:.2f}')

# Main Function
def main():
    # Load and preprocess the data
    df = pd.read_pickle("data/dataframes/2018_07.pkl")
    X_scaled = preprocess_data(df, FEATURES)

    # Apply KMeans Clustering
    labels_kmeans = apply_kmeans(X_scaled, N_CLUSTERS)
    df['label_kmeans'] = labels_kmeans
    evaluate_clustering(X_scaled, labels_kmeans)

    # Apply Agglomerative Clustering
    labels_agglo = apply_agglomerative(X_scaled, N_CLUSTERS)
    df['label_agglo'] = labels_agglo
    evaluate_clustering(X_scaled, labels_agglo)

    # Apply DBSCAN
    labels_dbscan = apply_dbscan(X_scaled)
    df['label_dbscan'] = labels_dbscan
    evaluate_clustering(X_scaled, labels_dbscan)

    # Save the resultant dataframe
    df.to_csv('clustered_data.csv', index=False)

if __name__ == '__main__':
    main()
