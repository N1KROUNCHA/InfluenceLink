from sklearn.cluster import KMeans

def cluster_influencers(embeddings):
    kmeans = KMeans(n_clusters=10, random_state=42)
    labels = kmeans.fit_predict(embeddings)
    return labels
