#!/usr/bin/env python3
"""
End-to-end test of column mapping with actual Excel file
"""
import pandas as pd
import json
import sys
sys.path.insert(0, '/workspaces/Engineering-and-Design/dcc/workflow/mapper_engine/engine')

from matchers.fuzzy import fuzzy_match_column, normalize_string

# Load Excel data
print("Loading Excel file...")
df = pd.read_excel(
    '/workspaces/Engineering-and-Design/dcc/data/Submittal and RFI Tracker Lists.xlsx',
    sheet_name="Prolog Submittals ",
    header=4,
    usecols="P:AP"
)

print(f"Loaded {len(df)} rows × {len(df.columns)} columns\n")

# Load schema
with open('/workspaces/Engineering-and-Design/dcc/config/schemas/dcc_register_enhanced.json', 'r') as f:
    schema = json.load(f)

columns = schema['enhanced_schema']['columns']

# Find the target column in Excel
print("=" * 80)
print("EXCEL HEADERS CONTAINING 'Response' or 'Date':")
print("=" * 80)

target_header = None
for i, header in enumerate(df.columns, 1):
    header_str = str(header)
    if 'Date S.O. to Response' in header_str:
        target_header = header
        print(f"\n{i}. {repr(header)}")
        print(f"   Type: {type(header)}")
        print(f"   Contains \\n: {'\\n' in header_str}")
        print(f"   Normalized: '{normalize_string(header_str)}'")
        break

if not target_header:
    print("ERROR: Target header not found!")
    sys.exit(1)

# Get aliases
aliases = columns['Review_Return_Plan_Date']['aliases']
print(f"\nSchema has {len(aliases)} aliases for Review_Return_Plan_Date:")
for i, alias in enumerate(aliases, 1):
    print(f"  {i}. {repr(alias)}")
    print(f"     Normalized: '{normalize_string(alias)}'")

# Test matching
print("\n" + "=" * 80)
print("MATCHING TEST:")
print("=" * 80)

match, score = fuzzy_match_column(str(target_header), aliases, threshold=0.6)
print(f"\nExcel header: {repr(target_header)}")
print(f"Matched to: {repr(match)}")
print(f"Score: {score:.3f}")

if score >= 0.6:
    print("✅ SUCCESS - Column would be mapped!")
else:
    print("❌ FAILURE - Column would NOT be mapped!")
    
    # Show all scores
    print("\nAll alias scores:")
    header_clean = normalize_string(str(target_header))
    for i, alias in enumerate(aliases, 1):
        alias_clean = normalize_string(alias)
        from difflib import SequenceMatcher
        s = SequenceMatcher(None, header_clean, alias_clean).ratio()
        print(f"  {i}. {s:.3f} - {repr(alias)}")
