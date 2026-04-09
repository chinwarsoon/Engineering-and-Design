
import json
from pathlib import Path
import pandas as pd

def print_or_display(obj):
    # When running in a non-interactive terminal, just print
    print(obj)

# Locate schema JSON files
def find_schema_dir(start_path: Path):
    start = start_path.resolve()
    for base in [start, *start.parents]:
        candidate = base / 'dcc' / 'config' / 'schemas'
        if candidate.exists() and candidate.is_dir():
            return candidate
    return None

def main():
    schema_dir = find_schema_dir(Path.cwd())
    if not schema_dir:
        print("Could not find the 'schemas' directory.")
        return

    # Hardcode the selection for this demonstration
    selected_path = schema_dir / 'dcc_register_enhanced.json'

    print(f'Loading JSON file: {selected_path}\n')
    try:
        with selected_path.open('r', encoding='utf-8') as f:
            json_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: The file {selected_path} was not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {selected_path}.")
        return


    # --- Table generation functions ---
    def to_top_level_table(data):
        if not isinstance(data, dict):
            return pd.DataFrame([{'type': str(type(data)), 'value': data}])
        rows = []
        for key, value in data.items():
            value_type = type(value).__name__
            size = len(value) if hasattr(value, '__len__') else None
            preview = str(value)
            if len(preview) > 100:
                preview = preview[:100] + '...'
            rows.append({'key': key, 'type': value_type, 'size': size, 'preview': preview})
        return pd.DataFrame(rows)

    def display_nested_properties(data):
        if not isinstance(data, dict):
            return
        print("\n--- Detailed Object Properties ---")
        found_table = False
        for key, value in data.items():
            if isinstance(value, dict) and value and all(isinstance(v, dict) for v in value.values()):
                found_table = True
                print(f"\nProperties for top-level key '{key}':")
                try:
                    df = pd.DataFrame.from_dict(value, orient='index')
                    with pd.option_context('display.max_rows', None, 'display.max_columns', None, 'display.width', 1000):
                        print_or_display(df)
                except Exception as e:
                    print(f"Could not create a table for '{key}': {e}")
        if not found_table:
            print("No top-level keys containing a dictionary of objects were found to tabulate.")

    # --- Main Execution ---
    print('\nTop-Level Summary')
    print_or_display(to_top_level_table(json_data))
    display_nested_properties(json_data)

if __name__ == '__main__':
    main()

