import requests
import pandas as pd 
from typing import Dict, List, Any

GUTENDEX_BASE = "https://gutendex.com/books"
GOOGLE_BOOK_BASE = "https://www.googleapis.com/books/v1/volumes"

_ALLOWED_PARAMS = [
    "search", "languages", "topic", "mime_type", "sort", "ids", "copyright", "author_year_start", "author_year_end" 
]

def build_query(parms: Dict[str, str]) -> Dict[str, str]:
    q = {}
    for k in _ALLOWED_PARAMS:
        v = (parms.get(k) or "").strip()
        if v:
            q[k] = v
    return q

def fetch_gutendex(parms: Dict[str, str], max_pages: int = 3) -> List[Dict[str, Any]]:
    if max_pages < 1 or max_pages > 5:
        raise ValueError("max_pages måste vara mellan 1 och 5")
    pages = []
    url = GUTENDEX_BASE
    query = build_query(parms)  # Build the query from parameters
    for _ in range(max_pages):
        r = requests.get(url, params=query, timeout=20)
        r.raise_for_status()
        data = r.json()
        pages.append(data)
        nxt = data.get("next")
        if not nxt: 
            break
        url = nxt
        query = None   # Nästa URL innehåller redan alla parametrer
    return pages

def normalize_books_to_df(pages: List[Dict[str, Any]]) -> pd.DataFrame:
    rows = []
    for page in pages:
        for b in page.get("results", []):
            authors = b.get("authors", [])
            author_names = ", ".join(a.get("name", "") for a in authors)
            main_author = authors[0].get("name") if authors else None
            birth = authors[0].get("birth_year") if authors else None
            death = authors[0].get("death_year") if authors else None
            langs = ",".join(b.get("languages", []))
            subjects = "; ".join(b.get("subjects", []))
            shelves = "; ".join(b.get("bookshelves", []))
            fmts = b.get("formats", {})
            cover = fmts.get("image/jpeg")
            text_plain = fmts.get("text/plain; charset=utf-8") or fmts.get("text/plain")
            downloads = b.get("download_count", 0)
            rows.append({
                "id": b.get("id"),
                "title": b.get("title"),
                "main_author": main_author,
                "author_names": author_names,
                "author_birth_year": birth,
                "author_death_year": death,
                "languages": langs,
                "subjects": subjects,
                "bookshelves": shelves,
                "cover_url": cover,
                "text_url": text_plain,
                "download_count": int(downloads or 0)
            })
    df = pd.DataFrame(rows)
    if not df.empty:
        df["download_count"] = pd.to_numeric(df["download_count"], errors="coerce").fillna(0).astype(int)
    return df

def aggregate_by_language(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["language","book_count"])
    exploded = df.assign(language=df["languages"].str.split(",")).explode("language")
    exploded["language"] = exploded["language"].fillna("").str.strip()
    agg = exploded.groupby("language").size().reset_index(name="book_count")
    return agg.sort_values("book_count", ascending=False)

def aggregate_by_author(df: pd.DataFrame, top_n: int = 20) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["main_author","book_count","total_downloads"])
    agg = (df.groupby("main_author", dropna=True)
             .agg(book_count=("id","count"), total_downloads=("download_count","sum"))
             .reset_index()
             .sort_values(["book_count","total_downloads"], ascending=False))
    return agg.head(top_n)

def enrich_with_google_books(df_subset: pd.DataFrame) -> list:
    results = []
    for _, row in df_subset.iterrows():
        title = row.get("title") or ""
        author = row.get("main_author") or ""
        q = f"intitle:{title} inauthor:{author}".strip() or title
        try:
            r = requests.get(GOOGLE_BOOK_BASE, params={"q": q, "maxResults": 1}, timeout=10)
            r.raise_for_status()
            items = r.json().get("items", [])
            if not items:
                results.append({"title": title, "main_author": author, "description": None, "thumbnail": None})
                continue
            info = items[0].get("volumeInfo", {})
            desc = info.get("description")
            thumb = (info.get("imageLinks") or {}).get("thumbnail")
            results.append({"title": title, "main_author": author, "description": desc, "thumbnail": thumb})
        except Exception:
            results.append({"title": title, "main_author": author, "description": None, "thumbnail": None})
    return results