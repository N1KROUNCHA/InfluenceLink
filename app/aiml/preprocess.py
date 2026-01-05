from sklearn.preprocessing import MinMaxScaler

def normalize_features(df):
    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(df)
    return scaled
