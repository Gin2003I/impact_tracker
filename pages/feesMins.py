import os
import pandas as pd
from dash import dcc, html
from utils import Header

# Define constants for paths
BASE_DIR = os.getcwd()  # Base directory
ASSETS_DIR = os.path.join("Output", "Assets")  # Custom assets directory
COMPLETION_MAP_FILE = os.path.join(ASSETS_DIR, "grand_total_map.html")  # Pre-existing map file
CSV_FILE = os.path.join("Output", "completion_rates_with_activity_region.csv")

# Helper function to preprocess columns
def preprocess_columns(df, columns):
    for col in columns:
        df[col] = df[col].str.replace('%', '', regex=False).astype(float)
    return df

# Render the existing map file
def render_completion_map():
    if not os.path.exists(COMPLETION_MAP_FILE):
        return html.Div(
            f"Error: Completion map file not found at {COMPLETION_MAP_FILE}.",
            style={"color": "red", "font-size": "16px", "text-align": "center"},
        )

    # Load the map directly from the specified path
    with open(COMPLETION_MAP_FILE, "r", encoding="utf-8") as file:
        map_html = file.read()

    return html.Div(
        [
            html.Iframe(
                srcDoc=map_html,  # Using srcDoc to embed the map directly from the HTML content
                style={
                    "width": "80%",  # Limit the width to 80% of the page width
                    "height": "500px",  # Limit the height to 500px
                    "border": "none",  # Remove border
                    "overflow": "hidden",  # Prevent scrollbars
                    "margin": "0 auto",  # Center the map
                    "display": "block",  # Ensure the map is block-aligned
                },
            )
        ],
        style={"text-align": "center", "overflow": "hidden"}  # Center the container and hide overflow
    )


# Generate region completion table
def create_region_completion_table(input_file):
    if not os.path.exists(input_file):
        print(f"Error: File not found -> {input_file}")
        return html.Div(f"Error: Input file missing -> {input_file}")
    try:
        df = pd.read_csv(input_file)
        df = preprocess_columns(df, ['Environment', 'Health & Safety', 'Social', 'Grand Total'])

        # Calculate averages for regions
        regions = ['EUROPE', 'LATAM', 'MEA', 'APAC', 'NORAM']
        avg_completions = []
        for region in regions:
            region_data = df[df['Region'] == region]
            if not region_data.empty:
                avg_completions.append({
                    'Region': region,
                    'Environment': round(region_data['Environment'].mean()),
                    'Health & Safety': round(region_data['Health & Safety'].mean()),
                    'Social': round(region_data['Social'].mean()),
                    ' Total': round(region_data['Grand Total'].mean())
                })

        avg_df = pd.DataFrame(avg_completions)

        # Convert to HTML table
        table_header = [html.Tr([html.Th(col) for col in avg_df.columns])]
        table_body = [
            html.Tr([html.Td(value) for value in row])
            for row in avg_df.itertuples(index=False, name=None)
        ]

        return html.Table(
            table_header + table_body,
            className="table table-bordered table-hover",
            style={"margin-top": "20px", "font-size": "14px", "width": "80%", "margin-left": "auto", "margin-right": "auto"}
        )
    except Exception as e:
        print(f"Error generating region completion table: {e}")
        return html.Div("Error processing data.")

# Main layout
def create_layout(app):
    return html.Div(
        children=[
            Header(app),
            html.Div(
                children=[
                    # Row 1: Interactive Map
                    html.Div(
                        [
                            html.H6("Global Completion Map", className="subtitle padded"),
                            render_completion_map()
                        ],
                        className="row",
                        style={"width": "100%"}
                    ),
                    # Row 2: Region Completion Table
                    html.Div(
                        [
                            html.H6("Region Completion Rates", className="subtitle padded"),
                            create_region_completion_table(CSV_FILE)
                        ],
                        className="row",
                        style={"width": "100%"}
                    ),
                ],
                className="sub_page"
            )
        ],
        className="page"
    )
