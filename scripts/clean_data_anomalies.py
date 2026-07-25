import json
import os
import re

FIX_MAP = {
    '212225040382 SA': ('212225040382', 'SANTHOSH VIRUPATCHIPURAM SIVAKUMA'),
    '212225230041 DEE': ('212225230041', 'DEEKSHA VICTOR SELVAKUMAR SINDHUPR'),
    '212224240013A': ('212224240013', 'ARANI VENKATA SUNDARA LEELA KRISHN'),
    '212224060154M': ('212224060154', 'MOHAMED THOUFIQ THANEES AHAMED'),
    '212224060226S': ('212224060226', 'SAI RAGAVA ANAND SURESH SAMBASIVA'),
    '21222422011T7HI': ('212224220117', 'THIRUNAVUKKARASU MEENAKSHISUNDAR'),
}

def clean_anomalies():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    
    # Check input file path
    input_paths = [
        os.path.join(base_dir, "data", "students", "student_courses_extracted.json"),
        os.path.join(base_dir, "student_courses_extracted.json")
    ]
    
    input_path = next((p for p in input_paths if os.path.exists(p)), None)
    if not input_path:
        print("Error: student_courses_extracted.json not found.")
        return

    print(f"Reading student dataset from: {input_path}")
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    cleaned_data = []
    student_course_map = {}
    fixed_reg_count = 0
    fixed_name_count = 0
    duplicate_merged = 0

    for row in data:
        reg = str(row.get('Register Number', '')).strip()
        name = str(row.get('Name', '')).strip()
        cname = str(row.get('Course Name', '')).strip()
        status = str(row.get('Status', '')).strip()

        # Apply register number & name fix
        if reg in FIX_MAP:
            new_reg, new_name = FIX_MAP[reg]
            if reg != new_reg: fixed_reg_count += 1
            if name != new_name: fixed_name_count += 1
            reg, name = new_reg, new_name
            row['Register Number'] = reg
            row['Name'] = name

        # Deduplicate student course entries
        key = (reg, cname)
        if key in student_course_map:
            existing_idx = student_course_map[key]
            existing_row = cleaned_data[existing_idx]
            duplicate_merged += 1
            # Prefer Pass / Completed over Enrolled
            if status.lower() in ['pass', 'completed'] and existing_row.get('Status', '').lower() not in ['pass', 'completed']:
                cleaned_data[existing_idx]['Status'] = status
        else:
            student_course_map[key] = len(cleaned_data)
            cleaned_data.append(row)

    print("\n--- Data Anomaly Resolution Summary ---")
    print(f"Total input rows: {len(data)}")
    print(f"Fixed malformed Register Numbers: {fixed_reg_count} rows")
    print(f"Fixed split/truncated Student Names: {fixed_name_count} rows")
    print(f"Merged duplicate course entries: {duplicate_merged} rows")
    print(f"Cleaned output rows: {len(cleaned_data)}")

    # Ensure output directories exist
    out_dir = os.path.join(base_dir, "data", "students")
    os.makedirs(out_dir, exist_ok=True)
    
    out_file = os.path.join(out_dir, "student_courses_extracted.json")
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(cleaned_data, f, indent=2)
    print(f"Cleaned dataset saved to: {out_file}")

    # Also sync root copy if present
    root_file = os.path.join(base_dir, "student_courses_extracted.json")
    with open(root_file, 'w', encoding='utf-8') as f:
        json.dump(cleaned_data, f, indent=2)
    print(f"Updated root dataset: {root_file}")

if __name__ == '__main__':
    clean_anomalies()
