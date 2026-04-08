#!/usr/bin/env python3
import json

# Load the schema
with open('dcc_register_enhanced.json', 'r', encoding='utf-8') as f:
    schema = json.load(f)

# Get current aliases
col_def = schema['enhanced_schema']['columns']['Review_Return_Plan_Date']
print(f"Current aliases ({len(col_def['aliases'])}):")
for i, alias in enumerate(col_def['aliases'], 1):
    print(f"  {i}. {repr(alias)}")

# Add the Excel header exactly as it appears
excel_header = "Date S.O. to Response\n(20 Working Days/\n 14 Working Days)"

# Check if it's already there
if excel_header not in col_def['aliases']:
    # Add it at the beginning for priority
    col_def['aliases'].insert(0, excel_header)
    print(f"\n✅ Added Excel header with actual newlines")
else:
    print(f"\n⚠️  Excel header already exists")

print(f"\nTotal aliases now: {len(col_def['aliases'])}")

# Write back with proper formatting
with open('dcc_register_enhanced.json', 'w', encoding='utf-8') as f:
    json.dump(schema, f, indent=2, ensure_ascii=False)

print("✅ Schema file saved successfully")

# Verify
with open('dcc_register_enhanced.json', 'r', encoding='utf-8') as f:
    schema2 = json.load(f)
    
aliases2 = schema2['enhanced_schema']['columns']['Review_Return_Plan_Date']['aliases']
print(f"\nVerification - aliases count: {len(aliases2)}")
print("First 3 aliases:")
for i in range(min(3, len(aliases2))):
    print(f"  {i+1}. {repr(aliases2[i])}")
