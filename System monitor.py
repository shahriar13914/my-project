import psutil
import time
import csv
import os
from datetime import datetime

# --- Configuration ---
LOG_FILE = 'system_performance.csv'
INTERVAL_SECONDS = 5  # How often to sample data (in seconds)
MAX_LOG_ENTRIES = 100 # Maximum number of entries to keep in the log file

def initialize_log_file(filename):
    """
    Initializes the CSV log file with headers if it doesn't exist.
    """
    # Check if the file exists and is not empty
    if not os.path.exists(filename) or os.stat(filename).st_size == 0:
        try:
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Timestamp', 'CPU_Usage_Percent', 'Memory_Usage_Percent'])
            print(f"Log file '{filename}' initialized with headers.")
        except IOError as e:
            print(f"Error initializing log file: {e}")
            return False
    else:
        print(f"Log file '{filename}' already exists.")
    return True

def get_performance_data():
    """
    Fetches the current CPU and memory usage.
    Returns a tuple (cpu_percent, memory_percent).
    """
    try:
        # Get CPU usage percentage. interval=None makes it non-blocking,
        # but subsequent calls will compare with the last call.
        # For a single, instantaneous reading, it's fine.
        # For a more accurate average over 'interval', psutil.cpu_percent(interval=1) is better
        # but we're controlling the interval outside.
        cpu_usage = psutil.cpu_percent(interval=0.1) # A small interval for a more accurate instantaneous reading

        # Get virtual memory usage details
        memory_info = psutil.virtual_memory()
        memory_usage = memory_info.percent # Percentage of total memory used

        return cpu_usage, memory_usage
    except Exception as e:
        print(f"Error getting performance data: {e}")
        return None, None

def log_performance_data(filename, cpu_usage, memory_usage):
    """
    Appends the performance data to the CSV log file.
    """
    try:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(filename, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, cpu_usage, memory_usage])
        print(f"Logged: {timestamp} - CPU: {cpu_usage}% | Memory: {memory_usage}%")
    except IOError as e:
        print(f"Error writing to log file: {e}")

def rotate_log_file(filename, max_entries):
    """
    Reads the log file, keeps only the last 'max_entries' lines,
    and overwrites the file. This prevents the log from growing indefinitely.
    """
    try:
        with open(filename, 'r', newline='') as f:
            reader = csv.reader(f)
            header = next(reader) # Read header
            lines = list(reader)  # Read all data lines

        if len(lines) > max_entries:
            lines_to_keep = lines[-max_entries:]
            print(f"Log file rotating: Keeping last {len(lines_to_keep)} entries.")
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(header) # Write header back
                writer.writerows(lines_to_keep) # Write kept lines
    except FileNotFoundError:
        print(f"Log file '{filename}' not found for rotation.")
    except Exception as e:
        print(f"Error rotating log file: {e}")

def main():
    """
    Main function to run the system monitoring.
    """
    print("Starting system performance monitor...")
    print(f"Logging to: {LOG_FILE}")
    print(f"Sampling every: {INTERVAL_SECONDS} seconds")
    print(f"Max log entries: {MAX_LOG_ENTRIES}")
    print("-" * 30)

    # Initialize log file
    if not initialize_log_file(LOG_FILE):
        print("Exiting due to log file initialization error.")
        return

    try:
        while True:
            cpu, memory = get_performance_data()
            if cpu is not None and memory is not None:
                log_performance_data(LOG_FILE, cpu, memory)
                rotate_log_file(LOG_FILE, MAX_LOG_ENTRIES) # Rotate after logging
            time.sleep(INTERVAL_SECONDS)
    except KeyboardInterrupt:
        print("\nSystem performance monitor stopped by user.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    # Ensure psutil is installed: pip install psutil
    try:
        import psutil
    except ImportError:
        print("The 'psutil' library is required. Please install it using: pip install psutil")
        exit(1)
    main()

