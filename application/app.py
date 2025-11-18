from flask import Flask, render_template, request, abort, redirect, url_for, jsonify
import pandas as pd
import requests
from datetime import datetime, timedelta
import plotly.graph_objs as go
from plotly.offline import plot

app = Flask(__name__)

_cached_df = None

@app.route('/', methods=['GET', 'POST'])
def home():
    data_html = None
    year = mounth = day = price = None

    if request.method == 'POST':
        # Get form data
        year = request.form.get('year')
        mounth = request.form.get('mounth')
        day = request.form.get('day')
        price = request.form.get('price')

        # Basic validation: check if all fields are filled
        if not all([year, mounth, day, price]):
            return redirect(url_for('error_page', code=400, message="Alla fält måste fyllas i!"))

        # Check that year, month, and day are numeric
        if not (year.isdigit() and mounth.isdigit() and day.isdigit()):
            return redirect(url_for('error_page', code=400, message="År, månad och dag måste vara siffror!"))

        # Convert to int for comparison
        year = int(year)
        mounth = int(mounth)
        day = int(day)

        # Validate price zone (SE1–SE4)
        valid_prices = ["SE1", "SE2", "SE3", "SE4"]
        if price not in valid_prices:
            return redirect(url_for('error_page', code=400, message="Ogiltig priszon! Välj mellan SE1, SE2, SE3 eller SE4."))

        # Validate date
        try:
            user_date = datetime(year, mounth, day)
        except ValueError:
            return redirect(url_for('error_page', code=400, message="Ogiltigt datum! Kontrollera år, månad och dag."))

        today = datetime.now()
        one_day_ahead = today + timedelta(days=1)
        min_date = datetime(2022, 11, 1)

        # Check if date is earlier than 2022-11-01
        if user_date < min_date:
            return redirect(url_for('error_page', code=400, message="Datumet får inte vara tidigare än 2022-11-01."))

        # Check if the date is more than one day ahead (fixed)
        if user_date.date() > one_day_ahead.date():
            return redirect(url_for('error_page', code=400, message="Det angivna datumet får inte vara mer än en dag framåt."))

        #  API endpoint
        api_url = f"https://www.elprisetjustnu.se/api/v1/prices/{year}/{str(mounth).zfill(2)}-{str(day).zfill(2)}_{price}.json"

        # Send request to API
        response = requests.get(api_url)

        if response.status_code == 200:
            json_data = response.json()

            # Convert JSON data to DataFrame
            df = pd.DataFrame(json_data)
            global _cached_df
            _cached_df = df

            # Format time to hh:mm
            if 'time_start' in df.columns:
                df['time_start'] = pd.to_datetime(df['time_start']).dt.strftime('%H:%M')
            if 'time_end' in df.columns:
                df['time_end'] = pd.to_datetime(df['time_end']).dt.strftime('%H:%M')

            # Generate HTML table
            data_html = df.to_html(classes='table table-striped', index=False)
        else:
            return redirect(url_for('error_page', code=404, message=f"Kunde inte hämta data från API ({response.status_code})."))

    return render_template('index.html', data=data_html, year=year, mounth=mounth, day=day, price=price)

@app.route('/diagram')
def diagram():
    if _cached_df is None:
       abort(404, description="Ingen data för diagrammet.")

    df = _cached_df

    # Check for required columns
    required_cols = ['time_start', 'SEK_per_kWh']
    if not all(col in df.columns for col in required_cols):
        return redirect(url_for('error_page', code=404, message="Data innehåller inte nödvändiga kolumner."))

    # Create line chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['time_start'], 
        y=df['SEK_per_kWh'], 
        mode='lines+markers',
        name='SEK per kWh'
    ))

    fig.update_layout(
        title='Elpris Diagram (SEK per kWh)',
        xaxis_title='Tid (hh:mm)',
        yaxis_title='Pris (SEK/kWh)'
    )

    # Convert chart to HTML
    plot_div = plot(fig, output_type='div', include_plotlyjs=True)
    return render_template('diagram.html', plot_div=plot_div)


"""
Error handling
"""
@app.errorhandler(400)
def bad_request(error):
    message = getattr(error, 'description', "Ogiltig begäran! Kontrollera dina inmatningar.")
    return render_template('error.html', code=400, message=message), 400

@app.errorhandler(404)
def page_not_found(error):
    message = getattr(error, 'description', "Sidan du letar efter kunde inte hittas!")
    return render_template('error.html', code=404, message=message), 404

@app.errorhandler(500)
def internal_error(error):
    message = getattr(error, 'description', "Internt serverfel! Försök igen senare.")
    return render_template('error.html', code=500, message=message), 500


# Generic route for displaying errors
@app.route('/error')
def error_page():
    code = request.args.get('code', default=400, type=int)
    message = request.args.get('message', default="Ett okänt fel har inträffat.")
    return render_template('error.html', code=code, message=message), code


if __name__ == '__main__':
    app.run(debug=True)
