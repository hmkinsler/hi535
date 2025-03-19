import pandas as pd

def merge_directory_data(file_path, output_path):
    """
    Merges directory data by address and organizes details across years.

    Parameters:
    - file_path: Path to the input CSV file in tidy format.
    - output_path: Path to save the merged output CSV.

    Returns:
    - None: The merged file is saved to the specified path.
    """
    # Load the tidy data
    data = pd.read_csv(file_path)

    # Pivot the data to group by Address and show how details change across years
    merged_data = data.pivot_table(
        index='Address',
        columns='Year',
        values=['Last Name', 'First Name', '(c)', 'Additional Info'],
        aggfunc=lambda x: ' | '.join(x.dropna().astype(str))
    )

    # Flatten the multi-index columns for better readability
    merged_data.columns = [
        f"{col[0]}_{col[1]}" if col[1] else col[0] for col in merged_data.columns
    ]

    # Reset index to make Address a regular column
    merged_data.reset_index(inplace=True)

    # Reorganize columns to group by year
    years = sorted(set(data['Year'].dropna().astype(int)))  # Get all years
    organized_columns = ['Address']  # Start with the Address column

    for year in years:
        organized_columns.extend(
            [f"Last Name_{year}", f"First Name_{year}", f"(c)_{year}", f"Additional Info_{year}"]
        )

    # Reorder columns if they exist in the merged data
    merged_data = merged_data[[col for col in organized_columns if col in merged_data.columns]]

    # Save the merged data to the specified output path
    merged_data.to_csv(output_path, index=False)
    print(f"Merged data saved to {output_path}")

# Input and output file paths
input_file_path = r"C:\Users\hacks\Documents\vscodeprojects\fourth_ward_directories\cleaned_directory_data.csv"  # Replace with your cleaned data file path
output_file_path = r"C:\Users\hacks\Documents\vscodeprojects\fourth_ward_directories\path_to_sorted_data.csv"  # Replace with desired output file path

# Call the function
merge_directory_data(input_file_path, output_file_path)
