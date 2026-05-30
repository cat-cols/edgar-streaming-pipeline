import os
import csv
import requests
import xml.etree.ElementTree as ET
import pandas as pd
from datetime import datetime

# Define the directory where the CSV file is located and where results will be saved
csv_file_path = "/Users/b/Desktop/SEC/Project/gamestop_filings_20240903013738.csv"  # Path to your CSV file with links
download_dir = "/Users/b/Desktop/SEC/Project"  # Directory to save results

# Ensure the download directory exists
os.makedirs(download_dir, exist_ok=True)

# Function to fetch and parse XML data from a given URL
def fetch_and_parse_xml(url):
    try:
        response = requests.get(url, headers={"User-Agent": "brandon.hardison@gmail.com"})
        if response.status_code == 200:
            # Parse the XML data
            root = ET.fromstring(response.content)
            return root
        else:
            print(f"Failed to fetch data from {url}. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"An error occurred while fetching data from {url}: {e}")
        return None

# Function to extract relevant data from the XML root element
def extract_data_from_xml(root):
    data = {}
    # Example: Extract data based on specific XML structure
    # Assuming the XML has elements like <FormType>, <FilingDate>, etc.
    for child in root:
        data[child.tag] = child.text
    return data

# Main function to process the CSV file and save extracted data to a new CSV
def main():
    extracted_data = []

    # Read the CSV file with links
    with open(csv_file_path, mode='r') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            if len(row) > 0:
                url = row[0]
                print(f"Processing URL: {url}")

                # Fetch and parse the XML data
                root = fetch_and_parse_xml(url)
                if root is not None:
                    # Extract data from the XML
                    data = extract_data_from_xml(root)
                    extracted_data.append(data)
    
    # Convert extracted data to a DataFrame
    df = pd.DataFrame(extracted_data)

    # Define the filename with a timestamp
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = os.path.join(download_dir, f"extracted_data_{timestamp}.csv")

    # Save the DataFrame to a CSV file
    df.to_csv(filename, index=False)
    
    print(f"Saved extracted data to {filename}")

if __name__ == "__main__":
    main()
