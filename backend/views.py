from flask import Blueprint, render_template, request, current_app, make_response
import json
from .utils import fetch_gutendex, normalize_books_to_df, aggregate_by_author, aggregate_by_language, enrich_with_google_books

def register_views(app):
    @app.route("/")
    def index():
        # Health check for backend service
        health = {"ok": True, "service": "gutendach-backend"}

        # Retrieve last search query from cookie, if available
        query = ""
        cookie_raw = request.cookies.get("gutendash_last_query")
        if cookie_raw:
            try:
                cookie_data = json.loads(cookie_raw)
                query = cookie_data.get("search", "")
            except Exception:
                query = ""

        # Render the home page with health info and last search query
        return render_template("index.html", health=health, query=query)


    @app.route("/search", methods=["GET", "POST"])
    def search_view():
        # Initialize variables
        books = None
        query = None

        if request.method == "POST":
            # Get search query submitted by user
            query = request.form.get("search", "").strip()
            pages = int(request.form.get("pages") or 1)

            # Fetch books data from Gutendex API
            pages_json = fetch_gutendex({"search": query}, max_pages=pages)
            df = normalize_books_to_df(pages_json)
            books = df.to_dict(orient="records")

            # Save the search query in a browser cookie for later retrieval
            cookie_data = {"search": query}
            resp = make_response(render_template("search.html", books=books, query=query))
            resp.set_cookie("gutendash_last_query", json.dumps(cookie_data), max_age=60*60*24*30)
            return resp

        # GET request: retrieve the last search query from cookie
        cookie_raw = request.cookies.get("gutendash_last_query")
        if cookie_raw:
            try:
                cookie_data = json.loads(cookie_raw)
                query = cookie_data.get("search", "")
            except Exception:
                query = ""

        # Render search page with either empty or last search query
        return render_template("search.html", books=books, query=query)

    @app.route("/authors")
    def authors_view():
        # Get search query and number of pages from request parameters
        q = request.args.get("search", "")
        pages = int(request.args.get("pages", 1))
        try:
            # Fetch books data and aggregate by authors
            pages_json = fetch_gutendex({"search": q}, max_pages=pages)
            df = normalize_books_to_df(pages_json)
            authors = aggregate_by_author(df, top_n=50).to_dict(orient="records")
        except Exception as e:
            # Render error page if API fails
            return render_template("error.html", code=502, message=str(e)), 502

        # Render authors page with aggregated data
        return render_template("authors.html", authors=authors, query=q)

    @app.route("/languages")
    def languages_view():
        # Get search query and number of pages from request parameters
        q = request.args.get("search", "")
        pages = int(request.args.get("pages", 1))
        try:
            # Fetch books data and aggregate by language
            pages_json = fetch_gutendex({"search": q}, max_pages=pages)
            df = normalize_books_to_df(pages_json)
            langs = aggregate_by_language(df).to_dict(orient="records")
        except Exception as e:
            # Render error page if API fails
            return render_template("error.html", code=502, message=str(e)), 502

        # Render languages page with aggregated data
        return render_template("languages.html", languages=langs, query=q)

    @app.route("/enrich")
    def enrich_view():
        # Get search query, number of pages, and limit for enrichment
        q = request.args.get("search", "")
        pages = int(request.args.get("pages", 1))
        limit = int(request.args.get("limit", 10))
        try:
            # Fetch books data and enrich using Google Books API
            pages_json = fetch_gutendex({"search": q}, max_pages=pages)
            df = normalize_books_to_df(pages_json)
            subset = df.head(max(1, min(limit, 50)))
            enriched = enrich_with_google_books(subset)
        except Exception as e:
            # Render error page if enrichment fails
            return render_template("error.html", code=502, message=str(e)), 502

        # Render enrichment page with enriched book data
        return render_template("enrich.html", items=enriched, query=q)
    
    @app.route("/book/<int:book_id>")
    def book_detail(book_id):
        try:
            pages_json = fetch_gutendex({"ids": str(book_id)}, max_pages=1)
            df = normalize_books_to_df(pages_json)
            if df.empty:
                return render_template("error.html", code=404, message="Book not found"), 404
            book = df.iloc[0].to_dict()

            # Extract all formats
            formats = book.get("formats")
            if not formats or not isinstance(formats, dict):
                formats = {}
            book["formats"] = formats

            # Debug: print formats in terminal
            print("Book formats:", book.get("formats"))

        except Exception as e:
            print("Error fetching book:", e)
            return render_template("error.html", code=502, message=str(e)), 502

        return render_template("book_detail.html", book=book)

    @app.route("/read/<int:book_id>")
    def read_book(book_id):
        try:
            # Fetch book by ID
            pages_json = fetch_gutendex({"ids": str(book_id)}, max_pages=1)
            df = normalize_books_to_df(pages_json)
            if df.empty:
                return render_template("error.html", code=404, message="Book not found"), 404
            book = df.iloc[0].to_dict()

            # Initialize content variable
            full_text = ""
            if book.get("text_url"):
                import requests
                try:
                    r = requests.get(book["text_url"], timeout=15)
                    r.raise_for_status()
                    full_text = r.text  # full text of book
                except Exception:
                    full_text = "Full text not available"

            # Pass full_text to template
            book["full_text"] = full_text

        except Exception as e:
            return render_template("error.html", code=502, message=str(e)), 502

        return render_template("read_book.html", book=book)

    # Error Handlers
    # Handles 404 errors (page not found)
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template(
            "error.html",
            code=404,
            message="Sidan kunde inte hittas (404). Gå tillbaka till startsidan."  # Swedish: Page not found
        ), 404

    # Handles 500 errors (internal server error)
    @app.errorhandler(500)
    def internal_error(error):
        return render_template(
            "error.html",
            code=500,
            message="Ett internt serverfel inträffade. Försök igen senare."  # Swedish: Internal server error
        ), 500

    # Handles any unexpected exception that might occur
    @app.errorhandler(Exception)
    def generic_error(error):
        print("Unhandled exception:", error)  
        return render_template(
            "error.html",
            code=500,
            message="Ett oväntat fel inträffade. Försök igen senare."
        ), 500

