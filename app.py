import os
import sys
import webbrowser
import dash
from dash import dcc, html
from dash.dependencies import Input, Output

# Import the function to run preprocessing
from preprocess import check_and_run_preprocessing

# Initialize the Dash app
app = dash.Dash(__name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}])
app.title = "Financial Report"
server = app.server

# Layout of the app
app.layout = html.Div([dcc.Location(id="url", refresh=False), html.Div(id="page-content")])

@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def display_page(pathname):
    from pages import overview, pricePerformance, portfolioManagement, feesMins

    if pathname == "/dash-financial-report/price-performance":
        return pricePerformance.create_layout(app)
    elif pathname == "/dash-financial-report/portfolio-management":
        return portfolioManagement.create_layout(app)
    elif pathname == "/dash-financial-report/fees":
        return feesMins.create_layout(app)
    elif pathname == "/dash-financial-report/full-view":
        return (
            overview.create_layout(app),
            pricePerformance.create_layout(app),
            portfolioManagement.create_layout(app),
            feesMins.create_layout(app),
        )
    else:
        return overview.create_layout(app)

def run_dashboard():
    """Run preprocessing first, then start the Dash app."""
    try:
        # Run preprocessing step
        print("Running preprocessing step...")
        file_name = "Filled_not filled.csv"  # Adjust this if needed
        preprocessing_done = check_and_run_preprocessing(file_name)

        if preprocessing_done:
            print("Preprocessing completed successfully.")
        else:
            print("Preprocessing skipped as it was already completed.")

        # Start the Dash app after preprocessing
        port = 8050
        url = f"http://127.0.0.1:{port}"
        print(f"Dashboard will be available at {url}")
        webbrowser.open(url)  # Open the app in a browser
        app.run_server(debug=False, use_reloader=False)  # Prevents Dash from restarting itself

    except Exception as e:
        print(f"Error occurred during preprocessing or dashboard startup: {e}")
        sys.exit(1)  # Exit if there's an error

if __name__ == "__main__":
    run_dashboard()  # Start the entire process
