# Solar Equipment Explorer

A data processing and visualization tool for exploring solar equipment data from the California Energy Commission, including PV modules, inverters, energy storage systems, batteries, and meters.

## Features

- **Data Acquisition**: Automatically downloads PV module and inverter data from the California Energy Commission
- **Database Storage**: Stores data in SQLite databases with proper schema and primary keys
- **Data Exploration**: Interactive UIs for filtering and exploring equipment specifications
- **Visualization**: Charts and comparisons to analyze equipment performance
- **Export Capabilities**: Export filtered data to CSV for further analysis

## Project Structure

### Main Application
- `solar_explorer.py`: Streamlit-based UI for exploring and visualizing all equipment types
- `start_app.py`: Wrapper script to launch the Streamlit app with warning filters
- `setup.py`: Sets up the application by running all downloader scripts

### Data Downloaders
- `modules/pv_module_downloader.py`: Downloads and processes the PV module Excel file
- `inverters/inverter_downloader.py`: Downloads and processes the inverter Excel file
- `storage/energy_storage_downloader.py`: Downloads and processes the energy storage systems Excel file
- `batteries/battery_downloader.py`: Downloads and processes the batteries Excel file
- `meters/meter_downloader.py`: Downloads and processes the meters Excel file

### Database Files
- `db/`: Directory containing all SQLite database files
  - `pv_modules.db`: PV modules database
  - `inverters.db`: Inverters database
  - `energy_storage.db`: Energy storage systems database
  - `batteries.db`: Batteries database
  - `meters.db`: Meters database

### Utility Scripts
- `utils/`: Directory containing utility scripts for data analysis and export

### Deployment Configuration
- `Procfile`: Configuration for Railway deployment
- `railway.json` and `railway.toml`: Railway platform configuration files
- `requirements.txt`: Python dependencies

## Installation and Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Set up databases
python setup.py

# Run the application
python start_app.py
```

## Deployment

This application is configured for deployment on Railway. The deployment process is automated through the Procfile and Railway configuration files.


## Installation

1. Clone this repository
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Download and update the databases:
   ```
   python pv_module_downloader.py           # For PV modules
   python inverters/inverter_downloader.py  # For inverters
   python storage/energy_storage_downloader.py  # For energy storage systems
   python batteries/battery_downloader.py    # For batteries
   python meters/meter_downloader.py         # For meters
   ```
   Or run all downloaders at once:
   ```
   python setup.py
   ```

2. Launch the application:
   ```
   streamlit run solar_explorer.py
   ```

3. View database schema:
   ```
   python list_db_columns.py
   ```

## Deployment

### Deploying to Railway

1. Create a Railway account at [railway.app](https://railway.app/)

2. Install the Railway CLI:
   ```
   npm i -g @railway/cli
   ```

3. Login to Railway:
   ```
   railway login
   ```

4. Initialize a new Railway project in your repository:
   ```
   railway init
   ```

5. Deploy your application:
   ```
   railway up
   ```

6. Open your deployed application:
   ```
   railway open
   ```

The application will automatically download all required data during the deployment process using the `setup.py` script.

## Data Structure

The databases include comprehensive information about various solar equipment:

### PV Modules
- Manufacturer and model details
- Power specifications (Pmax, Isc, Voc, etc.)
- Physical characteristics
- Certification information
- Temperature coefficients
- Unique module ID and timestamp of when data was added

### Inverters
- Manufacturer and model details
- Power ratings and efficiency
- Grid support capabilities
- Certification information
- Unique inverter ID and timestamp of when data was added

### Energy Storage Systems
- Manufacturer and model details
- Chemistry and capacity
- Power ratings and voltage
- PV DC input capability
- Certification information
- Unique storage ID and timestamp of when data was added

### Batteries
- Manufacturer and model details
- Chemistry and capacity
- Discharge rate and efficiency
- Certification information
- Unique battery ID and timestamp of when data was added

### Meters
- Manufacturer and model details
- Display type and PBI meter status
- Notes and listing dates
- Unique meter ID and timestamp of when data was added

## License

This project is for educational and research purposes.
