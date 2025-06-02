#!/usr/bin/env python
"""
Streamlit app launcher that suppresses coroutine warnings.
This script launches the solar_explorer.py Streamlit app with warning filters
to prevent the 'coroutine was never awaited' warnings.
"""
import os
import sys
import warnings
import subprocess

# Filter warnings at the Python level
warnings.filterwarnings("ignore", category=RuntimeWarning, message="coroutine.*never awaited")
warnings.filterwarnings("ignore", category=RuntimeWarning, message="Enable tracemalloc.*")

# Disable asyncio debug mode via environment variables
os.environ["PYTHONWARNINGS"] = "ignore::RuntimeWarning:asyncio"

def main():
    """Run the Streamlit app with warning filters applied."""
    print("Starting Solar Equipment Explorer with warning filters...")
    
    # Get the Python executable path
    python_exe = sys.executable
    
    # Construct the command to run streamlit with the warning filter
    cmd = [
        python_exe, 
        "-W", "ignore::RuntimeWarning:asyncio",
        "-m", "streamlit", 
        "run", 
        "solar_explorer.py"
    ]
    
    # Add any command line arguments passed to this script
    if len(sys.argv) > 1:
        cmd.extend(sys.argv[1:])
    
    # Run the Streamlit app with warning filters
    subprocess.run(cmd)

if __name__ == "__main__":
    main()
