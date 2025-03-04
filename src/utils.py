from oauth2client.service_account import ServiceAccountCredentials
import gspread
import json
import re
import csv
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Helper():
    def __init__(self):
        pass
    
    def to_google_sheet(self, data, sheet_name=None, sheet_url=None):
        try:
            creds_file = "config/cred.json"  # Replace with your credentials file
            
            # women's ice hockey
            # sheet_url = "https://docs.google.com/spreadsheets/d/1CvBlfX2YNMpgqK4_JQOLmtP-35VIIxz1UIhB8V4sut0/edit?gid=1038148581#gid=1038148581"  # Replace with your shared sheet URL

            # men's ice hockey
            # sheet_url = "https://docs.google.com/spreadsheets/d/1mQowKV3QELGZPf0WzHaqyiPKyt-CfBoCOJZ9uIcrIrM/edit?gid=858352977#gid=858352977"  # Replace with your shared sheet URL
            
            sheet = self.setup_google_sheet(creds_file, sheet_url, sheet_name)
        
            self.write_to_google_sheet(sheet, data)
            # self.write_to_json(data, f"output/{filtered_output}")
        except Exception as e:
            print(f"Error: {e}")
    
    @staticmethod
    def setup_google_sheet(creds_file, shared_sheet_url, sheet_name):
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name(creds_file, scope)
        client = gspread.authorize(creds)
        # Open the sheet by URL
        spreadsheet = client.open_by_url(shared_sheet_url)
        if sheet_name:
            sheet = spreadsheet.worksheet(sheet_name)
        else:
            sheet = spreadsheet.sheet1
        return sheet

    # Write data to Google Sheets
    @staticmethod
    def write_to_google_sheet(sheet, data):
        sheet.clear()  # Clear existing data
        if data:
            # Write headers
            headers = list(data[0].keys())
            sheet.insert_row(headers, 1)
            # Prepare data rows
            rows = [list(row.values()) for row in data]
            # Batch update rows
            sheet.insert_rows(rows, 2)
        print("Data written to Google Sheet")
        
    def get_data_from_google_sheet(self, sheet_name=None, sheet_url=None):
        try:
            creds_file = "config/cred.json"  # Replace with your credentials file
            sheet = self.setup_google_sheet(creds_file, sheet_url, sheet_name)
            data = sheet.get_all_records()
            return data
        except Exception as e:
            print(f"Error: {e}")
            return None

    def write_to_json(self, data, filename):
        '''
        write output data to a json file.
        '''
        with open(filename, 'w') as json_file:
            json.dump(data, json_file, indent=4)
        print(f"Data written to {filename}")
        
    def read_from_json(self, filename):
        '''
        read data from a json file.
        this could also use to transform data without scraping website all over again.
        '''
        with open(filename, 'r') as json_file:
            data = json.load(json_file)
        print(f"Data read from {filename}")
        return data
    
    def merge_json_files(self, file1, file2, output_file):
        '''
        Merge two JSON files and write the merged data to a new JSON file.
        '''
        try:
            data1 = self.read_from_json(file1)
            data2 = self.read_from_json(file2)
            merged_data = data1 + data2
            self.write_to_json(merged_data, output_file)
            logging.info(f'Merged data written to {output_file}')
        except Exception as e:
            logging.error(f'Error in merge_json_files: {e}')
    
    def transform_data(self, filename):
        '''
        Transform data by removing the last two digits from the 'Last Name' field.
        '''
        data = self.read_from_json(filename)
        
        # for item in data:
        #     item['Last Name'] = re.sub(r"'\d{2}", "", item['Last Name'])
        return self.sanitize(data)

    def sanitize(self, filename):
        try:
            json_items = self.read_from_json(filename)
            items = self.remove_duplicates(json_items)
            exclude = ['trainer', 'operation', 'operations', 'equipment', 'strength', 'conditioning', 'student', 'students', 'performance', 'volunteer', 'volunteers']
            _temp = []
            for item in items:
                
                # if item['School'] == 'Westfield State University':
                #     print('here')
                if not item['Title']:
                    continue
                # if not item['First Name']:
                #     continue
                item['Last Name'] = re.sub(r"'\d{2}", "", item['Last Name'])
                if not any(exc_item in item['Title'].lower() for exc_item in exclude):
                    if "coach" in item['Title'].lower() or "entraîneur" in item['Title'].lower():
                         _temp.append(item)

            return _temp
        except Exception as e:
            print(f"Error: {e}")
            return None
        
    def remove_duplicates(self, data):
        seen = set()
        unique_data = []
        for item in data:
            item_tuple = tuple(item.items())
            if item_tuple not in seen:
                seen.add(item_tuple)
                unique_data.append(item)
        return unique_data

    def reprocess(self):
        '''
        This function reads the data from the output.json file and reprocesses 
        it to remove the last two digits from the Last Name field.
        We can clean data without having to scrape the websites again.
        This could also be updated to transform the data in any other way.
        '''
        data = self.transform_data('output.json')
        sheet_name = 'List of Coaches (scraped)'
        self.to_google_sheet(data, sheet_name)
        
    def save_to_csv(self, data, filename=None):
        try:
            if filename is None:
                raise ValueError("Filename must be provided")
        
            os.makedirs("output", exist_ok=True)
            file_exists = os.path.isfile(f"output/{filename}")
        
            with open(f"output/{filename}", 'a', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=data[0].keys())
                if not file_exists:
                    writer.writeheader()
                writer.writerows(data)
        except Exception as e:
            logging.error(f'Error in save_to_csv: {e}')
            
    # function to clear csv
    def clear_csv(self, filename):
        try:
            logging.info(f'Clearing {filename}')
            if filename is None:
                raise ValueError("Filename must be provided")
        
            os.makedirs("output", exist_ok=True)
            file_exists = os.path.isfile(f"output/{filename}")
            
            with open(f"output/{filename}", 'w', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=[])
                writer.writeheader()
        except Exception as e:
            logging.error(f'Error in clear_csv: {e}')
            
    def new_csv(self, filename='output.csv'):
        try:
            data = []
            with open(filename, 'w', newline='') as csvfile:  # Open file in write mode to clear it
                writer = csv.DictWriter(csvfile, fieldnames=data[0].keys())
                writer.writeheader()  # Write headers
                writer.writerows(data)  # Write data rows
        except Exception as e:
            logging.error(f'Error in save_to_csv: {e}')
            
    def save_failed_config(self, failed_config):
        try:
            config = self.read_from_json("failed_config.json")
            config.append(failed_config)
            self.write_to_json(config, "failed_config.json")
        except Exception as e:
            logging.error(f'Error in save_failed_config: {e}')
            
    # clear failed config
    def clear_failed_config(self):
        try:
            self.write_to_json([], "failed_config.json")
        except Exception as e:
            logging.error(f'Error in clear_failed_config: {e}')
