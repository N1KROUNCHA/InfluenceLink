import pandas as pd
from app.db.mysql import conn

def load_dataset():
    query = """
    SELECT
      subscriber_count,
      video_count,
      avg_views,
      engagement_score
    FROM influencers
    WHERE engagement_score IS NOT NULL
    """

    df = pd.read_sql(query, conn)

    X = df.drop(columns=["engagement_score"])
    y = df["engagement_score"]

    return X, y
