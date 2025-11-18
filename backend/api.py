from flask import Blueprint, request, jsonify, make_response
import json
from backend.utils import (
    build_query, fetch_gutendex, normalize_books_to_df,
    aggregate_by_author, aggregate_by_language,
    enrich_with_google_books
)

api = Blueprint("api", __name__, url_prefix="/api")
COOKIE_NAME = "gutendash_last_query"

def parse_params():
    # 9 parametrar + pages
    fields = ["search","languages","topic","mime_type","sort","ids","copyright",
              "author_year_start","author_year_end"]
    params = {k: (request.args.get(k) or "").strip() for k in fields}
    try:
        pages = int(request.args.get("pages", 3))
    except ValueError:
        pages = 3
    if pages < 1 or pages > 5:
        return None, None, ("pages must be 1..5", 400)
    return params, pages, None

@api.get("/search")
def api_search():
    params, pages, err = parse_params()
    if err: return jsonify({"error": err[0]}), err[1]
    try:
        pages_json = fetch_gutendex(params, max_pages=pages)
    except Exception as e:
        return jsonify({"error": "upstream_error", "detail": str(e)}), 502

    df = normalize_books_to_df(pages_json)
    langs = aggregate_by_language(df).to_dict(orient="records")
    authors = aggregate_by_author(df).to_dict(orient="records")
    return jsonify({
        "count": int(df.shape[0]),
        "books": df.to_dict(orient="records"),
        "languages": langs,
        "authors": authors
    })

@api.get("/stats/languages")
def api_langs():
    params, pages, err = parse_params()
    if err: return jsonify({"error": err[0]}), err[1]
    df = normalize_books_to_df(fetch_gutendex(params, max_pages=pages))
    return jsonify(aggregate_by_language(df).to_dict(orient="records"))

@api.get("/stats/authors")
def api_authors():
    params, pages, err = parse_params()
    if err: return jsonify({"error": err[0]}), err[1]
    try:
        top = int(request.args.get("top", 100))
    except ValueError:
        top = 100
    df = normalize_books_to_df(fetch_gutendex(params, max_pages=pages))
    return jsonify(aggregate_by_author(df, top_n=top).to_dict(orient="records"))

@api.get("/enrich")
def api_enrich():
    params, pages, err = parse_params()
    if err: return jsonify({"error": err[0]}), err[1]
    try:
        limit = int(request.args.get("limit", 20))
    except ValueError:
        limit = 20
    df = normalize_books_to_df(fetch_gutendex(params, max_pages=pages))
    subset = df.head(max(1, min(limit, 50)))
    return jsonify(enrich_with_google_books(subset))

@api.post("/cookie")
def api_set_cookie():
    try:
        payload = request.get_json(force=True)
    except Exception:
        return jsonify({"error": "invalid_json"}), 400
    resp = make_response(("", 204))
    resp.set_cookie(COOKIE_NAME, json.dumps(payload), max_age=60*60*24*30)
    return resp

@api.get("/cookie")
def api_get_cookie():
    raw = request.cookies.get(COOKIE_NAME)
    if not raw:
        return jsonify({"search": "","languages": "","topic": "","mime_type": "","sort": "popular",
                        "ids": "","copyright": "",
                        "author_year_start": "","author_year_end": "","page_size": 3})
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        data = {}
    return jsonify(data)