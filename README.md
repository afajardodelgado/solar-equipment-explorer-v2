# Solar Equipment Explorer

A data processing and visualization tool for exploring photovoltaic (PV) modules and inverters data from the California Energy Commission.

## Features

- **Data Acquisition**: Automatically downloads PV module and inverter data from the California Energy Commission
- **Database Storage**: Stores data in SQLite databases with proper schema and primary keys
- **Data Exploration**: Interactive UIs for filtering and exploring equipment specifications
- **Visualization**: Charts and comparisons to analyze equipment performance
- **Export Capabilities**: Export filtered data to CSV for further analysis

## Components

### PV Modules
- `modules/pv_module_downloader.py`: Downloads and processes the PV module Excel file, storing data in SQLite
- `modules/pv_explorer.py`: Streamlit-based UI for exploring and visualizing PV module data

### Inverters
- `inverters/inverter_downloader.py`: Downloads and processes the inverter Excel file, storing data in SQLite
- `inverters/inverter_explorer.py`: Streamlit-based UI for exploring and visualizing inverter data

### Utilities
- `list_db_columns.py`: Utility script to view database schema
- `export_with_dates.py`: Exports data with properly formatted dates

## Installation

1. Clone this repository
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Download and update the databases:
   ```
   python modules/pv_module_downloader.py  # For PV modules
   python inverters/inverter_downloader.py  # For inverters
   ```

2. Launch the exploration UIs:
   ```
   streamlit run modules/pv_explorer.py     # For PV modules
   streamlit run inverters/inverter_explorer.py  # For inverters
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
