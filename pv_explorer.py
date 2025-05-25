import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from datetime import datetime

# Set page configuration for a minimalist aesthetic
st.set_page_config(
    page_title="PV Module Explorer",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for minimalist Rick Rubin aesthetic
st.markdown("""
<style>
    /* Minimalist styling */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    h1, h2, h3 {
        font-weight: 300;
        letter-spacing: 0.05em;
    }
    .stButton button {
        background-color: #222;
        color: white;
        border-radius: 0;
    }
    .stButton button:hover {
        background-color: #444;
        color: white;
    }
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #f5f5f5;
    }
</style>
""", unsafe_allow_html=True)

# App title
st.title("PV Module Explorer")
st.markdown("##### A minimalist interface for exploring solar panel data")

# Add a refresh button
if st.button("Refresh Data"):
    st.cache_data.clear()
    st.rerun()

# Function to load data
@st.cache_data(ttl=10, show_spinner="Loading database...")
def load_data():
    conn = sqlite3.connect('pv_modules.db')
    query = "SELECT * FROM pv_modules"
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    # Convert date columns if they exist and contain timestamps
    date_columns = ['CEC Listing Date', 'Last Update', 'Date Added to Tool']
    for col in date_columns:
        if col in df.columns:
            # Skip Date Added to Tool as it's already in the right format
            if col == 'Date Added to Tool':
                continue
            df[col] = df[col].apply(
                lambda x: datetime.fromtimestamp(int(x)).strftime('%Y-%m-%d') 
                if pd.notna(x) and str(x).strip() != "" else None
            )
    
    return df

# Load the data
with st.spinner("Loading data..."):
    df = load_data()

# Sidebar for filters
st.sidebar.markdown("## Filters")

# Manufacturer filter
manufacturers = ['All'] + sorted(df['Manufacturer'].unique().tolist())
selected_manufacturer = st.sidebar.selectbox("Manufacturer", manufacturers)

# Technology filter
technologies = ['All'] + sorted(df['Technology'].unique().tolist())
selected_technology = st.sidebar.selectbox("Technology", technologies)

# Power range filter - convert to numeric first
df['Nameplate Pmax ((W))'] = pd.to_numeric(df['Nameplate Pmax ((W))'], errors='coerce')
min_power = float(df['Nameplate Pmax ((W))'].min())
max_power = float(df['Nameplate Pmax ((W))'].max())
power_range = st.sidebar.slider(
    "Power Range (W)", 
    min_value=min_power,
    max_value=max_power,
    value=(min_power, max_power)
)

# Apply filters
filtered_df = df.copy()
if selected_manufacturer != 'All':
    filtered_df = filtered_df[filtered_df['Manufacturer'] == selected_manufacturer]
if selected_technology != 'All':
    filtered_df = filtered_df[filtered_df['Technology'] == selected_technology]

# Convert power column to numeric to ensure proper filtering
filtered_df['Nameplate Pmax ((W))'] = pd.to_numeric(filtered_df['Nameplate Pmax ((W))'], errors='coerce')

# Apply power range filter
filtered_df = filtered_df[
    (filtered_df['Nameplate Pmax ((W))'] >= power_range[0]) & 
    (filtered_df['Nameplate Pmax ((W))'] <= power_range[1])
]

# Main content area
st.markdown(f"### Showing {len(filtered_df)} of {len(df)} modules")

# Tabs for different views
tab1, tab2, tab3 = st.tabs(["Data Table", "Visualizations", "Module Comparison"])

with tab1:
    # Column selection
    all_columns = df.columns.tolist()
    default_columns = ['Manufacturer', 'Model Number', 'Technology', 'Nameplate Pmax ((W))', 'PTC', 'module_id', 'Date Added to Tool']
    
    with st.expander("Select Columns to Display"):
        # Make sure default columns exist in all_columns
        valid_defaults = [col for col in default_columns if col in all_columns]
        selected_columns = st.multiselect(
            "Choose columns",
            options=all_columns,
            default=valid_defaults
        )
    
    if not selected_columns:
        # Make sure default columns exist in all_columns
        selected_columns = [col for col in default_columns if col in all_columns]
    
    # Show the filtered data
    st.dataframe(filtered_df[selected_columns], use_container_width=True)
    
    # Export option
    if st.button("Export Filtered Data to CSV"):
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name="filtered_pv_modules.csv",
            mime="text/csv"
        )

with tab2:
    # Visualization options
    viz_type = st.selectbox(
        "Visualization Type",
        ["Power Distribution", "Efficiency Comparison", "Technology Breakdown"]
    )
    
    if viz_type == "Power Distribution":
        fig = px.histogram(
            filtered_df, 
            x="Nameplate Pmax ((W))",
            color="Technology" if selected_technology == 'All' else None,
            title="Power Distribution",
            labels={"Nameplate Pmax ((W))": "Power (W)"},
            template="simple_white"
        )
        st.plotly_chart(fig, use_container_width=True)
        
    elif viz_type == "Efficiency Comparison":
        if 'P2/Pref' in filtered_df.columns:
            fig = px.scatter(
                filtered_df,
                x="Nameplate Pmax ((W))",
                y="P2/Pref",
                color="Technology" if selected_technology == 'All' else None,
                hover_data=["Manufacturer", "Model Number"],
                title="Power vs Efficiency",
                labels={"Nameplate Pmax ((W))": "Power (W)", "P2/Pref": "Efficiency Ratio"},
                template="simple_white"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Efficiency data not available")
            
    elif viz_type == "Technology Breakdown":
        tech_counts = filtered_df['Technology'].value_counts().reset_index()
        tech_counts.columns = ['Technology', 'Count']
        
        fig = px.pie(
            tech_counts, 
            values='Count', 
            names='Technology',
            title="Technology Distribution",
            template="simple_white"
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.markdown("### Compare Modules")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Module 1")
        module1 = st.selectbox(
            "Select first module",
            options=filtered_df['Model Number'].tolist(),
            key="module1"
        )
        
    with col2:
        st.markdown("#### Module 2")
        module2 = st.selectbox(
            "Select second module",
            options=filtered_df['Model Number'].tolist(),
            key="module2"
        )
    
    if st.button("Compare"):
        module1_data = filtered_df[filtered_df['Model Number'] == module1].iloc[0]
        module2_data = filtered_df[filtered_df['Model Number'] == module2].iloc[0]
        
        comparison_cols = [
            'Manufacturer', 'Technology', 'Nameplate Pmax ((W))', 'PTC',
            'Nameplate Isc ((A))', 'Nameplate Voc ((V))', 'A_c ((m2))',
            'Average NOCT ((°C))', 'γPmax ((%/°C))', 'Date Added to Tool'
        ]
        
        comparison_df = pd.DataFrame({
            'Property': comparison_cols,
            module1: [module1_data[col] for col in comparison_cols],
            module2: [module2_data[col] for col in comparison_cols]
        })
        
        st.dataframe(comparison_df, use_container_width=True)
        
        # Radar chart for visual comparison
        if len(comparison_cols) > 3:
            # Prepare data for radar chart
            numeric_cols = [
                'Nameplate Pmax ((W))', 'PTC', 'Nameplate Isc ((A))', 
                'Nameplate Voc ((V))', 'A_c ((m2))'
            ]
            
            # Convert numeric columns to ensure proper comparison
            for col in numeric_cols:
                if col in module1_data and col in module2_data:
                    module1_data[col] = pd.to_numeric(module1_data[col], errors='coerce')
                    module2_data[col] = pd.to_numeric(module2_data[col], errors='coerce')
            
            # Remove Date Added to Tool from radar chart
            if 'Date Added to Tool' in numeric_cols:
                numeric_cols.remove('Date Added to Tool')
            
            radar_df = pd.DataFrame()
            for col in numeric_cols:
                if col in module1_data and col in module2_data:
                    max_val = max(float(module1_data[col]), float(module2_data[col]))
                    if max_val > 0:
                        radar_df[col] = [
                            float(module1_data[col])/max_val, 
                            float(module2_data[col])/max_val
                        ]
            
            radar_df['Module'] = [module1, module2]
            
            fig = px.line_polar(
                radar_df, 
                r=radar_df.iloc[:, :-1].values.tolist(), 
                theta=radar_df.columns[:-1].tolist(),
                line_close=True,
                color='Module',
                template="simple_white"
            )
            st.plotly_chart(fig, use_container_width=True)

# Footer
st.markdown("---")
st.markdown(
    "Built with Streamlit • Data from California Energy Commission • "
    f"Last updated: {datetime.now().strftime('%Y-%m-%d')}"
)
