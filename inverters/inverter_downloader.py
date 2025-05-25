import requests
import pandas as pd
import sqlite3
from io import BytesIO
from datetime import datetime

# Step 1: Download the Excel file
url = 'https://solarequipment.energy.ca.gov/Home/DownloadtoExcel?filename=InvertersList'
response = requests.get(url)
if response.status_code != 200:
    raise Exception(f"Failed to download file: {response.status_code}")

# Step 2: Load the Excel file into a pandas DataFrame
# Skip to row 14 (0-indexed, so this is the 15th row) for headers
# And use row 15 (0-indexed, so this is the 16th row) for units
excel_data = BytesIO(response.content)
df_headers = pd.read_excel(excel_data, engine='openpyxl', header=14, nrows=1)
excel_data.seek(0)  # Reset the file pointer
df_units = pd.read_excel(excel_data, engine='openpyxl', header=None, skiprows=15, nrows=1)

# Get the actual data starting from row 16 (0-indexed, so this is the 17th row)
excel_data.seek(0)  # Reset the file pointer
df = pd.read_excel(excel_data, engine='openpyxl', header=14, skiprows=2)

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

# Step 3: Create a unique identifier for each inverter
# We'll use a combination of Manufacturer Name and Model Number1
# Convert to string first to handle any numeric values
df['inverter_id'] = df['Manufacturer Name'].astype(str) + '_' + df['Model Number1'].astype(str)

# Step 4: Add a timestamp for when the data was added to the tool
current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
df['Date Added to Tool'] = current_time

# Step 5: Connect to SQLite database (or create it) using context manager
with sqlite3.connect('inverters.db') as conn:
    cursor = conn.cursor()

    # Step 6: Check if the table exists, if not create it with a primary key
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='inverters'")
    table_exists = cursor.fetchone() is not None

    # Also check if inverter_id column exists in the table
    inverter_id_exists = False
    if table_exists:
        try:
            cursor.execute("SELECT inverter_id FROM inverters LIMIT 1")
            inverter_id_exists = True
        except sqlite3.OperationalError:
            # inverter_id column doesn't exist, we'll need to recreate the table
            inverter_id_exists = False

    if not table_exists or not inverter_id_exists:
        # If table doesn't exist or doesn't have inverter_id, drop it and recreate
        if table_exists:
            cursor.execute("DROP TABLE inverters")
            print("Dropping existing table to add primary key and Date Added to Tool column.")
        
        # Handle NaT values and Timestamp objects in the dataframe before insertion
        for col in df.columns:
            df[col] = df[col].apply(lambda x: None if pd.isna(x) or str(x) == 'NaT' 
                                  else x.strftime('%Y-%m-%d %H:%M:%S') if isinstance(x, pd.Timestamp) 
                                  else x)
        
        # Create the table with inverter_id as primary key
        columns = df.columns
        column_defs = []
        for col in columns:
            if col == 'inverter_id':
                column_defs.append(f'"{col}" TEXT PRIMARY KEY')
            else:
                column_defs.append(f'"{col}" TEXT')
        
        columns_str = ', '.join(column_defs)
        create_table_query = f'CREATE TABLE IF NOT EXISTS inverters ({columns_str});'
        cursor.execute(create_table_query)
        
        # Insert all data - use try/except to handle any integrity errors
        try:
            # First try with if_exists='append'
            df.to_sql('inverters', conn, if_exists='append', index=False)
            print(f"Created new table and inserted {len(df)} rows.")
        except sqlite3.IntegrityError:
            # If we get integrity errors, try inserting one by one
            print("Handling duplicate primary keys...")
            inserted = 0
            for _, row in df.iterrows():
                try:
                    pd.DataFrame([row]).to_sql('inverters', conn, if_exists='append', index=False)
                    inserted += 1
                except sqlite3.IntegrityError:
                    # Skip duplicates
                    pass
            print(f"Inserted {inserted} rows, skipped {len(df) - inserted} duplicates.")
        except Exception as e:
            print(f"Error inserting data: {e}")
    else:
        # Table exists with inverter_id column, we need to handle upserts
        # First, get existing inverter_ids
        cursor.execute("SELECT inverter_id FROM inverters")
        existing_ids = [row[0] for row in cursor.fetchall()]
        
        # Split dataframe into new and existing records
        df_new = df[~df['inverter_id'].isin(existing_ids)]
        df_update = df[df['inverter_id'].isin(existing_ids)]
        
        # Insert new records
        if not df_new.empty:
            # Insert one by one to handle any potential integrity errors
            inserted = 0
            for _, row in df_new.iterrows():
                try:
                    pd.DataFrame([row]).to_sql('inverters', conn, if_exists='append', index=False)
                    inserted += 1
                except sqlite3.IntegrityError:
                    # Skip duplicates
                    pass
            print(f"Inserted {inserted} new inverters.")
        else:
            print("No new inverters to insert.")
        
        # Update existing records
        update_count = 0
        for _, row in df_update.iterrows():
            inverter_id = row['inverter_id']
            
            # Build update query dynamically
            update_parts = []
            params = []
            
            for col in df.columns:
                if col != 'inverter_id':
                    update_parts.append(f'"{col}" = ?')
                    # Handle NaT values and Timestamp objects
                    value = row[col]
                    if pd.isna(value) or str(value) == 'NaT':
                        params.append(None)
                    elif isinstance(value, pd.Timestamp):
                        # Convert Timestamp to string format
                        params.append(value.strftime('%Y-%m-%d %H:%M:%S'))
                    else:
                        params.append(value)
            
            update_query = f'UPDATE inverters SET {", ".join(update_parts)} WHERE inverter_id = ?'
            params.append(inverter_id)
            
            cursor.execute(update_query, params)
            update_count += cursor.rowcount
        
        print(f"Updated {update_count} existing inverters.")

    # Connection will be automatically committed and closed by the context manager

print("Inverter data has been successfully downloaded and stored in the database.")
print(f"Total rows: {len(df)}")
print(f"Total columns: {len(df.columns)}")
print("\nFirst 5 column names:")
for i, col in enumerate(df.columns[:5]):
    print(f"{i+1}. {col}")
