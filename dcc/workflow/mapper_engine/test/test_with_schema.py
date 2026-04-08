"""
Test with actual schema aliases
"""
import json
import re
import difflib

def normalize_string(text: str) -> str:
    """Normalize string for comparison."""
    normalized = text.lower().strip()
    prefixes = ['the ', 'a ', 'an ']
    for prefix in prefixes:
        if normalized.startswith(prefix):
            normalized = normalized[len(prefix):]
    normalized = re.sub(r'[^\w\s]', '', normalized)
    normalized = re.sub(r'\s+', ' ', normalized)
    return normalized.strip()

def fuzzy_match_column(header: str, target_columns, threshold: float = 0.6):
    """Perform fuzzy matching."""
    header_clean = normalize_string(header)
    best_match = ""
    best_score = 0.0
    
    for target in target_columns:
        target_clean = normalize_string(target)
        if header_clean == target_clean:
            return target, 1.0
        score = difflib.SequenceMatcher(None, header_clean, target_clean).ratio()
        if score > best_score and score >= threshold:
            best_match = target
            best_score = score
    
    return best_match, best_score

# Load actual schema aliases
with open('/workspaces/Engineering-and-Design/dcc/config/schemas/dcc_register_enhanced.json', 'r') as f:
    schema = json.load(f)

aliases = schema['enhanced_schema']['columns']['Review_Return_Plan_Date']['aliases']

# Test headers
test_headers = [
    "Date S.O. to Response\n(20 Working Days/\n 14 Working Days)",
    "Date S.O. to Response (20 Working Days/ 14 Working Days)",
    "review return_plan_date",
    "Review return_plan_date",
    "Return Plan Date",
    "Review Return Plan Date",
]

print("Testing with ACTUAL schema aliases:")
print("=" * 80)
print(f"Total aliases in schema: {len(aliases)}\n")

for header in test_headers:
    print(f"Header: {repr(header)}")
    print(f"  Normalized: '{normalize_string(header)}'")
    
    match, score = fuzzy_match_column(header, aliases, threshold=0.6)
    if score >= 0.6:
        print(f"  ✓ Matched: '{match}' (score: {score:.3f})")
    else:
        print(f"  ✗ NOT MATCHED (best score: {score:.3f})")
    print()
