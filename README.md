# programering2_grupp

Gutendex API Book

Gutendex API Book is a Flask web application. This application retrieves and displays book information from the Gutendex API. We have also used the Google Books API for data enrichment capabilities.
-- Features

Search for books by title or author

Show authors, number of books and downloads

Show language of books and number of books in each language
View details and full text of books
Enrich information with Google Books (book descriptions and covers)

Save last search in browser cookie
Simple user interface with HTML, CSS and Bootstrap

-- Installation and execution steps

git clone <repo-url>
cd Gutendex_API_Book/backend
python -m venv venv
source venv/bin/activate # Linux/Mac
venv\Scripts\activate # Windows
pip install -r requirements.txt
python app.py

If you install this application on the local system, you can run it on http://127.0.0.1:5000. However, to install and run on a personal server or VPS, you must also change the host and port values ​​and configure the DNS settings according to the domain.

The API is available in the /api path.

Sample API Paths
LR flowchart
A[Client / Browser] -->|GET /api/search| B[Gutendex API]
B --> C[Normalize & Aggregate Data]
C --> D[Response JSON]
A -->|GET /api/enrich| E[Google Books API]
E --> C

Book Search: /api/search?search=<query>&pages=2
Top Authors: /api/stats/authors?search=<query>&pages=2&top=50
Book Languages: /api/stats/languages?search=<query>&pages=2
Book Enrichment: /api/enrich?search=<query>&pages=2&limit=10

Project Structure
backend/
├── app.py # Flask Execution
├── api.py # Blueprint API
├── utils.py # Helper Functions
├── views.py # HTML Paths
├── requirements.txt # Packages
├── static/ # CSS and JS
└── templates/ # HTML Templates
tests/ # Tests with pytest

User Interface

Pages: Home, Search, Authors, Languages, Book Details, Full Text, Error Pages

Design Responsive with Bootstrap

Sample Screenshots
Home Search Authors

(Please add screenshots in docs/screenshots/)

Project Testing
pytest ../tests

test_api.py : Endpoint Testing

test_utils.py : Utility Testing

test_views.py : View Path Testing

Development and Customization

Add new features to views.py and templates

Change the look with CSS or another framework

Extend the API or add new resources

License

MIT License