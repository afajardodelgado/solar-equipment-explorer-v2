import sqlite3
import pandas as pd

# Connect to the SQLite database
conn = sqlite3.connect('pv_modules.db')

# Execute a SELECT * query to see all data
query = "SELECT * FROM pv_modules"
df = pd.read_sql_query(query, conn)

# Display basic information about the database
print(f"Database contains {len(df)} rows and {len(df.columns)} columns")

# Display the first 10 rows with all columns
print("\nFirst 10 rows (all columns):")
pd.set_option('display.max_columns', None)  # Show all columns
pd.set_option('display.width', 1000)  # Increase display width
pd.set_option('display.max_colwidth', 30)  # Limit column width for readability
print(df.head(10))

# Display all column names
print("\nAll column names:")
for i, col in enumerate(df.columns):
    print(f"{i+1}. {col}")

# Close the connection
conn.close()

# If you want to run a specific query, you can uncomment and modify the following:
"""
def run_custom_query(query):
    conn = sqlite3.connect('pv_modules.db')
    result = pd.read_sql_query(query, conn)
    conn.close()
    return result

# Example queries:
# 1. Count of records
# result = run_custom_query("SELECT COUNT(*) FROM pv_modules")

# 2. Filter by a specific column (replace 'ColumnName' with actual column name)
# result = run_custom_query("SELECT * FROM pv_modules WHERE \"ColumnName\" = 'SomeValue' LIMIT 10")

# 3. Get unique values in a column
# result = run_custom_query("SELECT DISTINCT \"ColumnName\" FROM pv_modules")

# print(result)
"""
