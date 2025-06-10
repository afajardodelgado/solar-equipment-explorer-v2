import requests
import pandas as pd
import sqlite3
from io import BytesIO
from datetime import datetime

# Step 1: Download the Excel file
url = 'https://solarequipment.energy.ca.gov/Home/DownloadtoExcel?filename=BatteryList'
response = requests.get(url)
if response.status_code != 200:
    raise Exception(f"Failed to download file: {response.status_code}")

# Step 2: Load the Excel file into a pandas DataFrame
# Skip to row 12 (0-indexed, so this is the 13th row) for headers
# Data starts from row 13 (0-indexed, so this is the 14th row)
excel_data = BytesIO(response.content)
df_headers = pd.read_excel(excel_data, engine='openpyxl', header=12, nrows=1)
excel_data.seek(0)  # Reset the file pointer

# Get the actual data starting from row 13 (0-indexed, so this is the 14th row)
excel_data.seek(0)  # Reset the file pointer
df = pd.read_excel(excel_data, engine='openpyxl', header=12, skiprows=1)

# Use the header names as is
df.columns = df_headers.columns

# Print column names to debug
print("Available columns:")
for i, col in enumerate(df.columns):
    print(f"{i}: {col}")

# Print the first row's values to debug
print("\nFirst row values:")
for i, val in enumerate(df.iloc[0]):
    print(f"{i}: {val}")

# Define the current time for the timestamp
current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# Create a new DataFrame with only the columns we need
new_df = pd.DataFrame()

# Map the columns from the original DataFrame to our standardized names
# We'll adjust these based on the actual column names in the data
try:
    # Map columns according to the Excel structure provided by the user
    # Excel column A: Manufacturer Name
    new_df['Manufacturer'] = df.iloc[:, 0]
    
    # Excel Column C: Model Number
    new_df['Model Number'] = df.iloc[:, 2]
    
    # Excel Column D: Technology
    new_df['Chemistry'] = df.iloc[:, 3]
    
    # Excel Column E: Description
    new_df['Description'] = df.iloc[:, 4]
    
    # Excel Column F: Certifying Entity
    new_df['Certifying Entity'] = df.iloc[:, 5]
    
    # Excel Column G: Certificate Date
    new_df['Certificate Date'] = df.iloc[:, 6]
    
    # Excel Column I: Nameplate Energy Capacity
    new_df['Capacity (kWh)'] = df.iloc[:, 8]
    
    # Excel Column J: Maximum Continuous Discharge Rate
    new_df['Discharge Rate (kW)'] = df.iloc[:, 9]
    
    # Excel Column K: Manufacturers Declared Roundtrip Efficiency
    new_df['Round Trip Efficiency (%)'] = df.iloc[:, 10]
    
    # Excel Column O: CEC Listing Date
    new_df['Battery Listing Date'] = df.iloc[:, 14]
    
    # Excel Column P: Last Update Date
    new_df['Last Update'] = df.iloc[:, 15]
    
    # Add the Date Added to Tool column
    new_df['Date Added to Tool'] = current_time
    
    # Create a unique identifier for each battery
    new_df['battery_id'] = new_df['Manufacturer'].astype(str) + '_' + new_df['Model Number'].astype(str)
    
    # Print the columns in our new DataFrame
    print("\nNew DataFrame columns:")
    for col in new_df.columns:
        print(f"- {col}")
    
    # Replace the original DataFrame with our new one
    df = new_df
    
except Exception as e:
    print(f"Error mapping columns: {e}")
    # If we encounter an error, we'll create a minimal DataFrame with just the essential columns
    new_df = pd.DataFrame()
    new_df['Manufacturer'] = df.iloc[:, 0]  # First column as manufacturer
    new_df['Model Number'] = df.iloc[:, 2]  # Third column as model number (column C)
    new_df['Chemistry'] = df.iloc[:, 3]  # Fourth column as chemistry (column D)
    new_df['Description'] = df.iloc[:, 4]  # Fifth column as description (column E)
    new_df['Capacity (kWh)'] = df.iloc[:, 8]  # Ninth column as capacity (column I)
    new_df['Discharge Rate (kW)'] = df.iloc[:, 9]  # Tenth column as discharge rate (column J)
    new_df['Round Trip Efficiency (%)'] = df.iloc[:, 10]  # Eleventh column as efficiency (column K)
    new_df['Battery Listing Date'] = df.iloc[:, 14]  # Fifteenth column as listing date (column O)
    new_df['Last Update'] = df.iloc[:, 15]  # Sixteenth column as last update (column P)
    new_df['Date Added to Tool'] = current_time
    new_df['battery_id'] = new_df['Manufacturer'].astype(str) + '_' + new_df['Model Number'].astype(str)
    df = new_df
    print("Created minimal DataFrame due to error")

# Step 5: Connect to SQLite database (or create it) using context manager
with sqlite3.connect('batteries.db') as conn:
    cursor = conn.cursor()

    # Step 6: Check if the table exists, if not create it with a primary key
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='batteries'")
    table_exists = cursor.fetchone() is not None

    # We're going to drop and recreate the table to ensure it has the correct structure
    if table_exists:
        cursor.execute("DROP TABLE batteries")
        print("Dropping existing table to create it with the correct columns.")
    
    # Handle NaT values and Timestamp objects in the dataframe before insertion
    for col in df.columns:
        df[col] = df[col].apply(lambda x: None if pd.isna(x) or str(x) == 'NaT' 
                              else x.strftime('%Y-%m-%d %H:%M:%S') if isinstance(x, pd.Timestamp) 
                              else x)
    
    # Create the table with battery_id as primary key
    columns = df.columns
    column_defs = []
    for col in columns:
        if col == 'battery_id':
            column_defs.append(f'"{col}" TEXT PRIMARY KEY')
        else:
            column_defs.append(f'"{col}" TEXT')
    
    columns_str = ', '.join(column_defs)
    create_table_query = f'CREATE TABLE IF NOT EXISTS batteries ({columns_str});'
    print(f"Creating table with columns: {columns_str}")
    cursor.execute(create_table_query)
    
    # Insert all data - use try/except to handle any integrity errors
    try:
        # First try with if_exists='replace' to ensure we have a clean table
        df.to_sql('batteries', conn, if_exists='replace', index=False)
        print(f"Created new table and inserted {len(df)} rows.")
    except Exception as e:
        print(f"Error inserting data: {e}")
        # If we get errors, try inserting one by one
        print("Trying to insert rows one by one...")
        inserted = 0
        for _, row in df.iterrows():
            try:
                pd.DataFrame([row]).to_sql('batteries', conn, if_exists='append', index=False)
                inserted += 1
            except Exception as e:
                print(f"Error inserting row: {e}")
                # Skip problematic rows
                pass
        print(f"Inserted {inserted} rows out of {len(df)}.")
    
    # Connection will be automatically committed and closed by the context manager

print("Battery data has been successfully downloaded and stored in the database.")
print(f"Total rows: {len(df)}")
print(f"Total columns: {len(df.columns)}")
print("\nFirst 5 column names:")
for i, col in enumerate(df.columns[:5]):
    print(f"{i+1}. {col}")
