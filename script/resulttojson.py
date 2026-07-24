import json
import re
import os
from paddleocr import PaddleOCR

def extract_information(image_path):
    print(f"Running OCR on {image_path}...")
    # Initialize PaddleOCR
    ocr = PaddleOCR(use_angle_cls=True, lang='en', show_log=False)
    
    # Run OCR
    result = ocr.ocr(image_path, cls=True)
    if not result or not result[0]:
        print("No text found.")
        return {}
    
    boxes = result[0]
    
    # Data to extract
    extracted_data = {
        "Student Name": "",
        "Reg. No.": "",
        "Semester": "",
        "Gender": "",
        "Program": "",
        "Credit Registered": "",
        "Credit Completed": "",
        "Results": []
    }
    
    table_items = []
    
    for box in boxes:
        coords, (text, confidence) = box
        text = text.strip()
        
        # Extract top-level fields
        if text.startswith("Student Name:"):
            extracted_data["Student Name"] = text.replace("Student Name:", "").strip()
        elif text.startswith("Reg. No.:"):
            extracted_data["Reg. No."] = text.replace("Reg. No.:", "").strip()
        elif text.startswith("Semester:") and len(text) < 20: # To avoid matching column header if it somehow merges
            extracted_data["Semester"] = text.replace("Semester:", "").strip()
        elif text.startswith("Gender:"):
            extracted_data["Gender"] = text.replace("Gender:", "").strip()
        elif text.startswith("Program:"):
            extracted_data["Program"] = text.replace("Program:", "").strip()
        elif text.startswith("Credit Registered"):
            match = re.search(r'\d+', text)
            if match:
                extracted_data["Credit Registered"] = match.group()
        elif text.startswith("Credit Completed"):
            match = re.search(r'\d+', text)
            if match:
                extracted_data["Credit Completed"] = match.group()
        else:
            # Save for table parsing
            x_center = sum([p[0] for p in coords]) / 4
            y_center = sum([p[1] for p in coords]) / 4
            if y_center < 1900:
                table_items.append({
                    "text": text,
                    "x": x_center,
                    "y": y_center
                })

    # Group table items by Y coordinate to form rows
    table_items.sort(key=lambda item: item['y'])
    
    rows = []
    current_row = []
    current_y = None
    
    for item in table_items:
        if current_y is None:
            current_y = item['y']
            current_row.append(item)
        elif abs(item['y'] - current_y) < 30: # 30 pixels threshold
            current_row.append(item)
            current_y = sum(i['y'] for i in current_row) / len(current_row)
        else:
            rows.append(current_row)
            current_row = [item]
            current_y = item['y']
            
    if current_row:
        rows.append(current_row)
        
    parsed_results = []
    
    for row in rows:
        row_data = {
            "Semester": "",
            "Course Name": "",
            "Grade point": "",
            "Grade": "",
            "Credit": "",
            "Result status": ""
        }
        is_valid_row = False
        
        for item in row:
            text = item['text']
            x = item['x']
            
            if x < 300:
                if text == "EVEN" or text == "ODD":
                    row_data["Semester"] = text
                    is_valid_row = True
            elif 300 <= x < 1000:
                # Add a space if there's already text
                if row_data["Course Name"]:
                    row_data["Course Name"] += " " + text
                else:
                    row_data["Course Name"] = text
            elif 1000 <= x < 1200:
                if re.match(r'^\d+$', text):
                    row_data["Grade point"] = text
            elif 1200 <= x < 1400:
                if len(text) <= 2: 
                    row_data["Grade"] = text
            elif 1400 <= x < 1550:
                if re.match(r'^\d+$', text):
                    row_data["Credit"] = text
            elif x >= 1550:
                if "Pass" in text or "Fail" in text:
                    row_data["Result status"] = text
                    
        # If the row has "EVEN" or "ODD", it's a new result row
        if is_valid_row:
            parsed_results.append(row_data)
        else:
            # Check if this row is a continuation of the previous course name
            if len(parsed_results) > 0:
                for item in row:
                    if 300 <= item['x'] < 1000:
                        parsed_results[-1]["Course Name"] += " " + item['text'].strip()
                        
    extracted_data["Results"] = parsed_results
    return extracted_data

if __name__ == "__main__":
    image_file = r"C:\download\clg_credit_tracker\page_0.png"
    if not os.path.exists(image_file):
        print(f"Error: {image_file} not found.")
    else:
        data = extract_information(image_file)
        out_file = r"C:\download\clg_credit_tracker\result.json"
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"Extraction complete. Saved to {out_file}.")