import pandas as pd
import os
import plotly.graph_objects as go
import plotly.express as px

# Define the directory for saving plots globally
PLOTS_DIR = "Output/Assets"
os.makedirs(PLOTS_DIR, exist_ok=True)

def preprocess_columns(df, columns):
    """Helper function to preprocess columns by removing '%' and converting to float."""
    for column in columns:
        if column in df.columns:
            df[column] = df[column].str.replace('%', '').astype(float)
        else:
            print(f"Warning: Column '{column}' not found in data.")
    return df

def calculate_and_plot_region_completions(input_file):
    df = pd.read_csv(input_file)
    df = preprocess_columns(df, ['Environment', 'Health & Safety', 'Social'])
    
    regions = ['EUROPE', 'LATAM', 'MEA', 'APAC', 'NORAM']
    avg_completions = []

    # Calculate average completion rates per region
    for region in regions:
        df_region = df[df['Region'] == region]
        if not df_region.empty:
            avg_completions.append({
                'Region': region,
                'Environment': df_region['Environment'].mean(skipna=True),
                'Health & Safety': df_region['Health & Safety'].mean(skipna=True),
                'Social': df_region['Social'].mean(skipna=True)
            })

    avg_df = pd.DataFrame(avg_completions).set_index('Region')
    plot_avg_completion_rates(avg_df, "average_completion_rates_by_region_without_grand_total.html")

def plot_avg_completion_rates(df, filename):
    """Plot average completion rates by region (excluding Grand Total) using Plotly with custom colors."""
    # Define custom colors for the KPIs
    colors = {
        'Environment': 'rgb(67, 0, 153)',  # HEX#430099
        'Health & Safety': 'rgb(145, 125, 185)',  # HEX#917db9 (Light Purple)
        'Social': 'rgb(180, 180, 180)'  # HEX#b4b4b4
    }

    # Create an interactive bar chart
    fig = go.Figure()

    # Add traces for each KPI with its corresponding color
    for column in df.columns:
        fig.add_trace(go.Bar(
            x=df.index,
            y=df[column],
            name=column,
            marker_color=colors.get(column, 'gray')  # Use custom colors, default to gray if column not in colors
        ))

    # Update layout for better visualization
    fig.update_layout(
        title='Average Completion Rates by Region (Excluding Grand Total)',
        xaxis_title='Region',
        yaxis_title='Completion Rate (%)',
        barmode='group',  # Grouped bar mode
        xaxis_tickangle=45,  # Tilt x-axis labels for better readability
        template='plotly_white',  # Use a clean white background template
        legend_title_text='Completion Categories',  # Add a title to the legend
        title_font_size=16
    )

    # Save the interactive plot to an HTML file
    plot_path = os.path.join(PLOTS_DIR, filename)
    fig.write_html(plot_path)
    print(f"Interactive Plot saved to: {plot_path}")

def calculate_and_plot_region_completions_heatmap(input_file):
    df = pd.read_csv(input_file)
    df = preprocess_columns(df, ['Environment', 'Health & Safety', 'Social', 'Grand Total'])

    regions = ['EUROPE', 'LATAM', 'MEA', 'APAC', 'NORAM']
    avg_completions = []

    for region in regions:
        df_region = df[df['Region'] == region]
        if not df_region.empty:
            avg_completions.append({
                'Region': region,
                'Environment': df_region['Environment'].mean(skipna=True),
                'Health & Safety': df_region['Health & Safety'].mean(skipna=True),
                'Social': df_region['Social'].mean(skipna=True),
                'Grand Total': df_region['Grand Total'].mean(skipna=True)
            })

    avg_df = pd.DataFrame(avg_completions).set_index('Region')
    plot_avg_completion_rates_heatmap(avg_df)

def plot_avg_completion_rates_heatmap(df):

    blue_grey_scale = [
        [0, "rgb(225, 220, 230)"],  # Light grey
        [0.5, "rgb(170, 155, 185)"],  # Medium grey
        [1, "rgb(115, 130, 230)"]  # Blue
    ]
    fig = px.imshow(df.T, labels={'x': 'Region', 'y': 'Completion Categories'},
                    title='Average Completion Rates by Region',
                    color_continuous_scale=blue_grey_scale, aspect='auto')

    plot_path = os.path.join(PLOTS_DIR, "average_completion_rates_by_region_heatmap.html")
    fig.write_html(plot_path)
    print(f"Interactive Heatmap saved to: {plot_path}")

def add_country_to_completion_data(location_file, completion_file, output_file):
    location_df = pd.read_csv(location_file)
    completion_df = pd.read_csv(completion_file)

    location_df['country'] = location_df['country'].replace({
        'UAE': 'United Arab Emirates',  # Add mappings as needed
    })
    
    completion_df['Location'] = completion_df['Location'].replace({
        'Abu Dhabi': 'Abu Dhabi',  # Normalize location names
    })

    merged_df = pd.merge(completion_df, location_df[['Site', 'country']], left_on='Location', right_on='Site', how='left')
    merged_df = merged_df.drop_duplicates(subset='Location')
    
    merged_df.to_csv(output_file, index=False)
    print(f"Updated file saved to: {output_file}")

def calculate_average_completion_per_country(input_file, output_file):
    df = pd.read_csv(input_file)
    df = preprocess_columns(df, ['Environment', 'Health & Safety', 'Social', 'Grand Total'])
    
    avg_completions_per_country = df.groupby('country')[['Environment', 'Health & Safety', 'Social', 'Grand Total']].mean()
    avg_completions_per_country.to_csv(output_file)
    print(f"Average completion rates per country saved to: {output_file}")

def plot_grand_total_map(input_file):
    df = pd.read_csv(input_file)
    df['Grand Total'] = df['Grand Total'].astype(float)

    # Create the choropleth map
    fig = px.choropleth(df, 
                        locations='country', 
                        locationmode='country names', 
                        color='Grand Total',
                        hover_name='country', 
                        color_continuous_scale='Viridis', 
                        title='Completion Rates (Grand Total) by Country',
                        labels={'Grand Total': 'Completion Rate (%)'})

    # Update layout for a white background, larger size, and other customizations
    fig.update_layout(
        template='plotly_white',  # Use the white background template
        plot_bgcolor='white',  # Set the plot area background to white
        geo=dict(
            lakecolor='white',  # Set the color of lakes to white (this makes the map cleaner)
            projection_type='equirectangular'  # Optionally adjust map projection for a different view
        ),
        title_font=dict(size=16, family="Arial"),  # Customize title font
        title_x=0.5,  # Center the title
        width=600,  # Set the width of the map (in pixels)
        height=500  # Set the height of the map (in pixels)
    )

    # Save the interactive map to an HTML file
    plot_path = os.path.join(PLOTS_DIR, "grand_total_map.html")
    fig.write_html(plot_path)
    print(f"Interactive map saved to: {plot_path}")

def calculate_and_plot_activity_completions(input_file):
    """Create a bar chart comparing IST vs IPS vs ISI for each KPI (Environment, Health & Safety, Social)."""
    # Load the data
    df = pd.read_csv(input_file)
    
    # Clean up the data by removing '%' and converting to float
    df = preprocess_columns(df, ['Environment', 'Health & Safety', 'Social', 'Grand Total'])
    
    # Calculate the average completion rates for IST, IPS, and ISI for each KPI
    avg_ist = df[df['Activity'] == 'IST'][['Environment', 'Health & Safety', 'Social']].mean()
    avg_ips = df[df['Activity'] == 'IPS'][['Environment', 'Health & Safety', 'Social']].mean()
    
    # Calculate ISI: Anything that is not IST or IPS
    df_isi = df[~df['Activity'].isin(['IST', 'IPS'])]  
    avg_isi = df_isi[['Environment', 'Health & Safety', 'Social']].mean()

    # Prepare the data for the bar chart
    kpis = ['Environment', 'Health & Safety', 'Social']
    ist_values = [avg_ist[kpi] for kpi in kpis]
    ips_values = [avg_ips[kpi] for kpi in kpis]
    isi_values = [avg_isi[kpi] for kpi in kpis]

    # Define custom colors for IST, IPS, and ISI
    colors = {
        'IST': 'rgb(115, 130, 230)',  # HEX#7382e6
        'IPS': 'rgb(205, 195, 215)',  # HEX#cdc3d7
        'ISI': 'rgb(150, 10, 40)'  # HEX#228b22 (Green for ISI)
    }

    # Create the bar chart with Plotly
    fig = go.Figure()

    # Add IST bars
    fig.add_trace(go.Bar(
        x=kpis,
        y=ist_values,
        name='IST',
        marker_color=colors['IST']
    ))

    # Add IPS bars
    fig.add_trace(go.Bar(
        x=kpis,
        y=ips_values,
        name='IPS',
        marker_color=colors['IPS']
    ))

    # Add ISI bars
    fig.add_trace(go.Bar(
        x=kpis,
        y=isi_values,
        name='ISI',
        marker_color=colors['ISI']
    ))

    # Update layout for better visualization
    fig.update_layout(
        title='Comparison of IST, IPS, and ISI for Completion Rates by KPI',
        xaxis_title='KPIs',
        yaxis_title='Completion Rate (%)',
        barmode='group',  # Grouped bars for each KPI
        xaxis_tickangle=0,
        legend_title='Activity',
        template='plotly_white',
        font=dict(
            size=14
        )
    )

    # Save the plot as an interactive HTML file
    plot_path = os.path.join(PLOTS_DIR, "comparison_of_IST_IPS_ISI.html")
    fig.write_html(plot_path)
    print(f"Interactive Plot saved to: {plot_path}")

# Example usage
input_file = "Output/completion_rates_with_activity_region.csv"
location_file = "Output/filled_0_1.csv"
completion_file = "Output/completion_rates_with_activity_region.csv"
output_file = "Output/average_completion_rates_per_country.csv"

calculate_and_plot_region_completions(input_file)
calculate_and_plot_region_completions_heatmap(input_file)
add_country_to_completion_data(location_file, completion_file, output_file)
calculate_average_completion_per_country(output_file, "Output/average_completion_rates_per_country.csv")
plot_grand_total_map("Output/average_completion_rates_per_country.csv")
calculate_and_plot_activity_completions(input_file)
