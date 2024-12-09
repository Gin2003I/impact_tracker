import os
import pandas as pd
from dash import dcc, html
from utils import Header

# Define constants for paths
OUTPUT_ASSETS_DIR = "Output/Assets"
PLOT_FILE = os.path.join(OUTPUT_ASSETS_DIR, "comparison_of_IST_IPS_ISI.html")
CSV_FILE = "Output/completion_rates_with_activity_region.csv"

# Load and process data for the KPI table
def get_kpi_completion_data():
    if not os.path.exists(CSV_FILE):
        raise FileNotFoundError(f"CSV file not found at path: {CSV_FILE}")

    df = pd.read_csv(CSV_FILE)

    # Preprocess columns (remove '%' and convert to float)
    for col in ['Environment', 'Health & Safety', 'Social']:
        df[col] = df[col].str.replace('%', '', regex=False).astype(float)

    # Calculate averages for each activity
    kpi_columns = ['Environment', 'Health & Safety', 'Social']
    ist_data = df[df['Activity'] == 'IST'][kpi_columns].mean()
    ips_data = df[df['Activity'] == 'IPS'][kpi_columns].mean()
    isi_data = df[~df['Activity'].isin(['IST', 'IPS'])][kpi_columns].mean()

    # Create a DataFrame for table display
    table_data = pd.DataFrame({
        'KPI': kpi_columns,
        'IST Completion Rate (%)': ist_data.values,
        'IPS Completion Rate (%)': ips_data.values,
        'ISI Completion Rate (%)': isi_data.values
    })

    return table_data.round(0)  # Round values to integers

# Render the existing plot file
def create_comparison_plot():
    if not os.path.exists(PLOT_FILE):
        return html.Div(
            f"Error: Plot file not found at {PLOT_FILE}.",
            style={"color": "red", "font-size": "16px", "text-align": "center"},
        )

    # Load the plot directly from the specified path
    with open(PLOT_FILE, "r", encoding="utf-8") as file:
        plot_html = file.read()

    return html.Div(
        [
            html.Iframe(
                srcDoc=plot_html,  # Using srcDoc to embed the plot directly from the HTML content
                style={"width": "100%", "height": "500px", "border": "none"},
            )
        ]
    )

# Create the table dynamically
def create_kpi_table():
    df = get_kpi_completion_data()

    table_header = [html.Tr([html.Th(col) for col in df.columns])]
    table_body = [
        html.Tr([html.Td(value) for value in row])
        for row in df.itertuples(index=False, name=None)
    ]

    return html.Table(
        table_header + table_body,
        className="table table-bordered table-hover",
        style={"margin-top": "20px", "font-size": "14px", "width": "80%", "margin-left": "auto", "margin-right": "auto"}
    )

# Main layout function
def create_layout(app):
    # Set the background color to match the gray shade of the header
    background_color = "#F4F6F9"  # Color to match the header's gray background

    return html.Div(
        children=[  
            Header(app),  # Use the Header from utils
            html.Div(
                children=[
                    html.Div(
                        [
                            # Row 1: KPI Comparison Plot
                            html.Div(
                                [
                                    html.H6("KPI Comparison (IST, IPS, ISI)", className="subtitle padded"),
                                    create_comparison_plot(),
                                ],
                                className="row",
                                style={"width": "100%"}  # No flexbox applied here, just full width
                            ),
                            # Row 2: KPI Completion Table
                            html.Div(
                                [
                                    html.H6("KPI Completion Rates", className="subtitle padded"),
                                    create_kpi_table(),
                                ],
                                className="row",
                                style={"width": "100%"}  # No flexbox applied here, just full width
                            ),
                        ],
                        className="sub_page",
                        style={
                            "width": "100%",
                            "minHeight": "100vh",
                            "textAlign": "center",
                            "padding": "20px",
                            "background-color": background_color,  # Set background color to the gray shade
                        },
                    ),
                ],
                className="page",
                style={"width": "100%", "height": "100vh", "display": "block", "overflow": "auto"},
            ),
        ],
        className="page",
    )
