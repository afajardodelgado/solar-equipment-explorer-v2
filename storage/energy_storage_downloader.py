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
# Skip to row 17 (0-indexed, so this is the 18th row) for headers
# Data starts from row 18 (0-indexed, so this is the 19th row)
excel_data = BytesIO(response.content)
df_headers = pd.read_excel(excel_data, engine='openpyxl', header=17, nrows=1)
excel_data.seek(0)  # Reset the file pointer

# Get the actual data starting from row 18 (0-indexed, so this is the 19th row)
excel_data.seek(0)  # Reset the file pointer
df = pd.read_excel(excel_data, engine='openpyxl', header=17, skiprows=1)

# Use the header names as is
df.columns = df_headers.columns

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

# Map columns according to the Excel structure provided by the user
# Column A: Manufacturer Name
new_df['Manufacturer'] = df.iloc[:, 0]

# Column C: Model Number
new_df['Model Number'] = df.iloc[:, 2]

# Column D: Technology
new_df['Chemistry'] = df.iloc[:, 3]

# Column E: PV DC Input Capability (Y/N)
new_df['PV DC Input Capability'] = df.iloc[:, 4]

# Column F: Certifying Entity
new_df['Certifying Entity'] = df.iloc[:, 5]

# Column G: Certificate Date
new_df['Certificate Date'] = df.iloc[:, 6]

# Column P: Description
new_df['Description'] = df.iloc[:, 15]

# Column Q: Nameplate Energy Capacity
new_df['Capacity (kWh)'] = df.iloc[:, 16]

# Column R: Nameplate Power
new_df['Continuous Power Rating (kW)'] = df.iloc[:, 17]

# Column S: Nominal Voltage
new_df['Voltage (Vac)'] = df.iloc[:, 18]

# Column T: Maximum Continuous Discharge Rate
new_df['Maximum Discharge Rate (kW)'] = df.iloc[:, 19]

# Column AI: CEC Listing Date
new_df['Energy Storage Listing Date'] = df.iloc[:, 34]

# Column AJ: Last Update
new_df['Last Update'] = df.iloc[:, 35]

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
