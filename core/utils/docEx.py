import pandas as pd
import os

# Load the Excel file
file_path = "utils\Sources.xlsx"  # Replace with your file path
df = pd.read_excel(file_path)

# Ensure the output directory exists
output_dir = "output_text_files"
os.makedirs(output_dir, exist_ok=True)

# Process each row and create a text file
for index, row in df.iterrows():
    article_no = row["No."]  # No column for numbering
    article = row["Article"]  # Article number
    keywords = row["Subdomain"]  # Related keywords or topics
    description = row["Item"]  # Description
    
    # Create the text content
    content = f"Article No: {article}\n\nRelated keywords or topics:\n{keywords}\n\nDescription:\n{description}"
    
    # Define the file name using both Article and No
    file_name = f"Article_{article}_No_{article_no}.txt"
    file_path = os.path.join(output_dir, file_name)
    
    # Write to the text file
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(content)

print(f"Text files have been generated in the '{output_dir}' directory.")
