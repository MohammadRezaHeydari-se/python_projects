import pandas as pd
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
from utils import build_query, normalize_books_to_df, aggregate_by_author, aggregate_by_language

def test_build_query_strips_and_filters():
    q = build_query({"search":"  dickens  ","foo":"bar","languages":"en"})
    assert "foo" not in q and q["search"]=="dickens" and q["languages"]=="en"

def test_normalize_books_empty():
    df = normalize_books_to_df([])
    assert df.empty

def test_aggregations_minimal():
    df = pd.DataFrame([
        {"id":1,"main_author":"A","download_count":5,"languages":"en"},
        {"id":2,"main_author":"A","download_count":7,"languages":"en"},
        {"id":3,"main_author":"B","download_count":3,"languages":"fr"},
    ])
    a = aggregate_by_author(df, top_n=10)
    assert a.iloc[0]["main_author"] == "A"
    l = aggregate_by_language(df)
    assert l["book_count"].sum() == 3