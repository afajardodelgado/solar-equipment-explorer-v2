import requests
import pandas as pd
import sqlite3
from io import BytesIO
from datetime import datetime

# Step 1: Download the Excel file
url = 'https://solarequipment.energy.ca.gov/Home/DownloadtoExcel?filename=PVModuleList'
response = requests.get(url)
if response.status_code != 200:
    raise Exception(f"Failed to download file: {response.status_code}")

# Step 2: Load the Excel file into a pandas DataFrame
# Skip to row 16 (0-indexed, so this is the 17th row) for headers
# And use row 17 (0-indexed, so this is the 18th row) for units
excel_data = BytesIO(response.content)
df_headers = pd.read_excel(excel_data, engine='openpyxl', header=16, nrows=1)
excel_data.seek(0)  # Reset the file pointer
df_units = pd.read_excel(excel_data, engine='openpyxl', header=None, skiprows=17, nrows=1)

# Get the actual data starting from row 18 (0-indexed, so this is the 19th row)
excel_data.seek(0)  # Reset the file pointer
df = pd.read_excel(excel_data, engine='openpyxl', header=16, skiprows=2)

# Combine column names with units
column_names = []
for i, col in enumerate(df_headers.columns):
    unit = df_units.iloc[0, i] if i < len(df_units.columns) else ""
    if pd.notna(unit) and str(unit).strip() != "":
        column_names.append(f"{col} ({unit})")
    else:
        column_names.append(col)

df.columns = column_names

# Step 3: Create a unique identifier for each module
# We'll use a combination of Manufacturer and Model Number
# Convert to string first to handle any numeric values
df['module_id'] = df['Manufacturer'].astype(str) + '_' + df['Model Number'].astype(str)

# Step 4: Add a timestamp for when the data was added to the tool
current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
df['Date Added to Tool'] = current_time

# Step 5: Connect to SQLite database (or create it)
conn = sqlite3.connect('pv_modules.db')
cursor = conn.cursor()

# Step 6: Check if the table exists, if not create it with a primary key
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='pv_modules'")
table_exists = cursor.fetchone() is not None

# Also check if module_id column exists in the table
module_id_exists = False
if table_exists:
    try:
        cursor.execute("SELECT module_id FROM pv_modules LIMIT 1")
        module_id_exists = True
    except sqlite3.OperationalError:
        # module_id column doesn't exist, we'll need to recreate the table
        module_id_exists = False

if not table_exists or not module_id_exists:
    # If table doesn't exist or doesn't have module_id, drop it and recreate
    if table_exists:
        cursor.execute("DROP TABLE pv_modules")
        print("Dropping existing table to add primary key and Date Added to Tool column.")
    
    # Create the table with module_id as primary key
    columns = df.columns
    column_defs = []
    for col in columns:
        if col == 'module_id':
            column_defs.append(f'"{col}" TEXT PRIMARY KEY')
        else:
            column_defs.append(f'"{col}" TEXT')
    
    columns_str = ', '.join(column_defs)
    create_table_query = f'CREATE TABLE IF NOT EXISTS pv_modules ({columns_str});'
    cursor.execute(create_table_query)
    
    # Handle NaT values and Timestamp objects in the dataframe before insertion
    for col in df.columns:
        df[col] = df[col].apply(lambda x: None if pd.isna(x) or str(x) == 'NaT' 
                              else x.strftime('%Y-%m-%d %H:%M:%S') if isinstance(x, pd.Timestamp) 
                              else x)
    
    # Insert all data - use try/except to handle any integrity errors
    try:
        # First try with if_exists='append'
        df.to_sql('pv_modules', conn, if_exists='append', index=False)
        print(f"Created new table and inserted {len(df)} rows.")
    except sqlite3.IntegrityError:
        # If we get integrity errors, try inserting one by one
        print("Handling duplicate primary keys...")
        inserted = 0
        for _, row in df.iterrows():
            try:
                pd.DataFrame([row]).to_sql('pv_modules', conn, if_exists='append', index=False)
                inserted += 1
            except sqlite3.IntegrityError:
                # Skip duplicates
                pass
        print(f"Inserted {inserted} rows, skipped {len(df) - inserted} duplicates.")
    except Exception as e:
        print(f"Error inserting data: {e}")
else:
    # Table exists with module_id column, we need to handle upserts
    # First, get existing module_ids
    cursor.execute("SELECT module_id FROM pv_modules")
    existing_ids = [row[0] for row in cursor.fetchall()]
    
    # Split dataframe into new and existing records
    df_new = df[~df['module_id'].isin(existing_ids)]
    df_update = df[df['module_id'].isin(existing_ids)]
    
    # Insert new records
    if not df_new.empty:
        # Insert one by one to handle any potential integrity errors
        inserted = 0
        for _, row in df_new.iterrows():
            try:
                pd.DataFrame([row]).to_sql('pv_modules', conn, if_exists='append', index=False)
                inserted += 1
            except sqlite3.IntegrityError:
                # Skip duplicates
                pass
        print(f"Inserted {inserted} new modules.")
    else:
        print("No new modules to insert.")
    
    # Update existing records
    update_count = 0
    for _, row in df_update.iterrows():
        module_id = row['module_id']
        
        # Build update query dynamically
        update_parts = []
        params = []
        
        for col in df.columns:
            if col != 'module_id':
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
        
        update_query = f'UPDATE pv_modules SET {", ".join(update_parts)} WHERE module_id = ?'
        params.append(module_id)
        
        cursor.execute(update_query, params)
        update_count += cursor.rowcount
    
    print(f"Updated {update_count} existing modules.")

# Step 7: Close the database connection
conn.commit()
conn.close()

print("Data has been successfully downloaded and stored in the database.")
print(f"Total rows: {len(df)}")
print(f"Total columns: {len(df.columns)}")
print("\nFirst 5 column names:")
for i, col in enumerate(df.columns[:5]):
    print(f"{i+1}. {col}")
