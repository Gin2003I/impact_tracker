import os
from dash import dcc, html
from utils import Header

# Define constants for paths
ASSETS_DIR = os.path.join("Output", "Assets")  # Custom directory for assets
PLOT_FILE_HEATMAP = os.path.join(ASSETS_DIR, "average_completion_rates_by_region_heatmap.html")
PLOT_FILE_BARCHART = os.path.join(ASSETS_DIR, "average_completion_rates_by_region_without_grand_total.html")

# Function to render a plot from an existing HTML file
def render_plot_from_file(plot_file):
    if not os.path.exists(plot_file):
        return html.Div(
            f"Error: Plot file not found at {plot_file}.",
            style={"color": "red", "font-size": "16px", "text-align": "center"},
        )

    # Load the plot directly from the specified path
    with open(plot_file, "r", encoding="utf-8") as file:
        plot_html = file.read()

    return html.Div(
        [
            html.Iframe(
                srcDoc=plot_html,  # Using srcDoc to embed the plot directly from the HTML content
                style={"width": "100%", "height": "600px", "border": "none"},
            )
        ]
    )

# Main layout function
def create_layout(app):
    return html.Div(
        children=[
            Header(app),  # Use the Header from utils
            html.Div(
                children=[
                    html.Div(
                        [
                            # Row 1: Heatmap
                            html.Div(
                                [
                                    html.H6("Average Completion Rates by Region (Heatmap)", className="subtitle padded"),
                                    render_plot_from_file(PLOT_FILE_HEATMAP),
                                ],
                                className="row",
                                style={"width": "100%"},
                            ),
                            # Row 2: Bar Chart
                            html.Div(
                                [
                                    html.H6("Average Completion Rates by Region (Bar Chart)", className="subtitle padded"),
                                    render_plot_from_file(PLOT_FILE_BARCHART),
                                ],
                                className="row",
                                style={"width": "100%"},
                            ),
                        ],
                        className="sub_page",
                        style={
                            "width": "100%",
                            "minHeight": "297mm",
                            "textAlign": "center",
                            "padding": "20px",
                            "background-color": "white",  # Set background color to white
                        },
                    ),
                ],
                className="page",
                style={"width": "100%", "minHeight": "297mm", "display": "block"},
            ),
        ],
        className="page",
    )

