import pdfplumber
import json
import os

def extract_curriculum_to_json(pdf_filename, output_json):
    """
    Extracts tabular curriculum data from the specified PDF and saves it as a JSON file.
    """
    if not os.path.exists(pdf_filename):
        print(f"Error: The file '{pdf_filename}' was not found in the current directory.")
        return

    curriculum_data = []
    
    # Define the headers based on the R2024-Curriculum-AIDS table structure
    headers = [
        "S.No", "Remarks", "Category", "Course Code R2024", 
        "Course Code R2019", "Course Title", "Prerequisite", 
        "Theory Credits", "Practical Credits", "Total Credits", 
        "CGPA/Non-CGPA", "Course Type"
    ]

    print(f"Opening {pdf_filename} for extraction...")
    
    with pdfplumber.open(pdf_filename) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            # Extract tables from the current page
            tables = page.extract_tables()
            
            for table in tables:
                for row in table:
                    # Skip empty rows or header rows that repeat "S.No"
                    if not row or row[0] == "S.No" or row[0] is None:
                        continue
                    
                    # Clean and map the row data to the respective headers
                    row_data = {}
                    for i, header in enumerate(headers):
                        # Handle potential missing columns and clean up newline characters from the PDF
                        if i < len(row) and row[i] is not None:
                            cleaned_value = str(row[i]).replace('\n', ' ').strip()
                        else:
                            cleaned_value = ""
                            
                        row_data[header] = cleaned_value
                    
                    # Only append rows that have an actual serial number to filter out noise
                    if row_data["S.No"].isdigit():
                        curriculum_data.append(row_data)

    # Write the extracted list of dictionaries to a JSON file
    with open(output_json, 'w', encoding='utf-8') as json_file:
        json.dump(curriculum_data, json_file, indent=4, ensure_ascii=False)
    
    print(f"Extraction complete! Successfully saved {len(curriculum_data)} courses to '{output_json}'.")

# Execute the function referencing the provided document
if __name__ == "__main__":
    target_file = "C:\download\clg_credit_tracker\dataset\R2024-Curriculum-AIDS.pdf"
    output_file = "R2024_Curriculum_Extracted.json"
    
    extract_curriculum_to_json(target_file, output_file)