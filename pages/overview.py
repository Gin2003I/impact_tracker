import os
from dash import dcc, html
from utils import Header  # Assuming the Header utility exists

# Define the folder path where your HTML plots are stored
PLOTS_DIR = "Output/Assets"

# Function to read and return HTML content from files
def get_iframe_src(file_name):
    """Reads the HTML file and returns its content or an error message if not found."""
    file_path = os.path.join(PLOTS_DIR, file_name)
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                return file.read()
        except UnicodeDecodeError:
            with open(file_path, "r", encoding="latin-1") as file:
                return file.read()
    else:
        return f"<h3>Error: File {file_name} not found in {PLOTS_DIR}.</h3>"

# Create the layout for the Overview page
def create_layout(app):
    # Fetch the HTML content for the filterable data table
    table_html = get_iframe_src("filterable_data_table.html")

    return html.Div(
        [
            # Corporate-styled header with navigation
            Header(app),

            # Main content container
            html.Div(
                [
                    # Row 1 - Full-page Iframe (Filterable Data Table)
                    html.Div(
                        [
                            html.Iframe(
                                srcDoc=table_html,  # Display the HTML content in an Iframe
                                style={
                                    "width": "100%",  # Full width
                                    "height": "calc(100vh - 60px)",  # Adjust height to fit the viewport minus the header
                                    "border": "none",
                                },
                            ),
                        ],
                        className="row",
                        style={
                            "width": "100%",
                            "height": "100%",
                            "padding": "0",
                            "margin": "0",
                        },
                    ),
                ],
                className="sub_page",
            ),
        ],
        className="page",
        style={
            "width": "100%",
            "height": "100vh",  # Full viewport height
            "padding": "0",
            "margin": "0",
            "overflow": "hidden",  # Prevent scrolling
        },
    )
