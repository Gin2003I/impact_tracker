import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sys

# Define directories for input and output files
INPUT_DIR = "Input"
OUTPUT_DIR = "Output"
OUTPUT_ASSETS_DIR = os.path.join(OUTPUT_DIR, "Assets")
os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_ASSETS_DIR, exist_ok=True)

# Function to read the parameters from the text file
def read_dashboard_parameters(file_name="dashboard_parameters.txt"):
    # Check if we are running from a bundled .exe
    if getattr(sys, 'frozen', False):
        # Running from a bundled .exe, use _MEIPASS to access bundled files
        bundle_dir = sys._MEIPASS  # Temporary folder where files are extracted
    else:
        # Running from source code
        bundle_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct the path to the dashboard parameters file
    file_path = os.path.join(bundle_dir, file_name)

    # Initialize the parameters dictionary
    parameters = {}

    # Read the parameters file if it exists
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            for line in f.readlines():
                if line.strip():  # Skip empty lines
                    key, value = line.strip().split('=')
                    parameters[key] = int(value) if value.isdigit() else value
    else:
        print(f"Warning: The parameters file '{file_path}' does not exist. Using default values.")
        # Default parameters if the file is not found
        parameters = {
            "year_to_analyze": 2024,
            "current_month": 11
        }
    
    return parameters

# DataImpactTracker Class
class DataImpactTracker:
    def __init__(self, input_file, activity_region_file, output_folder):
        self.input_file = input_file
        self.activity_region_file = activity_region_file
        self.output_folder = output_folder

    @staticmethod
    def transform_completion(value):
        return 1 if value == 'Filled' else 0 if value == 'Not Filled' else value

    def process_completion_data(self):
        if not os.path.exists(self.input_file):
            raise FileNotFoundError(f"File not found: {self.input_file}")
        df = pd.read_csv(self.input_file)
        df['Completion'] = df['Completion'].apply(self.transform_completion)
        processed_file = os.path.join(self.output_folder, "filled_0_1.csv")
        df.to_csv(processed_file, index=False)
        print(f"Processed completion data saved as: {processed_file}")
        return processed_file

    def generate_pivot_table(self, input_file, year=None):
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"File not found: {input_file}")
        df = pd.read_csv(input_file)
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        if year:
            df = df[df['Date'].dt.year == year]
        valid_frequencies = ['month', 'quarter', 'annual']
        df = df[df['Frequency'].str.lower().isin(valid_frequencies)]
        filled_df = df[df['Completion'] == 1]
        count_df = filled_df.groupby(['Site', 'KPI Category']).size().unstack(fill_value=0)
        all_sites = df['Site'].unique()
        all_categories = df['KPI Category'].unique()
        count_df = count_df.reindex(index=all_sites, columns=all_categories, fill_value=0)
        count_df['Total général'] = count_df.sum(axis=1)
        total_row = count_df.sum(axis=0).to_frame().T
        total_row.index = ['Total']
        count_df = pd.concat([count_df, total_row])
        pivot_table_file = os.path.join(self.output_folder, "Completed_Forms_Pivot.csv")
        count_df.to_csv(pivot_table_file, float_format='%.0f')
        print(f"Pivot table saved as: {pivot_table_file}")
        return pivot_table_file

    def calculate_completion_rates(self, input_file, current_month=None, year_to_analyze=None):
        if not os.path.exists(input_file) or not os.path.exists(self.activity_region_file):
            raise FileNotFoundError("Required input files are missing.")
        df = pd.read_csv(input_file)
        activity_region_df = pd.read_csv(self.activity_region_file)
        kpi_yearly_requirements = {"Environment": 17, "Health & Safety": 12, "Social": 5}
        current_month = 12 if current_month is None else current_month
        quarters_passed = (current_month - 1) // 3
        kpi_required_forms_to_date = {
            "Environment": min(round((current_month / 12) * 12) + quarters_passed + (1 if current_month == 12 else 0), 17),
            "Health & Safety": min(round((current_month / 12) * 12), 12),
            "Social": min(quarters_passed + (1 if current_month == 12 else 0), 5)
        }
        df['Environment'] = (df['Environment'] / kpi_required_forms_to_date["Environment"]) * 100
        df['Health & Safety'] = (df['Health & Safety'] / kpi_required_forms_to_date["Health & Safety"]) * 100
        df['Social'] = (df['Social'] / kpi_required_forms_to_date["Social"]) * 100
        df['Grand Total'] = df[['Environment', 'Health & Safety', 'Social']].mean(axis=1, skipna=True)
        completion_rates = df[['Environment', 'Health & Safety', 'Social', 'Grand Total']].fillna(0).round(0).astype(int).astype(str) + '%'
        output_df = df.iloc[:, 0].to_frame().join(completion_rates)
        output_df.columns = ['Location', 'Environment', 'Health & Safety', 'Social', 'Grand Total']
        merged_df = pd.merge(activity_region_df, output_df, on="Location", how="left")
        if year_to_analyze:
            merged_df['Year to Analyze'] = year_to_analyze
        merged_df = merged_df.sort_values(by="Location")
        final_output_file = os.path.join(self.output_folder, "completion_rates_with_activity_region.csv")
        merged_df.to_csv(final_output_file, index=False)
        print(f"Completion rates saved as: {final_output_file}")
        return final_output_file

    def run(self, year_to_analyze=None, current_month=None):
        processed_file = self.process_completion_data()
        pivot_table_file = self.generate_pivot_table(processed_file, year=year_to_analyze)
        final_output = self.calculate_completion_rates(pivot_table_file, current_month=current_month, year_to_analyze=year_to_analyze)
        return final_output

# Plotting Functions (as before)
def calculate_and_plot_region_completions(input_file):
    pass

def calculate_and_plot_activity_completions(input_file):
    pass

# Main Function
def generate_all_data():
    # Read the parameters from the dashboard_parameters.txt file
    parameters = read_dashboard_parameters(file_name="dashboard_parameters.txt")
    
    # Get the year and month values from the parameters
    year_to_analyze = parameters.get("year_to_analyze", 2024)
    current_month = parameters.get("current_month", 11)

    # Step 1: Run DataImpactTracker
    tracker = DataImpactTracker(
        input_file=os.path.join(INPUT_DIR, "Filled_not filled.csv"),
        activity_region_file=os.path.join(INPUT_DIR, "Activity_Region_Category.csv"),
        output_folder=OUTPUT_DIR
    )
    final_csv = tracker.run(year_to_analyze=year_to_analyze, current_month=current_month)

    # Step 2: Use the generated final CSV for further processing
    calculate_and_plot_region_completions(final_csv)
    calculate_and_plot_activity_completions(final_csv)
    print("All data generated successfully!")

if __name__ == "__main__":
    generate_all_data()
