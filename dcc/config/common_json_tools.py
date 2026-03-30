import json
from pathlib import Path
import pandas as pd


def find_schema_dir(start_path: Path):
    start = start_path.resolve()
    for base in [start, *start.parents]:
        candidates = [
            base / 'dcc' / 'config' / 'schemas',
            base / 'config' / 'schemas',
            base / 'schemas',
        ]
        for candidate in candidates:
            if candidate.exists() and candidate.is_dir():
                return candidate
    return None


def to_schema_table(data):
    schema_dict = data.get('schema', {}) if isinstance(data, dict) else {}
    rows = [
        {'standard_name': standard_name, 'source_name': source_name}
        for standard_name, source_names in schema_dict.items()
        for source_name in source_names
    ]
    return pd.DataFrame(rows)


def to_parameters_table(data):
    parameters_dict = data.get('parameters', {}) if isinstance(data, dict) else {}
    rows = [{'parameter': k, 'value': v} for k, v in parameters_dict.items()]
    return pd.DataFrame(rows)


def to_row_mapping_table(data):
    row_mapping_dict = data.get('row_mapping', {}) if isinstance(data, dict) else {}
    rows = [
        {'approval_code': approval_code, 'alias': alias}
        for approval_code, aliases in row_mapping_dict.items()
        for alias in aliases
    ]
    return pd.DataFrame(rows)


def to_top_level_table(data):
    if not isinstance(data, dict):
        return pd.DataFrame([{'type': str(type(data)), 'value': data}])

    rows = []
    for key, value in data.items():
        if isinstance(value, dict):
            value_type = 'dict'
            size = len(value)
        elif isinstance(value, list):
            value_type = 'list'
            size = len(value)
        else:
            value_type = type(value).__name__
            size = None
        rows.append({'key': key, 'type': value_type, 'size': size, 'preview': str(value)[:120]})

    return pd.DataFrame(rows)


if __name__ == '__main__':
    schema_dir = find_schema_dir(Path.cwd())
    if schema_dir is None:
        raise FileNotFoundError(f'No JSON schema files found in dcc/config/schemas from cwd {Path.cwd()} (searched parent paths)')

    json_files = sorted(schema_dir.glob('*.json'))
    if not json_files:
        raise FileNotFoundError(f'No JSON schema files found in {schema_dir}')

    print('Resolved schema directory:', schema_dir)
    print('Available JSON schema files:')
    for i, fpath in enumerate(json_files, start=1):
        print(f'{i:>2}. {fpath.name}')

    selection = input('Enter the index or file name to inspect (default 1): ').strip() or '1'
    if selection.isdigit():
        idx = int(selection) - 1
        if idx < 0 or idx >= len(json_files):
            raise IndexError('Selection index out of range')
        selected_path = json_files[idx]
    else:
        selected_path = schema_dir / selection
        if not selected_path.exists():
            raise FileNotFoundError(f'File not found: {selected_path}')

    print(f'\nLoading JSON file: {selected_path}')
    with selected_path.open('r', encoding='utf-8') as f:
        json_data = json.load(f)

    print('\nTop-level keys:')
    if isinstance(json_data, dict):
        print(list(json_data.keys()))
    else:
        print(type(json_data))

    top_level_table = to_top_level_table(json_data)
    schema_table = to_schema_table(json_data)
    parameters_table = to_parameters_table(json_data)
    row_mapping_table = to_row_mapping_table(json_data)

    print('\nTop-Level Summary')
    print(top_level_table.to_string(index=False))

    if isinstance(json_data, dict):
        if 'choices' in json_data:
            print('\nChoices Table')
            print(pd.DataFrame({'choice': json_data['choices']}).to_string(index=False))

        if 'document_types' in json_data:
            print('\nDocument Types Table')
            print(pd.DataFrame(json_data['document_types']).T.to_string())

        if 'tools' in json_data:
            print('\nTools Table')
            print(pd.DataFrame(json_data['tools']).T.to_string())

        if 'workflows' in json_data:
            print('\nWorkflows Table')
            print(pd.DataFrame(json_data['workflows']).T.to_string())

        if 'mappings' in json_data and isinstance(json_data['mappings'], dict):
            print('\nMapping rows (one per key/value item):')
            mapping_rows = []
            for key, values in json_data['mappings'].items():
                if isinstance(values, list):
                    for value in values:
                        mapping_rows.append({'key': key, 'mapped_value': value})
                else:
                    mapping_rows.append({'key': key, 'mapped_value': values})
            print(pd.DataFrame(mapping_rows).to_string(index=False))

    print('\nSchema Table')
    print(schema_table.to_string(index=False))

    print('\nParameters Table')
    print(parameters_table.to_string(index=False))

    print('\nRow Mapping Table')
    print(row_mapping_table.to_string(index=False))
