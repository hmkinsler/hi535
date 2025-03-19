import re
import os
import pandas as pd

# Function to parse a single directory file
def parse_directory(file_path, output_path):
    # Read the file
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    # Initialize a list to store parsed data
    parsed_data = []
    
    # Updated regex for parsing
    regex = re.compile(r"^(\d+)\s+([^\d\(]+)\s*(\([a-zA-Z]\))?\s*(.*)$")
    
    for line in lines:
        # Match the line with the regex
        match = regex.match(line.strip())
        if match:
            # Extract fields from regex groups
            address = match.group(1)  # House number
            full_name = match.group(2).strip()  # Full name or business name
            tag = match.group(3) if match.group(3) else ""  # (c) or other tags
            additional_info = match.group(4).strip() if match.group(4) else ""  # Additional info
            
            # Split the full name into last and first names
            name_parts = full_name.split()
            last_name = name_parts[0] if len(name_parts) > 0 else ""
            first_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""
            
            # Append the parsed data
            parsed_data.append({
                "Address": address,
                "Last Name": last_name,
                "First Name": first_name,
                "(c)": "Yes" if "(c)" in tag else "No",
                "Additional Info": additional_info
            })
    
    # Convert the parsed data to a DataFrame
    df = pd.DataFrame(parsed_data)
    
    # Save the DataFrame to a CSV file
    df.to_csv(output_path, index=False)
    print(f"Data successfully saved to {output_path}")

# Function to process all files in a folder
def process_folder(input_folder, output_folder):
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)
    
    # Loop through all .txt files in the input folder
    for filename in os.listdir(input_folder):
        if filename.endswith(".txt"):
            # Define file paths
            input_file_path = os.path.join(input_folder, filename)
            output_file_name = os.path.splitext(filename)[0] + ".csv"  # Replace .txt with .csv
            output_file_path = os.path.join(output_folder, output_file_name)
            
            # Parse the file and save the output
            parse_directory(input_file_path, output_file_path)

# Folder paths
input_folder = r"C:\Users\hacks\Documents\vscodeprojects\fourth_ward_directories\directory_txt"  # Replace with your input folder path
output_folder = r"C:\Users\hacks\Documents\vscodeprojects\fourth_ward_directories\csv_output"  # Replace with your output folder path

# Call the folder processing function
process_folder(input_folder, output_folder)
