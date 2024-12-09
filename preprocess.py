import os
import shutil
import subprocess
import sys

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
os.chdir(BASE_DIR)  # Ensure script runs with correct working directory

INPUT_DIR = os.path.join(BASE_DIR, 'Input')
OUTPUT_DIR = os.path.join(BASE_DIR, 'Output')
LOCK_FILE = os.path.join(INPUT_DIR, ".preprocess_done")

# Ensure directories exist
for folder in [INPUT_DIR, OUTPUT_DIR]:
    if not os.path.exists(folder):
        os.makedirs(folder)

def move_input_file(file_name):
    """Move the CSV file to the Input folder."""
    src_file = os.path.join(BASE_DIR, file_name)
    dest_file = os.path.join(INPUT_DIR, file_name)

    if os.path.exists(dest_file):
        print(f"File already exists at {dest_file}, skipping move.")
        return

    if os.path.exists(src_file):
        shutil.move(src_file, dest_file)
        print(f"File moved to {dest_file}")
    else:
        print(f"Error: {file_name} does not exist in the current directory.")

def run_preprocessing_scripts():
    """Run the required scripts for data processing and plotting."""
    try:
        scripts = [
            os.path.join(BASE_DIR, 'pages', 'generate_data.py'),
            os.path.join(BASE_DIR, 'pages', 'table.py'),
            os.path.join(BASE_DIR, 'pages', 'plotting.py'),
        ]
        
        for script in scripts:
            print(f"Running script: {script}")
            subprocess.run([sys.executable, script], check=True)

        # Create lock file after successful run
        with open(LOCK_FILE, 'w') as lock:
            lock.write("Preprocessing complete.")
        print("Preprocessing complete. Lock file created.")
    except subprocess.CalledProcessError as e:
        print(f"Error running script {e.cmd}: {e}")
        sys.exit(1)

def check_and_run_preprocessing(file_name):
    """Delete the lock file if it exists and run preprocessing scripts."""
    print("Deleting the lock file if it exists...")
    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)
        print("Lock file removed.")

    print("Running preprocessing scripts...")
    move_input_file(file_name)  # Move the CSV file to the Input folder
    run_preprocessing_scripts()  # Run the preprocessing scripts
    return True  # Indicate that preprocessing was done

if __name__ == "__main__":
    file_name = "Filled_not filled.csv"
    
    # Always run preprocessing and recreate the lock file
    check_and_run_preprocessing(file_name)
    
    print("Preprocessing finished successfully!")
