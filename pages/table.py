import pandas as pd
import os

# Define file paths
OUTPUT_DIR = "Output"
PLOTS_DIR = os.path.join(OUTPUT_DIR, "Assets")
os.makedirs(PLOTS_DIR, exist_ok=True)

def add_country_to_completion_data(location_file, completion_file, output_file):
    """Merge location-to-country mapping with completion data."""
    location_df = pd.read_csv(location_file)
    completion_df = pd.read_csv(completion_file)

    location_df['country'] = location_df['country'].replace({
        'UAE': 'United Arab Emirates',
    })
    completion_df['Location'] = completion_df['Location'].replace({
        'Abu Dhabi': 'Abu Dhabi',
    })

    merged_df = pd.merge(completion_df, location_df[['Site', 'country']], left_on='Location', right_on='Site', how='left')
    merged_df = merged_df.drop_duplicates(subset='Location')
    merged_df.to_csv(output_file, index=False)
    print(f"Updated file saved to: {output_file}")

def generate_html_table(input_file):
    """Generate an interactive HTML table with filters."""
    data = pd.read_csv(input_file)
    html_table = data.to_html(classes='table table-striped', index=False)

    activity_options = data['Activity'].unique().tolist()
    region_options = data['Region'].unique().tolist()
    category_options = data['Category'].unique().tolist()
    location_options = data['Location'].unique().tolist()
    country_options = data['country'].unique().tolist()

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Filterable Data Table</title>
        <link rel="stylesheet" href="https://cdn.datatables.net/1.11.5/css/jquery.dataTables.css">
        <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
        <script src="https://cdn.datatables.net/1.11.5/js/jquery.dataTables.js"></script>
    </head>
    <body>
        <h1>Interactive Data Table with Filters</h1>
        <div class="filter-container">
            <label>Activity:</label>
            <select id="activity-filter">
                <option value="">All</option>
                {"".join([f'<option value="{option}">{option}</option>' for option in activity_options])}
            </select>
            <label>Region:</label>
            <select id="region-filter">
                <option value="">All</option>
                {"".join([f'<option value="{option}">{option}</option>' for option in region_options])}
            </select>
        </div>
        {html_table}
        <script>
            $(document).ready(function() {{
                $('table').DataTable();
                $('#activity-filter').on('change', function() {{
                    $('table').DataTable().column(0).search(this.value).draw();
                }});
                $('#region-filter').on('change', function() {{
                    $('table').DataTable().column(1).search(this.value).draw();
                }});
            }});
        </script>
    </body>
    </html>
    """
    output_html_path = os.path.join(PLOTS_DIR, "filterable_data_table.html")
    with open(output_html_path, 'w') as f:
        f.write(html_content)
    print(f"HTML table saved to: {output_html_path}")

if __name__ == "__main__":
    # Example file paths
    location_file = os.path.join(OUTPUT_DIR, "filled_0_1.csv")
    completion_file = os.path.join(OUTPUT_DIR, "completion_rates_with_activity_region.csv")
    output_file = os.path.join(OUTPUT_DIR, "completion_rates_with_activity_region_with_country.csv")

    # Step 1: Add country data
    add_country_to_completion_data(location_file, completion_file, output_file)

    # Step 2: Generate HTML table with filters
    generate_html_table(output_file)
