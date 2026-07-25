import pdfplumber
import pandas as pd
import argparse
import json
import os

def extract_course_info(pdf_path):
    extracted_data = []
    
    if not os.path.exists(pdf_path):
        print(f"Error: File '{pdf_path}' not found.")
        return []

    print(f"Processing '{pdf_path}'...")
    
    with pdfplumber.open(pdf_path) as pdf:
        end_idx = min(1327, len(pdf.pages))
        pages_to_process = pdf.pages[399:end_idx]
        total_pages = len(pages_to_process)
        
        for idx, page in enumerate(pages_to_process):
            page_num = 399 + idx
            print(f"\n--- Processing page {idx + 1}/{total_pages} (Actual PDF Page {page_num + 1}) ---")
            tables = page.extract_tables()
            for table in tables:
                if not table:
                    continue
                
                header_idx = -1
                for i, row in enumerate(table):
                    row_str = " ".join([str(cell).lower().replace('\n', ' ') for cell in row if cell])
                    if 'register' in row_str and 'name' in row_str and 'course' in row_str:
                        header_idx = i
                        break
                
                if header_idx != -1 and len(table) > header_idx + 1:
                    headers = [str(col).replace('\n', ' ').strip() if col else f"Col_{j}" for j, col in enumerate(table[header_idx])]
                    df = pd.DataFrame(table[header_idx+1:], columns=headers)
                    
                    col_map = {}
                    for col in df.columns:
                        col_lower = col.lower().strip()
                        if 'register number' in col_lower or 'register no' in col_lower or ('register' in col_lower and 'number' in col_lower):
                            col_map['Register Number'] = col
                        elif 'course name' in col_lower:
                            col_map['Course Name'] = col
                        elif 'student name' in col_lower or 'name' in col_lower:
                            col_map['Name'] = col
                        elif 'dept' in col_lower or 'department' in col_lower:
                            col_map['Dept'] = col
                        elif '24 code' in col_lower:
                            col_map['24 Code'] = col
                        elif '19 code' in col_lower:
                            col_map['19 CODE'] = col
                        elif 'category' in col_lower:
                            col_map['Category'] = col
                        elif 'credits' in col_lower or 'credit' in col_lower:
                            col_map['credits'] = col
                        elif 'status' in col_lower:
                            col_map['Status'] = col

                    required_cols = ['Register Number', 'Name', 'Course Name', 'Status']
                    has_required = all(c in col_map for c in required_cols)
                    
                    if has_required:
                        last_reg, last_name, last_dept = '', '', ''
                        for _, row in df.iterrows():
                            reg = str(row.get(col_map['Register Number'], '')).replace('\n', ' ').strip()
                            name = str(row.get(col_map['Name'], '')).replace('\n', ' ').strip()
                            dept = str(row.get(col_map.get('Dept', ''), '')).replace('\n', ' ').strip() if 'Dept' in col_map else ''
                            
                            if reg and reg.lower() not in ['none', 'nan', '', 'register number', 'register no']:
                                last_reg = reg
                                if name and name.lower() not in ['none', 'nan', '']: last_name = name
                                if dept and dept.lower() not in ['none', 'nan', '']: last_dept = dept
                            else:
                                reg = last_reg
                                name = last_name
                                dept = last_dept
                                
                            if not reg:
                                continue
                                
                            cname = str(row.get(col_map['Course Name'], '')).replace('\n', ' ').strip()
                            if not cname or cname.lower() in ['none', 'nan', '']:
                                continue
                                
                            c24 = str(row.get(col_map.get('24 Code', ''), '')).replace('\n', ' ').strip() if '24 Code' in col_map else ''
                            c19 = str(row.get(col_map.get('19 CODE', ''), '')).replace('\n', ' ').strip() if '19 CODE' in col_map else ''
                            category = str(row.get(col_map.get('Category', ''), '')).replace('\n', ' ').strip() if 'Category' in col_map else ''
                            credits_val = str(row.get(col_map.get('credits', ''), '')).replace('\n', ' ').strip() if 'credits' in col_map else ''
                            status = str(row.get(col_map.get('Status', ''), '')).replace('\n', ' ').strip()
                            
                            record = {
                                'Register Number': reg,
                                'Name': name,
                                'Dept': dept,
                                '24 Code': c24,
                                '19 CODE': c19,
                                'Course Name': cname,
                                'Category': category,
                                'credits': credits_val,
                                'Status': status
                            }
                            extracted_data.append(record)

    return extracted_data

if __name__ == '__main__':
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    default_pdf = os.path.join(base_dir, 'dataset', 'curriculum', 'Category-wise Credit Completion Summary for I, II & III Year(8.5.26).pdf')
    default_out = os.path.join(base_dir, 'data', 'students', 'student_courses_extracted.json')

    parser = argparse.ArgumentParser(description='Extract student course info from PDF.')
    parser.add_argument('pdf_path', type=str, nargs='?', help='Path to the input PDF file', default=default_pdf)
    parser.add_argument('--output', type=str, help='Path to output JSON file', default=default_out)
    args = parser.parse_args()
    
    data = extract_course_info(args.pdf_path)
    
    if data:
        os.makedirs(os.path.dirname(args.output), exist_ok=True)
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        print(f"Data saved to '{args.output}'")
