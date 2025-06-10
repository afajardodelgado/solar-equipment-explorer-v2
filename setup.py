import subprocess
import os
import sys
import time
import concurrent.futures
from pathlib import Path

# Maximum time to wait for each downloader in seconds
DOWNLOADER_TIMEOUT = 120

# Number of retries for each downloader
MAX_RETRIES = 2

# Check if we're running on Railway
IS_RAILWAY = 'RAILWAY_ENVIRONMENT' in os.environ

def run_downloader(downloader_path, python_executable):
    """Run a single downloader script with timeout and retries."""
    downloader_str = str(downloader_path)
    db_name = os.path.basename(downloader_str).replace('_downloader.py', '.db')
    if 'inverter' in downloader_str:
        db_name = 'inverters.db'
    elif 'energy_storage' in downloader_str:
        db_name = 'energy_storage.db'
    elif 'battery' in downloader_str:
        db_name = 'batteries.db'
    elif 'meter' in downloader_str:
        db_name = 'meters.db'
    elif 'pv_module' in downloader_str:
        db_name = 'pv_modules.db'
    
    # Check if database already exists
    base_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    db_path = base_dir / 'db' / db_name
    
    if db_path.exists() and db_path.stat().st_size > 0:
        print(f"Database {db_name} already exists, skipping download")
        return True
    
    print(f"Running {downloader_str}...")
    
    for attempt in range(MAX_RETRIES + 1):
        try:
            # Run with timeout
            process = subprocess.run(
                [python_executable, downloader_str],
                check=True,
                timeout=DOWNLOADER_TIMEOUT,
                capture_output=True,
                text=True
            )
            print(f"Successfully ran {downloader_str}")
            return True
        except subprocess.TimeoutExpired:
            print(f"Timeout running {downloader_str} (attempt {attempt+1}/{MAX_RETRIES+1})")
            if attempt == MAX_RETRIES:
                print(f"Giving up on {downloader_str} after {MAX_RETRIES+1} attempts")
                # Create an empty file to prevent future download attempts
                if IS_RAILWAY and not db_path.exists():
                    print(f"Creating empty database {db_name} to continue deployment")
                    db_path.touch()
                return False
        except subprocess.CalledProcessError as e:
            print(f"Error running {downloader_str}: {e}")
            print(f"STDOUT: {e.stdout}")
            print(f"STDERR: {e.stderr}")
            if attempt == MAX_RETRIES:
                print(f"Giving up on {downloader_str} after {MAX_RETRIES+1} attempts")
                # Create an empty file to prevent future download attempts
                if IS_RAILWAY and not db_path.exists():
                    print(f"Creating empty database {db_name} to continue deployment")
                    db_path.touch()
                return False
        except Exception as e:
            print(f"Unexpected error running {downloader_str}: {e}")
            if attempt == MAX_RETRIES:
                print(f"Giving up on {downloader_str} after {MAX_RETRIES+1} attempts")
                # Create an empty file to prevent future download attempts
                if IS_RAILWAY and not db_path.exists():
                    print(f"Creating empty database {db_name} to continue deployment")
                    db_path.touch()
                return False
        
        # Wait before retrying
        if attempt < MAX_RETRIES:
            wait_time = 2 ** attempt  # Exponential backoff
            print(f"Waiting {wait_time} seconds before retrying...")
            time.sleep(wait_time)
    
    return False

def run_downloaders():
    """Run all data downloaders to set up the databases."""
    print("Setting up databases...")
    start_time = time.time()
    
    # Get base directory
    base_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    
    # Get Python executable
    python_executable = sys.executable
    
    # List of downloader scripts to run with absolute paths
    downloaders = [
        base_dir / "modules" / "pv_module_downloader.py",
        base_dir / "modules" / "inverter_downloader.py",
        base_dir / "modules" / "battery_downloader.py",
        base_dir / "modules" / "energy_storage_downloader.py",
        base_dir / "modules" / "meter_downloader.py"
    ]
    
    # Run downloaders in parallel if not on Railway
    if not IS_RAILWAY:
        print("Running downloaders in parallel...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = {executor.submit(run_downloader, d, python_executable): d for d in downloaders}
            for future in concurrent.futures.as_completed(futures):
                downloader = futures[future]
                try:
                    success = future.result()
                    if not success:
                        print(f"Warning: Failed to download data for {downloader}")
                except Exception as e:
                    print(f"Exception running {downloader}: {e}")
    else:
        # On Railway, run sequentially to avoid memory issues
        print("Running downloaders sequentially (Railway environment detected)...")
        for downloader in downloaders:
            success = run_downloader(downloader, python_executable)
            if not success:
                print(f"Warning: Failed to download data for {downloader}")
    
    end_time = time.time()
    print(f"Database setup complete in {end_time - start_time:.2f} seconds!")

if __name__ == "__main__":
    run_downloaders()
