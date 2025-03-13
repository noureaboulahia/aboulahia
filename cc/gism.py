import os
import json
import pandas as pd

def process_text_to_json(text):
    rows = text.split("=")
    data = {}
    
    for row in rows:
        row = row.strip()
        if not row:
            continue
        
        columns = row.split("+")
        while len(columns) < 3:
            columns.append("")
        
        third_column_parts = columns[2].split("&")
        col1, col2 = columns[0], columns[1]
        
        if col1 not in data:
            data[col1] = {}
        if col2 not in data[col1]:
            data[col1][col2] = []
        
        for part in third_column_parts:
            sub_parts = part.split("ببب", 1)
            if len(sub_parts) == 1:
                sub_parts.append("")
            
            data[col1][col2].append({"part": sub_parts[0].strip(), "detail": sub_parts[1].strip()})
    
    return data

def process_files():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    final_data = {}
    
    for filename in os.listdir(script_dir):
        file_path = os.path.join(script_dir, filename)
        
        if filename.endswith(".txt"):
            with open(file_path, "r", encoding="utf-8") as file:
                text = file.read().strip()
            
            if not text:
                print(f"{filename} فارغ، تم تخطيه.")
                continue
            
            file_data = process_text_to_json(text)
            for key, value in file_data.items():
                if key not in final_data:
                    final_data[key] = value
                else:
                    for sub_key, sub_value in value.items():
                        if sub_key not in final_data[key]:
                            final_data[key][sub_key] = sub_value
                        else:
                            final_data[key][sub_key].extend(sub_value)
    
    json_filename = os.path.join(script_dir, "data.json")
    with open(json_filename, "w", encoding="utf-8") as json_file:
        json.dump(final_data, json_file, ensure_ascii=False, indent=4)
    
    print("تم إنشاء data.json بنجاح!")

if __name__ == "__main__":
    process_files()
    print("تمت معالجة جميع الملفات!")
