import sqlite3
import pandas as pd
import os
from datetime import datetime

# Connect to the SQLite database
conn = sqlite3.connect('pv_modules.db')

# Execute a SELECT * LIMIT 100 query
query = "SELECT * FROM pv_modules LIMIT 100"
df = pd.read_sql_query(query, conn)

# Identify date columns (based on column names)
date_columns = ['CEC Listing Date', 'Last Update']

# Convert Unix timestamps to readable datetime format
for col in date_columns:
    if col in df.columns:
        # Convert only non-null values
        df[col] = df[col].apply(
            lambda x: datetime.fromtimestamp(int(x)).strftime('%Y-%m-%d %H:%M:%S') 
            if pd.notna(x) and str(x).strip() != "" else x
        )

# Export to CSV
output_file = 'sample_query_with_dates.csv'
df.to_csv(output_file, index=False)

# Close the connection
conn.close()

print(f"Exported {len(df)} rows to {output_file}")
print(f"File contains {len(df.columns)} columns")
print(f"CSV file size: {round(os.path.getsize(output_file) / 1024, 2)} KB")

# Display the first few rows to confirm date conversion
print("\nPreview of the exported data with converted dates (first 5 rows):")
print(df[['Manufacturer', 'Model Number'] + date_columns].head(5))
