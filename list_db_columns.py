import sqlite3
import pandas as pd

def list_db_columns():
    """List all columns in the pv_modules table"""
    try:
        # Connect to the database
        conn = sqlite3.connect('pv_modules.db')
        cursor = conn.cursor()
        
        # Get table info
        cursor.execute("PRAGMA table_info(pv_modules)")
        columns = cursor.fetchall()
        
        # Print column information
        print(f"Found {len(columns)} columns in pv_modules table:")
        print("-" * 80)
        print(f"{'Index':<6} {'Name':<40} {'Type':<10} {'Primary Key':<12}")
        print("-" * 80)
        
        for col in columns:
            cid, name, type_name, notnull, default_value, pk = col
            print(f"{cid:<6} {name:<40} {type_name:<10} {'Yes' if pk else 'No':<12}")
        
        # Also get a sample row to verify data
        cursor.execute("SELECT * FROM pv_modules LIMIT 1")
        sample = cursor.fetchone()
        if sample:
            print("\nSample data available. Number of fields in first row:", len(sample))
        else:
            print("\nNo data found in the table.")
            
        # Close the connection
        conn.close()
        
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_db_columns()
