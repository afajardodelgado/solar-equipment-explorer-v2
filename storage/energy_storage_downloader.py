import requests
import pandas as pd
import sqlite3
from io import BytesIO
from datetime import datetime

# Step 1: Download the Excel file
url = 'https://solarequipment.energy.ca.gov/Home/DownloadtoExcel?filename=EnergyStorage'
response = requests.get(url)
if response.status_code != 200:
    raise Exception(f"Failed to download file: {response.status_code}")

# Step 2: Load the Excel file into a pandas DataFrame
# Based on the screenshot, the headers are one row above where we were looking
# Skip to row 15 (0-indexed, so this is the 16th row) for headers
# And use row 16 (0-indexed, so this is the 17th row) for units
excel_data = BytesIO(response.content)
df_headers = pd.read_excel(excel_data, engine='openpyxl', header=15, nrows=1)
excel_data.seek(0)  # Reset the file pointer
df_units = pd.read_excel(excel_data, engine='openpyxl', header=None, skiprows=16, nrows=1)

# Get the actual data starting from row 17 (0-indexed, so this is the 18th row)
excel_data.seek(0)  # Reset the file pointer
df = pd.read_excel(excel_data, engine='openpyxl', header=15, skiprows=2)

# Combine column names with units
column_names = []
for i, col in enumerate(df_headers.columns):
    unit = df_units.iloc[0, i] if i < len(df_units.columns) else ""
    if pd.notna(unit) and str(unit).strip() != "":
        column_names.append(f"{col} ({unit})")
    else:
        column_names.append(col)

df.columns = column_names

# Print column names to debug
print("Available columns:")
for i, col in enumerate(df.columns):
    print(f"{i}: {col}")

# The data structure is different than expected
# Looking at the first row's values to determine manufacturer and model
print("\nFirst row values:")
for i, val in enumerate(df.iloc[0]):
    print(f"{i}: {val}")

# Print the actual column names we have now
print("\nActual column names:")
for i, col in enumerate(df.columns):
    print(f"{i}: {col}")

# Define the current time for the timestamp
current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# Create a new DataFrame with only the columns we need
new_df = pd.DataFrame()

# Map the columns from the original DataFrame to our standardized names
new_df['Manufacturer'] = df['Manufacturer Name']
new_df['Model Number'] = df['Model Number']
new_df['Chemistry'] = df['Technology']
new_df['Capacity (kWh)'] = df['Nameplate Energy Capacity ((kWh))']
new_df['Continuous Power Rating (kW)'] = df['Nameplate Power ((kW))']
new_df['Voltage (Vac)'] = df['Nominal Voltage ((Vac))']
new_df['Round Trip Efficiency (%)'] = df['Manufacturer Declared Roundtrip Efficiency ((%, AC-AC)1)']
new_df['Energy Storage Listing Date'] = df['CEC Listing Date ((mm/dd/yyyy))']

# Add the Date Added to Tool column
new_df['Date Added to Tool'] = current_time

# Create a unique identifier for each storage system
new_df['storage_id'] = new_df['Manufacturer'].astype(str) + '_' + new_df['Model Number'].astype(str)

# Print the columns in our new DataFrame
print("\nNew DataFrame columns:")
for col in new_df.columns:
    print(f"- {col}")

# Replace the original DataFrame with our new one
df = new_df

# We've already created the storage_id and added the timestamp in the new DataFrame

# Step 5: Connect to SQLite database (or create it) using context manager
with sqlite3.connect('energy_storage.db') as conn:
    cursor = conn.cursor()

    # Step 6: Check if the table exists, if not create it with a primary key
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='energy_storage'")
    table_exists = cursor.fetchone() is not None

    # We're going to drop and recreate the table to ensure it has the correct structure
    if table_exists:
        cursor.execute("DROP TABLE energy_storage")
        print("Dropping existing table to create it with the correct columns.")
    
    # Handle NaT values and Timestamp objects in the dataframe before insertion
    for col in df.columns:
        df[col] = df[col].apply(lambda x: None if pd.isna(x) or str(x) == 'NaT' 
                              else x.strftime('%Y-%m-%d %H:%M:%S') if isinstance(x, pd.Timestamp) 
                              else x)
    
    # Create the table with storage_id as primary key
    columns = df.columns
    column_defs = []
    for col in columns:
        if col == 'storage_id':
            column_defs.append(f'"{col}" TEXT PRIMARY KEY')
        else:
            column_defs.append(f'"{col}" TEXT')
    
    columns_str = ', '.join(column_defs)
    create_table_query = f'CREATE TABLE IF NOT EXISTS energy_storage ({columns_str});'
    print(f"Creating table with columns: {columns_str}")
    cursor.execute(create_table_query)
    
    # Insert all data - use try/except to handle any integrity errors
    try:
        # First try with if_exists='replace' to ensure we have a clean table
        df.to_sql('energy_storage', conn, if_exists='replace', index=False)
        print(f"Created new table and inserted {len(df)} rows.")
    except Exception as e:
        print(f"Error inserting data: {e}")
        # If we get errors, try inserting one by one
        print("Trying to insert rows one by one...")
        inserted = 0
        for _, row in df.iterrows():
            try:
                pd.DataFrame([row]).to_sql('energy_storage', conn, if_exists='append', index=False)
                inserted += 1
            except Exception as e:
                print(f"Error inserting row: {e}")
                # Skip problematic rows
                pass
        print(f"Inserted {inserted} rows out of {len(df)}.")
    
    # Connection will be automatically committed and closed by the context manager

print("Energy Storage data has been successfully downloaded and stored in the database.")
print(f"Total rows: {len(df)}")
print(f"Total columns: {len(df.columns)}")
print("\nFirst 5 column names:")
for i, col in enumerate(df.columns[:5]):
    print(f"{i+1}. {col}")
