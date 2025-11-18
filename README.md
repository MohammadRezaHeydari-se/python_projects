##Project Introduction

ELPRICE is a Flask web application that displays electricity price information in Sweden and allows users to view price charts and tables for a specific date and region.

The project uses the official elprisetjustnu.se API to retrieve data and displays the data as HTML tables and Plotly graphs.

ــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــ
#Features:

Retrieves electricity price data by date and region (SE1–SE4)
Displays data as HTML tables with Bootstrap classes
Plots electricity price graphs with Plotly
Validation of inputs and error handling
Displays error pages with appropriate messages
Automatic testing with pytest

---
#Short description of files:

app.py: routes and data processing logic, API fetch, error handling and charts
index.html: main page with data entry form and table display
diagram.html: Plotly chart display
base.html: base template and header and footer insertion
header.html and footer.html: header and footer
error.html: error pages display
test_app.py: unit test to check the performance of routes and application logic

---
Technologies and Dependencies

Technologies:

Python 3.11+
Flask 3.1.2
Pandas 2.3.3
Plotly 6.3.1
Bootstrap 5
Requests 2.32.5

---
#Installation and Setup

Clone the project:
git clone <repository_url>
cd ELPRICE

Create a virtual environment:
python -m venv venv
source venv/bin/activate # Linux / Mac
venv\Scripts\activate # Windows

Install packages:
pip install -r requirements.txt

Run the program:
flask --app app run

---
## bash

```bash
git clone <repository_url>
cd ELPRICE
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r requirements.txt
python -m application.app
```


Open a browser and go to:
http://127.0.0.1:5000/
---
#Using the program

On the main page, enter the desired date (year, month, day) and price zone (SE1–SE4).

Click the Hitta information button.

If data is available:
The price table is displayed in HTML
The PRIS Diagram link is enabled to view the diagram
If you enter the wrong date or zone, you will be redirected to an error page.

#Error Management

Error Pages and Input Management:
Date less than 2022-11-01 → Error
Date more than one day ago → Error
Empty or invalid fields → Error
Invalid region → Error
No API access → Error

Errors are displayed in the form of an error.html page with code and message.

Charts

Line chart of electricity prices in SEK per kWh
X-axis: time (hh:mm)
Y-axis: price (SEK/kWh)

Implemented with Plotly and displayed in HTML

#Tests

Tests written with pytest:

GET / → Show homepage
POST / with incomplete data → Check redirect to /error
POST / with wrong date or region → Check redirect to /error
POST / with valid data → Create HTML table
GET /diagram without data → 404 error
GET /diagram with existing data → Show chart
GET /error → Show error message

To run tests:
pytest
pytest -v

#Development

Add support for new regions
Store data in database for historical analysis
Improve UI with JavaScript and Chart.js
Add ability to select date range by multiple days