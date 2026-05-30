import os
import zipfile
import requests
import pandas as pd
import json
from datetime import datetime
from io import BytesIO

# Function to download and extract the ZIP file
def download_and_extract_zip(url, headers, extract_to):
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        with zipfile.ZipFile(BytesIO(response.content)) as z:
            z.extractall(extract_to)
        print(f"ZIP file extracted to {extract_to}")
    else:
        print(f"Failed to download ZIP file: {response.status_code}")
        return None

# Function to process the extracted JSON files and save them to CSV
def process_json_files(extract_to, output_dir, cik):
    json_file = os.path.join(extract_to, f"{cik}.json")
    if os.path.exists(json_file):
        with open(json_file, 'r') as f:
            data = json.load(f)
            save_json_to_csv(data, output_dir)
    else:
        print(f"JSON file for CIK {cik} not found in the extracted data.")

# Function to save JSON data to CSV files by date and form name
def save_json_to_csv(data, output_dir):
    if 'filings' in data and 'recent' in data['filings']:
        recent_filings = data['filings']['recent']
        
        for i in range(len(recent_filings.get('form', []))):
            form = recent_filings['form'][i]
            date = recent_filings['filingDate'][i]
            document_url = f"https://www.sec.gov/Archives/edgar/data/{data['cik']}/{recent_filings['accessionNumber'][i].replace('-', '')}/{recent_filings['primaryDocument'][i]}"

            # Prepare the data for the DataFrame
            row_data = {
                "Form": form,
                "Date": date,
                "URL": document_url
            }

            # Create a DataFrame
            df = pd.DataFrame([row_data])

            # Define the filename based on date and form name
            date_str = datetime.strptime(date, "%Y-%m-%d").strftime("%Y%m%d")
            filename = f"{date_str}_{form}.csv"
            file_path = os.path.join(output_dir, filename)

            # Check if the file already exists
            if os.path.exists(file_path):
                # If it exists, append the new data without writing the header
                df.to_csv(file_path, mode='a', header=False, index=False)
            else:
                # If it doesn't exist, write the data with the header
                df.to_csv(file_path, mode='w', header=True, index=False)

            print(f"Data saved to {file_path}")

# Main function to run the script
def main():
    # API URL to the ZIP file
    api_url = "https://www.sec.gov/Archives/edgar/daily-index/xbrl/companyfacts.zip"
    headers = {
        "User-Agent": "brandon.hardison@gmail.com"  # Replace with your details
    }

    # Directory to extract the ZIP file and save CSV files
    extract_to = "/Users/b/Desktop/SEC/Project/Extracted"
    output_dir = "/Users/b/Desktop/SEC/Project/CSV"
    os.makedirs(extract_to, exist_ok=True)  # Ensure the directory exists
    os.makedirs(output_dir, exist_ok=True)  # Ensure the directory exists

    # Download and extract the ZIP file
    download_and_extract_zip(api_url, headers, extract_to)

    # Process the extracted JSON files and save them to CSV for the specified CIK
    cik = "0001326380"  # CIK for GameStop
    process_json_files(extract_to, output_dir, cik)

if __name__ == "__main__":
    main()