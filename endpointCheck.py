import http.client
import csv
import time
from datetime import datetime
from urllib.parse import urlparse

# Configuration
ENDPOINTS = [
    {"url": "https://azgeobp-dev.fs2c.usda.gov/portal/sharing/rest/generateToken", "name": "Dev Portal"},
    {"url": "https://azgeobp-stg.fs2c.usda.gov/portal/sharing/rest/generateToken", "name": "Stage & Sandbox Portal"},
]
CSV_FILE = "endpoint_health_log.csv"
CHECK_INTERVAL = 60  # 10 minutes in seconds

def check_endpoint_health(ENDPOINTS):
    parsed_url = urlparse(ENDPOINTS["url"])
    connection = http.client.HTTPSConnection(parsed_url.netloc, timeout=30)
    try:
        connection.request("GET", parsed_url.path or "/")
        response = connection.getresponse()
        status = "UP" if response.status == 200 else "DOWN"
        status_code = response.status
    finally:
        connection.close()
        del connection  # Ensure the connection object is deleted to clear cache
    return status, status_code

def log_status_to_csv(endpoint, status, status_code):
  
    print(f"[{datetime.now()}] {endpoint['name']} ({endpoint['url']}): {status} (Status Code: {status_code})")   # Print status to terminal
    with open(CSV_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([datetime.now().isoformat(), endpoint["name"], endpoint["url"], status, status_code])

def main():
    # Write CSV header if the file is empty
    try:
        with open(CSV_FILE, mode='x', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Timestamp", "Endpoint Name", "Endpoint URL", "Status", "Status Code"])
    except FileExistsError:
        pass

    while True:
        for endpoint in ENDPOINTS:
            status, status_code = check_endpoint_health(endpoint)
            log_status_to_csv(endpoint, status, status_code)
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
