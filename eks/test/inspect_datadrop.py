import pandas as pd
import json

file_path = r'eks/data/twrp/datadrop/Datadrop Summary.xlsx'
try:
    xl = pd.ExcelFile(file_path)
    summary = {}
    for sheet_name in xl.sheet_names:
        df = xl.parse(sheet_name, nrows=5)
        summary[sheet_name] = list(df.columns)
    
    print(json.dumps(summary, indent=2))
except Exception as e:
    print(f"Error: {e}")
