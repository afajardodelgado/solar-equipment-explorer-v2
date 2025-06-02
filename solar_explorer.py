import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import subprocess
import os
import sys
from datetime import datetime
from pathlib import Path

# Set page configuration
st.set_page_config(
    page_title="Solar Equipment Explorer",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for a minimalist aesthetic
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton button {
        background-color: #343a40;
        color: white;
    }
    .stDataFrame {
        padding: 10px;
    }
    h1, h2, h3 {
        color: #343a40;
    }
    .stSidebar {
        background-color: #f8f9fa;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 0px;
        justify-content: flex-start;
    }
    .stTabs [data-baseweb="tab"] {
        height: 60px;
        white-space: pre-wrap;
        background-color: white;
        border-radius: 4px 4px 0 0;
        padding: 15px 30px;
        min-width: 250px;
        font-size: 20px;
        font-weight: 400;
        color: #666;
        border: 1px solid #eee;
        border-bottom: none;
    }
    .stTabs [aria-selected="true"] {
        background-color: #f0f2f6;
        border-bottom: 3px solid #4e8df5;
        font-weight: 700;
        color: #333;
    }
    .stat-container {
        display: flex;
        justify-content: space-between;
        margin-bottom: 20px;
    }
    .stat-box {
        background-color: white;
        border-radius: 5px;
        padding: 15px 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        width: 30%;
        text-align: center;
    }
    .stat-label {
        font-size: 14px;
        color: #666;
        margin-bottom: 5px;
    }
    .stat-value {
        font-size: 24px;
        font-weight: bold;
        color: #333;
    }
</style>
""", unsafe_allow_html=True)

# Add custom CSS to make the search bar narrower and style the refresh button
st.markdown("""
<style>
    /* Make the search input narrower */
    [data-testid="stTextInput"] {
        max-width: 250px;
    }
    
    /* Style the refresh button to look like the screenshot */
    [data-testid="stButton"] button {
        background-color: #f8f9fa;
        color: #6c757d;
        border: 1px solid #e0e0e0;
        border-radius: 50%;
        width: 28px;
        height: 28px;
        padding: 0;
        font-size: 14px;
        line-height: 1;
        display: flex;
        align-items: center;
        justify-content: center;
        min-height: 0;
        box-shadow: none;
    }
    
    /* Hover effect for refresh button */
    [data-testid="stButton"] button:hover {
        background-color: #f0f0f0;
        border-color: #d0d0d0;
        color: #495057;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.title("☀️ Solar Equipment Explorer")

# Define base directory for database files
BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__)))

# Function to get database path
def get_db_path(db_name):
    return str(BASE_DIR / db_name)


# Function to load PV module data
@st.cache_data
def load_pv_data():
    with sqlite3.connect(get_db_path('pv_modules.db')) as conn:
        query = "SELECT * FROM pv_modules"
        df = pd.read_sql_query(query, conn)
    
    # Handle date columns - they're already stored as strings in the database
    date_columns = ['CEC Listing Date', 'Last Update', 'Date Added to Tool']
    for col in date_columns:
        if col in df.columns:
            # Vectorized operation instead of apply
            mask = df[col].notna() & df[col].astype(str).str.len().gt(10)
            df.loc[mask, col] = df.loc[mask, col].astype(str).str[:10]
    
    return df

# Function to load inverter data
@st.cache_data
def load_inverter_data():
    with sqlite3.connect(get_db_path('inverters.db')) as conn:
        query = "SELECT * FROM inverters"
        df = pd.read_sql_query(query, conn)
    
    # Handle date columns - they're already stored as strings in the database
    date_columns = ['Date Added to Tool', 'Last Update', 'Grid Support Listing Date']
    for col in date_columns:
        if col in df.columns:
            # Vectorized operation instead of apply
            mask = df[col].notna() & df[col].astype(str).str.len().gt(10)
            df.loc[mask, col] = df.loc[mask, col].astype(str).str[:10]
    
    return df

# Function to load energy storage data
@st.cache_data
def load_energy_storage_data():
    with sqlite3.connect(get_db_path('energy_storage.db')) as conn:
        query = "SELECT * FROM energy_storage"
        df = pd.read_sql_query(query, conn)
    
    # Handle date columns - they're already stored as strings in the database
    date_columns = ['Date Added to Tool', 'Last Update', 'Energy Storage Listing Date', 'Certificate Date']
    for col in date_columns:
        if col in df.columns:
            # Vectorized operation instead of apply
            mask = df[col].notna() & df[col].astype(str).str.len().gt(10)
            df.loc[mask, col] = df.loc[mask, col].astype(str).str[:10]
    
    return df

# Function to load battery data
@st.cache_data
def load_battery_data():
    with sqlite3.connect(get_db_path('batteries.db')) as conn:
        query = "SELECT * FROM batteries"
        df = pd.read_sql_query(query, conn)
    
    # Handle date columns - they're already stored as strings in the database
    date_columns = ['Date Added to Tool', 'Last Update', 'Battery Listing Date', 'Certificate Date']
    for col in date_columns:
        if col in df.columns:
            # Vectorized operation instead of apply
            mask = df[col].notna() & df[col].astype(str).str.len().gt(10)
            df.loc[mask, col] = df.loc[mask, col].astype(str).str[:10]
    
    return df

# Function to load meter data
@st.cache_data
def load_meter_data():
    with sqlite3.connect(get_db_path('meters.db')) as conn:
        query = "SELECT * FROM meters"
        df = pd.read_sql_query(query, conn)
    
    # Handle date columns - they're already stored as strings in the database
    date_columns = ['Date Added to Tool', 'Last Update', 'Meter Listing Date']
    for col in date_columns:
        if col in df.columns:
            # Vectorized operation instead of apply
            mask = df[col].notna() & df[col].astype(str).str.len().gt(10)
            df.loc[mask, col] = df.loc[mask, col].astype(str).str[:10]
    
    return df

# Create tabs for equipment types
tab1, tab2, tab3, tab4, tab5 = st.tabs(["PV Modules", "Grid Support Inverter List", "Energy Storage Systems", "Batteries", "Meters"])

# Function to run the appropriate downloader script based on equipment type
def run_downloader(equipment_type):
    try:
        # Determine which script to run based on equipment type
        if equipment_type == "PV Modules":
            script_path = str(BASE_DIR / "pv_module_downloader.py")
        elif equipment_type == "Grid Support Inverter List":
            script_path = str(BASE_DIR / "inverters" / "inverter_downloader.py")
        elif equipment_type == "Energy Storage Systems":
            script_path = str(BASE_DIR / "storage" / "energy_storage_downloader.py")
        elif equipment_type == "Batteries":
            script_path = str(BASE_DIR / "batteries" / "battery_downloader.py")
        elif equipment_type == "Meters":
            script_path = str(BASE_DIR / "meters" / "meter_downloader.py")
        else:
            st.error(f"Unknown equipment type: {equipment_type}")
            return False
        
        # Check if the script exists
        if not os.path.exists(script_path):
            st.error(f"Downloader script not found: {script_path}")
            return False
        
        # Use a spinner while downloading data
        with st.spinner(f"Downloading latest {equipment_type} data..."):
            # Run the script using subprocess with the correct Python executable
            python_executable = sys.executable
            result = subprocess.run([python_executable, script_path], 
                                  capture_output=True, 
                                  text=True, 
                                  check=False)
            
            if result.returncode == 0:
                st.success(f"Successfully updated {equipment_type} database.")
                # Clear cache to force reload of data
                st.cache_data.clear()
                return True
            else:
                st.error(f"Error updating {equipment_type} database: {result.stderr}")
                with st.expander("View Error Details"):
                    st.code(result.stderr)
                return False
    except Exception as e:
        st.error(f"Error running downloader: {str(e)}")
        return False

# Function to display equipment data with consistent formatting
def display_equipment_data(equipment_type, df, id_column, manufacturer_column, model_column, efficiency_column, power_column):
    
    # Display statistics in a consistent format
    # Determine which date column to use based on equipment type
    date_column = None
    if equipment_type == "PV Modules":
        date_column = 'CEC Listing Date'
    elif equipment_type == "Grid Support Inverter List":
        date_column = 'Grid Support Listing Date'
    elif equipment_type == "Energy Storage Systems":
        date_column = 'Energy Storage Listing Date'
    elif equipment_type == "Batteries":
        date_column = 'Battery Listing Date'
    elif equipment_type == "Meters":
        date_column = 'Meter Listing Date'
    
    # Handle the date formatting safely
    latest_listing_date = "N/A"
    if date_column and date_column in df.columns and not df.empty:
        try:
            # Filter out None, 'None', and empty values before finding max date
            valid_dates = df[df[date_column].notna() & 
                             (df[date_column].astype(str) != 'None') & 
                             (df[date_column].astype(str) != '')][date_column]
            
            if not valid_dates.empty:
                max_date = valid_dates.max()
                if isinstance(max_date, str) and len(max_date) > 0:
                    # If it contains time, just take the date part
                    if ' ' in max_date:
                        latest_listing_date = max_date.split(' ')[0]
                    else:
                        latest_listing_date = max_date
                else:
                    latest_listing_date = str(max_date) if max_date else "N/A"
            else:
                latest_listing_date = "N/A"
        except Exception as e:
            print(f"Error processing dates: {e}")
            latest_listing_date = "N/A"
    
    # Format the label based on equipment type
    date_label = "Latest Listing Date"
    if equipment_type == "PV Modules":
        date_label = "Latest CEC Listing Date"
    elif equipment_type == "Grid Support Inverter List":
        date_label = "Latest Grid Support Listing Date"
    elif equipment_type == "Energy Storage Systems":
        date_label = "Latest Energy Storage Listing Date"
    elif equipment_type == "Batteries":
        date_label = "Latest Battery Listing Date"
    elif equipment_type == "Meters":
        date_label = "Latest Meter Listing Date"
    
    st.markdown("""
    <div class="stat-container">
        <div class="stat-box">
            <div class="stat-label">Total Items</div>
            <div class="stat-value">{}</div>
        </div>
        <div class="stat-box">
            <div class="stat-label">Manufacturers</div>
            <div class="stat-value">{}</div>
        </div>
        <div class="stat-box">
            <div class="stat-label">{}</div>
            <div class="stat-value">{}</div>
        </div>
    </div>
    """.format(
        len(df), 
        df[manufacturer_column].nunique(),
        date_label,
        latest_listing_date
    ), unsafe_allow_html=True)
    
    # Display filtered data
    st.subheader(f"{equipment_type}")
    
    # Create a row with two columns - one for filters on the left and search on the right
    filter_col, search_col = st.columns([1, 1])
    
    # Add a filters button in the left column
    with filter_col:
        with st.expander("Add Filters Here"):
            # Filter by manufacturer
            manufacturers = ["All"] + sorted(df[manufacturer_column].unique().tolist())
            selected_manufacturer = st.selectbox(
                "Manufacturer", 
                manufacturers,
                key=f"manufacturer_select_{equipment_type}"
            )
            
            # Filter by efficiency if available
            if efficiency_column in df.columns:
                try:
                    min_efficiency = float(df[efficiency_column].min())
                    max_efficiency = float(df[efficiency_column].max())
                    efficiency_range = st.slider(
                        f"Efficiency (%)",
                        min_efficiency,
                        max_efficiency,
                        (min_efficiency, max_efficiency),
                        key=f"efficiency_slider_{equipment_type}"
                    )
                except (ValueError, TypeError):
                    st.warning(f"Cannot filter by {efficiency_column} due to data type issues.")
                    efficiency_column = None
    
    # Add a search bar in the right column
    with search_col:
        with st.expander("Add Search Here"):
            tab_search_query = st.text_input(
                f"Search {equipment_type} by {manufacturer_column} or {model_column}", 
                "", 
                placeholder="Enter search term...",
                key=f"search_{equipment_type}"
            )
            
            # Apply search if provided
            if tab_search_query:
                try:
                    # Handle potential errors in string operations
                    search_results = df[df[manufacturer_column].astype(str).str.contains(tab_search_query, case=False, na=False) | 
                                      df[model_column].astype(str).str.contains(tab_search_query, case=False, na=False)]
                    
                    # Only update df if we found results
                    if not search_results.empty:
                        df = search_results
                        st.success(f"Found {len(df)} items matching '{tab_search_query}'")
                    else:
                        st.warning(f"No items found matching '{tab_search_query}'. Showing all items instead.")
                except Exception as e:
                    st.error(f"Search error: {e}. Showing all items instead.")
                    # Keep df as is if there's an error
        
    # Add a simple refresh button aligned far right
    refresh_container = st.container()
    with refresh_container:
        # Use a very uneven column split to push the button far right
        _, right_col = st.columns([39, 1])
        with right_col:
            # Use a simple circular refresh icon
            if st.button("⟳", key=f"refresh_button_{equipment_type}", help="Download latest data and refresh"):
                # Run the appropriate downloader script
                success = run_downloader(equipment_type)
                if success:
                    # Clear cache and reload the app
                    st.cache_data.clear()
                    st.experimental_rerun()
    
    st.write(f"Showing {len(df)} items")
    
    # Apply filters
    filtered_df = df.copy()
    
    if selected_manufacturer != "All":
        filtered_df = filtered_df[filtered_df[manufacturer_column] == selected_manufacturer]
    
    if efficiency_column and efficiency_column in df.columns:
        try:
            filtered_df = filtered_df[
                (filtered_df[efficiency_column].astype(float) >= efficiency_range[0]) &
                (filtered_df[efficiency_column].astype(float) <= efficiency_range[1])
            ]
        except (ValueError, TypeError):
            st.warning(f"Could not apply {efficiency_column} filter due to data type issues.")
    
    # Select columns to display
    all_columns = df.columns.tolist()
    default_columns = [id_column, manufacturer_column, model_column]
    
    # Add equipment-specific columns to defaults
    if equipment_type == "PV Modules":
        # Set specific default columns for PV Modules
        default_columns = ['module_id', 'Manufacturer', 'Model Number', 'CEC Listing Date', 'Technology', 'Nameplate Pmax (W)']
    elif equipment_type == "Grid Support Inverter List":
        # Set specific default columns for Grid Support Inverter List
        default_columns = ['inverter_id', 'Manufacturer Name', 'Model Number1', 'Grid Support Listing Date', 'Description']
    elif equipment_type == "Energy Storage Systems":
        # Set specific default columns for Energy Storage Systems
        default_columns = ['storage_id', 'Manufacturer', 'Model Number', 'Energy Storage Listing Date', 'Chemistry', 'Description', 'PV DC Input Capability', 'Capacity (kWh)', 'Continuous Power Rating (kW)', 'Maximum Discharge Rate (kW)', 'Voltage (Vac)', 'Certifying Entity', 'Certificate Date']
    elif equipment_type == "Batteries":
        # Set specific default columns for Batteries
        default_columns = ['battery_id', 'Manufacturer', 'Model Number', 'Battery Listing Date', 'Chemistry', 'Description', 'Capacity (kWh)', 'Discharge Rate (kW)', 'Round Trip Efficiency (%)', 'Certifying Entity', 'Certificate Date']
    elif equipment_type == "Meters":
        # Set specific default columns for Meters
        default_columns = ['meter_id', 'Manufacturer', 'Model Number', 'Meter Listing Date', 'Display Type', 'PBI Meter', 'Note']
    
    # Keep only columns that exist in the dataframe
    default_columns = [col for col in default_columns if col in all_columns]
    
    selected_columns = st.multiselect(
        "Select columns to display",
        all_columns,
        default=default_columns,
        key=f"columns_{equipment_type}"
    )
    
    if selected_columns:
        st.dataframe(filtered_df[selected_columns], use_container_width=True)
    else:
        st.dataframe(filtered_df, use_container_width=True)
    
    return filtered_df

# PV Modules Tab
with tab1:
    # Load PV module data
    with st.spinner("Loading PV Modules data..."):
        df_pv = load_pv_data()
        filtered_df_pv = display_equipment_data(
            "PV Modules",
            df_pv,
            'module_id',
            'Manufacturer',
            'Model Number',
            'PTC Efficiency (%)',
            'Power Rating (W)'
        )

# Grid Support Inverter List Tab
with tab2:
    # Load Grid Support Inverter data
    with st.spinner("Loading Grid Support Inverter List data..."):
        try:
            df_inv = load_inverter_data()
            filtered_df_inv = display_equipment_data(
                "Grid Support Inverter List",
                df_inv,
                'inverter_id',
                'Manufacturer Name',
                'Model Number1',
                'CEC Weighted Efficiency (%)',
                'Rated Output Power (kW)'
            )
        except Exception as e:
            st.error(f"Error loading inverter data: {e}")

# Energy Storage Systems Tab
with tab3:
    # Load Energy Storage Systems data
    with st.spinner("Loading Energy Storage Systems data..."):
        try:
            df_storage = load_energy_storage_data()
            filtered_df_storage = display_equipment_data(
                "Energy Storage Systems",
                df_storage,
                'storage_id',
                'Manufacturer',
                'Model Number',
                'Round Trip Efficiency (%)',
                'Maximum Discharge Rate (kW)'
            )
        except Exception as e:
            st.error(f"Error loading energy storage data: {e}")
            st.info("To download Energy Storage Systems data, click the refresh button in the top right corner.")
            
            # Add a button to run the downloader script directly if no data is available
            if st.button("Download Energy Storage Data"):
                success = run_downloader("Energy Storage Systems")
                if success:
                    st.experimental_rerun()

# Batteries Tab
with tab4:
    # Load Batteries data
    with st.spinner("Loading Batteries data..."):
        try:
            df_battery = load_battery_data()
            filtered_df_battery = display_equipment_data(
                "Batteries",
                df_battery,
                'battery_id',
                'Manufacturer',
                'Model Number',
                'Round Trip Efficiency (%)',
                'Discharge Rate (kW)'
            )
        except Exception as e:
            st.error(f"Error loading battery data: {e}")
            st.info("To download Batteries data, click the refresh button in the top right corner.")
            
            # Add a button to run the downloader script directly if no data is available
            if st.button("Download Batteries Data"):
                success = run_downloader("Batteries")
                if success:
                    st.experimental_rerun()

# Meters Tab
with tab5:
    # Load Meters data
    with st.spinner("Loading Meters data..."):
        try:
            df_meter = load_meter_data()
            filtered_df_meter = display_equipment_data(
                "Meters",
                df_meter,
                'meter_id',
                'Manufacturer',
                'Model Number',
                'Display Type',
                'PBI Meter'
            )
        except Exception as e:
            st.error(f"Error loading meter data: {e}")
            st.info("To download Meters data, click the refresh button in the top right corner.")
            
            # Add a button to run the downloader script directly if no data is available
            if st.button("Download Meters Data"):
                success = run_downloader("Meters")
                if success:
                    st.experimental_rerun()

# Add visualization section to each tab
def display_visualizations(filtered_df, equipment_type, manufacturer_column, efficiency_column, power_column):
    st.subheader("Data Visualization")
    # Add a unique key for each selectbox based on equipment_type
    chart_type = st.selectbox(
        "Select chart type",
        ["Manufacturer Distribution", "Efficiency Comparison", "Power Comparison", "Correlation Plot"],
        key=f"chart_type_{equipment_type}"
    )
    
    if chart_type == "Manufacturer Distribution":
        # Group manufacturers by count
        manufacturer_counts = filtered_df[manufacturer_column].value_counts().reset_index()
        manufacturer_counts.columns = ['Manufacturer', 'Count']
        
        # Calculate percentage
        total = manufacturer_counts['Count'].sum()
        manufacturer_counts['Percentage'] = (manufacturer_counts['Count'] / total * 100).round(1)
        
        # Keep only top 10 manufacturers, group others
        top_n = 10
        if len(manufacturer_counts) > top_n:
            top_manufacturers = manufacturer_counts.head(top_n).copy()
            other_count = manufacturer_counts.iloc[top_n:]['Count'].sum()
            other_percentage = manufacturer_counts.iloc[top_n:]['Percentage'].sum()
            
            # Add "Other" category
            other_row = pd.DataFrame({
                'Manufacturer': ['Other'],
                'Count': [other_count],
                'Percentage': [other_percentage.round(1)]
            })
            
            manufacturer_counts = pd.concat([top_manufacturers, other_row])
        
        # Sort by percentage descending
        manufacturer_counts = manufacturer_counts.sort_values('Percentage', ascending=True)
        
        # Create a custom color palette - distinct colors for top categories, gray for "Other"
        colors = px.colors.qualitative.Bold[:top_n]
        if len(manufacturer_counts) > top_n:
            colors.append('#CCCCCC')  # Gray for "Other"
        
        # Create horizontal bar chart
        fig = px.bar(
            manufacturer_counts,
            y='Manufacturer',
            x='Percentage',
            title=f'Share of {equipment_type} by Manufacturer (%)',
            color='Manufacturer',
            color_discrete_sequence=colors,
            text='Percentage',
            orientation='h',
            height=500
        )
        
        # Improve layout
        fig.update_traces(texttemplate='%{text}%', textposition='outside')
        fig.update_layout(
            xaxis_title='Market Share (%)',
            yaxis_title='Manufacturer',
            showlegend=False,
            margin=dict(l=20, r=20, t=40, b=20),
            xaxis=dict(range=[0, max(manufacturer_counts['Percentage']) * 1.15])  # Add space for labels
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    elif chart_type == "Efficiency Comparison" and efficiency_column in filtered_df.columns:
        try:
            fig = px.box(
                filtered_df,
                x=manufacturer_column,
                y=efficiency_column,
                title=f'Efficiency Comparison by Manufacturer',
                color=manufacturer_column,
                color_discrete_sequence=px.colors.qualitative.Bold,
                height=500
            )
            fig.update_layout(
                xaxis_title='Manufacturer',
                yaxis_title='Efficiency (%)',
                showlegend=False,
                xaxis={'categoryorder':'total descending'}
            )
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Could not create efficiency comparison chart: {e}")
    
    elif chart_type == "Power Comparison" and power_column in filtered_df.columns:
        try:
            fig = px.box(
                filtered_df,
                x=manufacturer_column,
                y=power_column,
                title=f'Power Rating Comparison by Manufacturer',
                color=manufacturer_column,
                color_discrete_sequence=px.colors.qualitative.Bold,
                height=500
            )
            fig.update_layout(
                xaxis_title='Manufacturer',
                yaxis_title='Power Rating',
                showlegend=False,
                xaxis={'categoryorder':'total descending'}
            )
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Could not create power comparison chart: {e}")
    
    elif chart_type == "Correlation Plot":
        # Select only numeric columns for correlation
        numeric_cols = filtered_df.select_dtypes(include=['float64', 'int64']).columns.tolist()
        
        if len(numeric_cols) >= 2:
            # Add unique keys for each axis selectbox based on equipment_type
            x_axis = st.selectbox("X-axis", numeric_cols, index=0, key=f"x_axis_{equipment_type}")
            y_axis = st.selectbox("Y-axis", numeric_cols, index=min(1, len(numeric_cols)-1), key=f"y_axis_{equipment_type}")
            
            fig = px.scatter(
                filtered_df,
                x=x_axis,
                y=y_axis,
                color=manufacturer_column,
                title=f'{y_axis} vs {x_axis}',
                color_discrete_sequence=px.colors.qualitative.Bold,
                height=500
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Not enough numeric columns available for correlation plot.")

# Update the tab content to include visualizations
with tab1:
    # Add visualization section for PV Modules
    display_visualizations(
        filtered_df_pv,
        "PV Modules",
        'Manufacturer',
        'PTC Efficiency (%)',
        'Power Rating (W)'
    )

with tab2:
    # Add visualization section for Grid Support Inverter List
    display_visualizations(
        filtered_df_inv,
        "Grid Support Inverter List",
        'Manufacturer Name',
        'Weighted Efficiency (%)',
        'Maximum Continuous Output Power at Unity Power Factor ((kW))'
    )

with tab3:
    # Add visualization section for Energy Storage Systems
    display_visualizations(
        filtered_df_storage,
        "Energy Storage Systems",
        'Manufacturer',
        'Chemistry',
        'Maximum Discharge Rate (kW)'
    )

with tab4:
    # Add visualization section for Batteries
    display_visualizations(
        filtered_df_battery,
        "Batteries",
        'Manufacturer',
        'Round Trip Efficiency (%)',
        'Discharge Rate (kW)'
    )

with tab5:
    # Add visualization section for Meters
    display_visualizations(
        filtered_df_meter,
        "Meters",
        'Manufacturer',
        'Display Type',
        'PBI Meter'
    )

# Add equipment comparison functionality to each tab
def display_comparison(filtered_df, equipment_type, id_column):
    st.subheader(f"{equipment_type} Comparison")
    st.markdown(f"Select {equipment_type.lower()} to compare their specifications side by side.")
    
    # Get list of equipment
    equipment_list = filtered_df[id_column].tolist()
    if len(equipment_list) > 1:
        selected_equipment = st.multiselect(
            f"Select {equipment_type.lower()} to compare",
            equipment_list,
            max_selections=3,
            key=f"compare_{equipment_type}"
        )
        
        if selected_equipment:
            comparison_df = filtered_df[filtered_df[id_column].isin(selected_equipment)]
            
            # Transpose the dataframe for side-by-side comparison
            comparison_df = comparison_df.set_index(id_column).T
            
            st.dataframe(comparison_df, use_container_width=True)
    else:
        st.info(f"Apply filters to see more {equipment_type.lower()} for comparison.")

# Update the tab content to include comparisons
with tab1:
    # Add comparison section for PV Modules
    display_comparison(filtered_df_pv, "PV Modules", 'module_id')

with tab2:
    # Add comparison section for Grid Support Inverter List
    display_comparison(filtered_df_inv, "Grid Support Inverter List", 'inverter_id')

with tab3:
    # Add comparison section for Energy Storage Systems
    display_comparison(filtered_df_storage, "Energy Storage Systems", 'storage_id')

with tab4:
    # Add comparison section for Batteries
    display_comparison(filtered_df_battery, "Batteries", 'battery_id')

with tab5:
    # Add comparison section for Meters
    display_comparison(filtered_df_meter, "Meters", 'meter_id')

# Footer
st.markdown("---")
st.markdown("Data source: California Energy Commission")
st.markdown(f"Last updated: {datetime.now().strftime('%Y-%m-%d')}")
