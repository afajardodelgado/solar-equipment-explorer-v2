import subprocess
import os
import sys
from pathlib import Path

def run_downloaders():
    """Run all data downloaders to set up the databases."""
    print("Setting up databases...")
    
    # Get base directory
    base_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    
    # Get Python executable
    python_executable = sys.executable
    
    # List of downloader scripts to run with absolute paths
    downloaders = [
        base_dir / "pv_module_downloader.py",
        base_dir / "inverters" / "inverter_downloader.py",
        base_dir / "batteries" / "battery_downloader.py",
        base_dir / "storage" / "energy_storage_downloader.py",
        base_dir / "meters" / "meter_downloader.py"
    ]
    
    # Run each downloader
    for downloader in downloaders:
        downloader_str = str(downloader)
        print(f"Running {downloader_str}...")
        try:
            subprocess.run([python_executable, downloader_str], check=True)
            print(f"Successfully ran {downloader_str}")
        except subprocess.CalledProcessError as e:
            print(f"Error running {downloader_str}: {e}")
        except Exception as e:
            print(f"Unexpected error running {downloader_str}: {e}")
    
    print("Database setup complete!")

if __name__ == "__main__":
    run_downloaders()
