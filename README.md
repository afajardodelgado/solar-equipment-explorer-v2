# PV Module Explorer

A data processing and visualization tool for exploring photovoltaic (PV) module data from the California Energy Commission.

## Features

- **Data Acquisition**: Automatically downloads PV module data from the California Energy Commission
- **Database Storage**: Stores data in an SQLite database with proper schema and primary keys
- **Data Exploration**: Interactive UI for filtering and exploring module specifications
- **Visualization**: Charts and comparisons to analyze module performance
- **Export Capabilities**: Export filtered data to CSV for further analysis

## Components

- `pv_module_downloader.py`: Downloads and processes the Excel file, storing data in SQLite
- `pv_explorer.py`: Streamlit-based UI for exploring and visualizing the data
- `list_db_columns.py`: Utility script to view database schema
- `export_with_dates.py`: Exports data with properly formatted dates

## Installation

1. Clone this repository
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Download and update the database:
   ```
   python pv_module_downloader.py
   ```

2. Launch the exploration UI:
   ```
   streamlit run pv_explorer.py
   ```

3. View database schema:
   ```
   python list_db_columns.py
   ```

## Data Structure

The database includes comprehensive information about PV modules including:
- Manufacturer and model details
- Power specifications (Pmax, Isc, Voc, etc.)
- Physical characteristics
- Certification information
- Temperature coefficients
- Unique module ID and timestamp of when data was added

## License

This project is for educational and research purposes.
