import pandas as pd

from transforms.transform_utils import (
    normalize_language,
    normalize_topics,
    count_frames,
    cluster_articles_by_title,
)

#1. --------------------------------------------------------------
# Checks that language codes and names are normalized correctly
# and that empty or missing values are handled safely.
def test_normalize_language_basic():
    assert normalize_language("eng") == "English"
    assert normalize_language("Swedish") == "Swedish"
    assert normalize_language("") is None
    assert normalize_language(None) is None

#2. --------------------------------------------------------------
# Different topic spellings are normalized to a single format. environment/climate = environment_climate
def test_normalize_topics_alias_and_scoring():
    aliases = normalize_topics(["environment & climate", "science"])
    assert aliases == ["environment_climate", "science"]

#3. --------------------------------------------------------------
# Checks that the text mentiones the narrative frames  we are looking for (war, humanitarian, sanctions)
def test_count_frames_hits_expected_frames():
    text = (
        "The war caused civilian displacement and humanitarian aid deliveries "
        "amid new economic sanctions."
    )
    #scores goes through text and finds keywords, counts how many hits it gets and returns nr of hits
    assert scores["Conflict & War"] > 0
    scores = count_frames(text) 
    assert scores["Humanitarian Impact"] > 0
    assert scores["Sanctions & Pressure"] > 0

#4. --------------------------------------------------------------
# Checks that similar news headlines are grouped together, while unrelated ones remain separate.
def test_cluster_articles_by_title_groups_similar_headlines():
    data = pd.DataFrame(
        {
            "title": [
                "Russia invades Ukraine in latest offensive",#cluster
                "Ukraine invasion by Russia continues", #cluster
                "Completely different sports headline", #not in the cluster
            ],
            "published_at": pd.to_datetime(
                ["2025-01-02", "2025-01-01", "2025-01-03"], utc=True
            ),
        }
    ) # after being added to a df, clusters compare texts, calculates titles 
    # IF = threshold 0.25 = appear in the same cluster. IF 0 = 100%different 1.0 = identical 
    # max 10 can be in the same cluster
    clusters = cluster_articles_by_title(data, limit=10, threshold=0.25)
    # Expect at least one cluster with the two similar headlines
    assert any(len(c) == 2 for c in clusters)
