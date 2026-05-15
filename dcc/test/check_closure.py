import pandas as pd
import json

# Read the processed output
df = pd.read_csv('output/processed_dcc_universal.csv', nrows=100)

print("Columns available:", [c for c in df.columns if 'Closed' in c or 'Plan' in c or 'Latest' in c or 'Submission' in c or 'Revision' in c])
print()

# Check rows 3, 5, 8 which still report L3-L-V-0302
for row_idx in [3, 5, 8, 17]:
    r = df.iloc[row_idx]
    print(f"Row {row_idx}:")
    print(f"  Submission_Closed={r.get('Submission_Closed', 'N/A')}")
    print(f"  Resubmission_Plan_Date={r.get('Resubmission_Plan_Date', 'N/A')}")
    print(f"  Submission_Date={r.get('Submission_Date', 'N/A')}")
    print(f"  Latest_Submission_Date={r.get('Latest_Submission_Date', 'N/A')}")
    print(f"  Document_ID={r.get('Document_ID', 'N/A')}")
    is_latest = True
    if 'Latest_Submission_Date' in df.columns and 'Submission_Date' in df.columns:
        try:
            sub = pd.to_datetime(r['Submission_Date'])
            latest = pd.to_datetime(r['Latest_Submission_Date'])
            is_latest = sub >= latest
        except:
            pass
    print(f"  Is latest revision? {is_latest}")
    print()
