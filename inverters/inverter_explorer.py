import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from datetime import datetime

# Set page configuration
st.set_page_config(
    page_title="Inverter Explorer",
    page_icon="⚡",
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
</style>
""", unsafe_allow_html=True)

# Title and description
st.title("⚡ Inverter Explorer")
st.markdown("A minimalist interface for exploring solar inverter data from the California Energy Commission.")

# Function to load data from SQLite database
@st.cache_data
def load_data():
    conn = sqlite3.connect('inverters.db')
    query = "SELECT * FROM inverters"
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    # Handle date columns - they're already stored as strings in the database
    date_columns = ['Date Added to Tool']
    for col in date_columns:
        if col in df.columns:
            df[col] = df[col].apply(
                lambda x: x[:10] if pd.notna(x) and isinstance(x, str) and len(x) > 10 else x
            )
    
    return df

# Load the data
with st.spinner("Loading data..."):
    df = load_data()

# Add a refresh button to clear the cache and reload data
if st.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.experimental_rerun()

# Display basic statistics
st.subheader("Dataset Overview")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Inverters", len(df))
with col2:
    st.metric("Manufacturers", df['Manufacturer'].nunique())
with col3:
    st.metric("Latest Update", df['Date Added to Tool'].max() if 'Date Added to Tool' in df.columns else "N/A")

# Sidebar for filtering
st.sidebar.header("Filters")

# Filter by manufacturer
manufacturers = ["All"] + sorted(df['Manufacturer Name'].unique().tolist())
selected_manufacturer = st.sidebar.selectbox("Manufacturer", manufacturers)

# Filter by weighted efficiency
if 'Weighted Efficiency (%)' in df.columns:
    min_efficiency = float(df['Weighted Efficiency (%)'].min())
    max_efficiency = float(df['Weighted Efficiency (%)'].max())
    efficiency_range = st.sidebar.slider(
        "Weighted Efficiency (%)",
        min_efficiency,
        max_efficiency,
        (min_efficiency, max_efficiency)
    )

# Apply filters
filtered_df = df.copy()

if selected_manufacturer != "All":
    filtered_df = filtered_df[filtered_df['Manufacturer Name'] == selected_manufacturer]

if 'Weighted Efficiency (%)' in df.columns:
    filtered_df = filtered_df[
        (filtered_df['Weighted Efficiency (%)'].astype(float) >= efficiency_range[0]) &
        (filtered_df['Weighted Efficiency (%)'].astype(float) <= efficiency_range[1])
    ]

# Display filtered data
st.subheader("Filtered Inverters")
st.write(f"Showing {len(filtered_df)} inverters")

# Select columns to display
all_columns = df.columns.tolist()
default_columns = ['inverter_id', 'Manufacturer Name', 'Model Number1', 'Weighted Efficiency (%)', 'Maximum Continuous Output Power at Unity Power Factor ((kW))', 'Date Added to Tool']
default_columns = [col for col in default_columns if col in all_columns]

selected_columns = st.multiselect(
    "Select columns to display",
    all_columns,
    default=default_columns
)

if selected_columns:
    st.dataframe(filtered_df[selected_columns], use_container_width=True)
else:
    st.dataframe(filtered_df, use_container_width=True)

# Data visualization
st.subheader("Data Visualization")
chart_type = st.selectbox(
    "Select chart type",
    ["Manufacturer Distribution", "Efficiency Comparison", "Correlation Plot"]
)

if chart_type == "Manufacturer Distribution":
    fig = px.pie(
        filtered_df,
        names='Manufacturer',
        title='Inverters by Manufacturer',
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    st.plotly_chart(fig, use_container_width=True)

elif chart_type == "Efficiency Comparison" and 'CEC Weighted Efficiency (%)' in df.columns:
    fig = px.box(
        filtered_df,
        x='Manufacturer',
        y='CEC Weighted Efficiency (%)',
        title='Efficiency Comparison by Manufacturer',
        color='Manufacturer',
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    st.plotly_chart(fig, use_container_width=True)

elif chart_type == "Correlation Plot":
    # Select only numeric columns for correlation
    numeric_cols = filtered_df.select_dtypes(include=['float64', 'int64']).columns.tolist()
    
    if len(numeric_cols) >= 2:
        x_axis = st.selectbox("X-axis", numeric_cols, index=0)
        y_axis = st.selectbox("Y-axis", numeric_cols, index=min(1, len(numeric_cols)-1))
        
        fig = px.scatter(
            filtered_df,
            x=x_axis,
            y=y_axis,
            color='Manufacturer',
            hover_name='Model',
            title=f'{y_axis} vs {x_axis}',
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Not enough numeric columns available for correlation plot.")

# Inverter comparison
st.subheader("Inverter Comparison")
st.markdown("Select inverters to compare their specifications side by side.")

# Get list of inverters
inverter_list = filtered_df['inverter_id'].tolist()
if len(inverter_list) > 1:
    selected_inverters = st.multiselect(
        "Select inverters to compare",
        inverter_list,
        max_selections=3
    )
    
    if selected_inverters:
        comparison_df = filtered_df[filtered_df['inverter_id'].isin(selected_inverters)]
        
        # Transpose the dataframe for side-by-side comparison
        comparison_df = comparison_df.set_index('inverter_id').T
        
        st.dataframe(comparison_df, use_container_width=True)
else:
    st.info("Apply filters to see more inverters for comparison.")

# Footer
st.markdown("---")
st.markdown("Data source: California Energy Commission")
st.markdown(f"Last updated: {datetime.now().strftime('%Y-%m-%d')}")
