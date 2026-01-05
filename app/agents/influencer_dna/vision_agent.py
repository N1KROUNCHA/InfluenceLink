import requests
import numpy as np
from io import BytesIO
from PIL import Image
from sklearn.cluster import KMeans


def extract_dominant_colors(image_url: str, k: int = 3):
    """
    Extract dominant colors from an image URL.
    Returns list of HEX colors.
    """

    if not image_url:
        return []

    try:
        response = requests.get(image_url, timeout=6)
        if response.status_code != 200:
            return []

        img = Image.open(BytesIO(response.content)).convert("RGB")

        # Resize for speed + stability
        img = img.resize((128, 128))

        pixels = np.array(img).reshape(-1, 3)

        # Edge case: too few pixels
        if len(pixels) < k:
            return []

        kmeans = KMeans(
            n_clusters=k,
            n_init=10,
            random_state=42
        )

        kmeans.fit(pixels)
        centers = kmeans.cluster_centers_.astype(int)

        colors = [
            "#{:02x}{:02x}{:02x}".format(c[0], c[1], c[2])
            for c in centers
        ]

        return colors

    except Exception as e:
        # Silent fail so pipeline never crashes
        return []

