"""
Validation module for schema-based data validation.
Extracted from UniversalDocumentProcessor validation methods.
"""

import pandas as pd
import numpy as np
import logging
import re
from typing import Dict, Any, List, Optional, Any as TypingAny

logger = logging.getLogger(__name__)

# Error codes mapping based on error_handling/config/error_codes.json
ERROR_CODES = {
    'required': 'P-V-V-0505',
    'allow_null': 'P-V-V-0505',
    'pattern': 'P-V-V-0501',
    'min_length': 'P-V-V-0501',
    'max_length': 'P-V-V-0502',
    'min_value': 'P-V-V-0501',
    'max_value': 'P-V-V-0501',
    'format': 'P-V-V-0504',
    'allowed_values': 'P-V-V-0503',
    'schema_reference_check': 'P-V-V-0506',
    'starts_with_schema_reference': 'P-V-V-0501',
    'derived_pattern': 'P-V-V-0501',
    'group_consistency': 'P-V-V-0501',
}


def collect_raw_pattern_errors(df: pd.DataFrame, columns_schema: dict) -> pd.Series:
    """
    Validate raw input data against schema pattern rules BEFORE any transformations.

    Returns a Series of error strings indexed by DataFrame row index, for rows
    where pattern validation fails. Empty string for rows that pass.
    """
    error_msgs = pd.Series("", index=df.index)

    for column_name, column_def in columns_schema.items():
        if not isinstance(column_def, dict):
            continue
        if column_name not in df.columns:
            continue

        allow_null = column_def.get('allow_null', True)
        validation_rules = _normalize_validation_rules(column_def.get('validation', {}))

        for validation in validation_rules:
            rule_type = validation.get('type')

            if rule_type == 'pattern':
                pattern = validation['pattern']
                # Handle duplicate columns - take first occurrence
                col_data = df[column_name]
                if hasattr(col_data, 'columns'):  # DataFrame (duplicates)
                    col_data = col_data.iloc[:, 0]
                df_str = col_data.astype(str)
                mask = ~df_str.str.match(pattern)
                if allow_null:
                    mask &= col_data.notna()
                if mask.any():
                    bad_values = col_data.loc[mask].dropna().head(5).tolist()
                    code = ERROR_CODES.get('pattern', 'P-V-V-0501')
                    msg = f"[{code}] {column_name} raw input pattern mismatch ({pattern}): {bad_values}"
                    logger.warning(
                        f"Raw input pattern validation failed for {column_name}: "
                        f"{mask.sum()}/{len(df)} values don't match {pattern}. "
                        f"Sample: {bad_values[:5]}"
                    )
                    error_msgs[mask] = error_msgs[mask].apply(
                        lambda x: f"{msg}".strip("; ") if not x else f"{x}; {msg}".strip("; ")
                    )

    return error_msgs


def apply_validation(df: pd.DataFrame, columns_schema: dict, schema_data: dict,
                     raw_errors: pd.Series = None) -> pd.DataFrame:
    """
    Apply validation rules from schema and record errors per-row.

    Args:
        df: Input DataFrame
        columns_schema: Column definitions from schema
        schema_data: Full schema data for reference lookups
        raw_errors: Pre-existing raw input validation errors

    Returns:
        DataFrame with validation applied and Validation_Errors column populated
    """
    df_validated = df.copy()

    # Initialize Validation_Errors column if it exists in schema
    error_col = "Validation_Errors"
    if error_col in columns_schema:
        df_validated[error_col] = ""

    def record_errors(mask, message, code=None):
        error_msg = f"[{code}] {message}" if code else message
        if error_col in df_validated.columns and mask.any():
            df_validated.loc[mask, error_col] = df_validated.loc[mask, error_col].apply(
                lambda x: f"{x}; {error_msg}".strip("; ")
            )

    for column_name, column_def in columns_schema.items():
        if not isinstance(column_def, dict):
            continue
        is_required = column_def.get('required', False)
        if column_name not in df_validated.columns:
            if is_required:
                logger.error(f"Validation failed: Required column {column_name} is missing.")
            continue

        allow_null = column_def.get('allow_null', True)
        mask_null = df_validated[column_name].isna()
        if not allow_null and mask_null.any():
            code = ERROR_CODES.get('allow_null', 'P-V-V-0505')
            msg = f"{column_name} cannot be null"
            logger.warning(f"Validation failed: {msg} ({mask_null.sum()} found)")
            record_errors(mask_null, msg, code=code)

        validation_rules = _normalize_validation_rules(column_def.get('validation', {}))

        for validation in validation_rules:
            rule_type = validation.get('type')

            if rule_type == 'pattern' or ('pattern' in validation and rule_type is None):
                pattern = validation['pattern']
                df_str = df_validated[column_name].astype(str)
                mask = ~df_str.str.match(pattern)
                if allow_null:
                    mask &= df_validated[column_name].notna()
                if mask.any():
                    code = ERROR_CODES.get('pattern', 'P-V-V-0501')
                    msg = f"{column_name} pattern mismatch ({pattern})"
                    logger.warning(f"Pattern validation failed for {column_name}: {mask.sum()} invalid values")
                    record_errors(mask, msg, code=code)

            if rule_type == 'min_length' or ('min_length' in validation and rule_type is None):
                min_len = validation['min_length']
                df_str = df_validated[column_name].astype(str)
                mask = df_str.str.len() < min_len
                if allow_null:
                    mask &= df_validated[column_name].notna()
                if mask.any():
                    code = ERROR_CODES.get('min_length', 'P-V-V-0501')
                    msg = f"{column_name} too short (<{min_len})"
                    logger.warning(f"Min length validation failed for {column_name}: {mask.sum()} values too short")
                    record_errors(mask, msg, code=code)

            if rule_type == 'max_length' or ('max_length' in validation and rule_type is None):
                max_len = validation['max_length']
                mask = df_validated[column_name].astype(str).str.len() > max_len
                if allow_null:
                    mask &= df_validated[column_name].notna()
                if mask.any():
                    code = ERROR_CODES.get('max_length', 'P-V-V-0502')
                    msg = f"{column_name} too long (>{max_len})"
                    logger.warning(f"Max length validation failed for {column_name}: {mask.sum()} values too long")
                    record_errors(mask, msg, code=code)

            if rule_type == 'max_value' or ('max_value' in validation and rule_type is None):
                max_val = validation['max_value']
                mask = pd.to_numeric(df_validated[column_name], errors='coerce') > max_val
                if allow_null:
                    mask &= df_validated[column_name].notna()
                if mask.any():
                    code = ERROR_CODES.get('max_value', 'P-V-V-0501')
                    msg = f"{column_name} too high (>{max_val})"
                    logger.warning(f"Max value validation failed for {column_name}: {mask.sum()} numeric values > {max_val}")
                    record_errors(mask, msg, code=code)

            if rule_type == 'min_value' or ('min_value' in validation and rule_type is None):
                min_val = validation['min_value']
                mask = pd.to_numeric(df_validated[column_name], errors='coerce') < min_val
                if allow_null:
                    mask &= df_validated[column_name].notna()
                if mask.any():
                    code = ERROR_CODES.get('min_value', 'P-V-V-0501')
                    msg = f"{column_name} too low (<{min_val})"
                    logger.warning(f"Min value validation failed for {column_name}: {mask.sum()} numeric values < {min_val}")
                    record_errors(mask, msg, code=code)

            if (rule_type == 'format' or ('format' in validation and rule_type is None)) and validation.get('format') == 'YYYY-MM-DD':
                parsed = pd.to_datetime(df_validated[column_name], format="%Y-%m-%d", errors='coerce')
                mask = parsed.isna() & df_validated[column_name].notna() & (df_validated[column_name] != 'NA')
                if allow_null:
                    mask &= df_validated[column_name].notna()
                if mask.any():
                    code = ERROR_CODES.get('format', 'P-V-V-0504')
                    msg = f"{column_name} invalid date format (expected YYYY-MM-DD)"
                    logger.warning(f"Format validation (YYYY-MM-DD) failed for {column_name}: {mask.sum()} invalid dates")
                    record_errors(mask, msg, code=code)

            if rule_type == 'allowed_values' or ('allowed_values' in validation and rule_type is None):
                allowed = validation['allowed_values']
                mask = ~df_validated[column_name].isin(allowed)
                if allow_null:
                    mask &= df_validated[column_name].notna()
                if mask.any():
                    code = ERROR_CODES.get('allowed_values', 'P-V-V-0503')
                    msg = f"{column_name} value not allowed"
                    logger.warning(f"Allowed values validation failed for {column_name}: {mask.sum()} invalid values")
                    record_errors(mask, msg, code=code)

            if rule_type == 'group_consistency':
                group_cols = validation.get('group_by', [])
                target_col = validation.get('ensure_same')
                if group_cols and target_col and target_col in df_validated.columns:
                    valid_group_cols = [c for c in group_cols if c in df_validated.columns]
                    if len(valid_group_cols) == len(group_cols):
                        nunique_counts = df_validated.groupby(valid_group_cols)[target_col].transform('nunique')
                        mask = nunique_counts > 1
                        if mask.any():
                            code = ERROR_CODES.get('group_consistency', 'P-V-V-0501')
                            msg = f"{column_name} group inconsistency on {target_col}"
                            logger.warning(f"Group consistency validation failed for {column_name}: Column {target_col} must be the same within groups {valid_group_cols}")
                            record_errors(mask, msg, code=code)

            if rule_type == 'schema_reference_check':
                schema_ref = validation.get('reference') or column_def.get('schema_reference')
                if schema_ref:
                    mask = _apply_schema_reference_validation(
                        df_validated,
                        column_name,
                        allow_null,
                        schema_ref,
                        schema_data,
                        data_section=validation.get('data_section'),
                        field_name=validation.get('field'),
                        exclude_codes=validation.get('exclude_codes', []),
                    )
                    if mask is not None and mask.any():
                        code = ERROR_CODES.get('schema_reference_check', 'P-V-V-0506')
                        msg = f"{column_name} not in {schema_ref}"
                        record_errors(mask, msg, code=code)

            if rule_type == 'starts_with_schema_reference':
                schema_ref = validation.get('reference') or column_def.get('schema_reference')
                if schema_ref:
                    ref_data = schema_data.get(f'{schema_ref}_data', {})
                    allowed_codes = _get_schema_reference_allowed_codes(
                        ref_data,
                        data_section=validation.get('data_section'),
                        field_name=validation.get('field'),
                    )
                    if allowed_codes:
                        codes_regex = "|".join([re.escape(str(c)) for c in allowed_codes if c is not None])
                        pattern = f"^({codes_regex})"
                        mask = ~df_validated[column_name].astype(str).str.match(pattern, na=False)
                        if allow_null:
                            mask &= df_validated[column_name].notna()
                        if mask.any():
                            code = ERROR_CODES.get('starts_with_schema_reference', 'P-V-V-0501')
                            msg = f"{column_name} does not start with valid code from {schema_ref}"
                            logger.warning(f"Starts-with validation failed for {column_name}: {mask.sum()} invalid values")
                            record_errors(mask, msg, code=code)

            if rule_type == 'derived_pattern':
                source_cols = validation.get('source_columns', [])
                separator = validation.get('separator', '-')
                
                regex_parts = []
                for src_col in source_cols:
                    if src_col in columns_schema:
                        src_def = columns_schema[src_col]
                        src_regex = _get_column_representative_regex(src_col, src_def, schema_data)
                        regex_parts.append(src_regex)
                    else:
                        regex_parts.append(r"[^ \-]+")
                
                combined_pattern = f"^{re.escape(separator).join(regex_parts)}$"
                df_str = df_validated[column_name].astype(str)
                mask = ~df_str.str.match(combined_pattern, na=False)
                if allow_null:
                    mask &= df_validated[column_name].notna()
                    
                if mask.any():
                    code = ERROR_CODES.get('derived_pattern', 'P-V-V-0501')
                    msg = f"{column_name} dynamic pattern mismatch"
                    logger.warning(f"Derived pattern validation failed for {column_name}: {mask.sum()} invalid values (Target pattern: {combined_pattern})")
                    record_errors(mask, msg, code=code)

        # Backward-compatible default schema_reference validation when no
        # explicit schema_reference_check rule is declared.
        has_explicit_schema_ref_rule = any(
            rule.get('type') == 'schema_reference_check' for rule in validation_rules
        )
        schema_ref = column_def.get('schema_reference')
        if schema_ref and not has_explicit_schema_ref_rule:
            mask = _apply_schema_reference_validation(
                df_validated, column_name, allow_null, schema_ref, schema_data
            )
            if mask is not None and mask.any():
                code = ERROR_CODES.get('schema_reference_check', 'P-V-V-0506')
                msg = f"{column_name} not in {schema_ref}"
                record_errors(mask, msg, code=code)

    # Merge raw input pattern validation errors (collected before transformations)
    if raw_errors is not None and error_col in df_validated.columns:
        raw_errors_aligned = raw_errors.reindex(df_validated.index, fill_value="")
        has_raw_errors = raw_errors_aligned != ""
        if has_raw_errors.any():
            for idx in df_validated.index[has_raw_errors]:
                existing = df_validated.at[idx, error_col]
                raw_msg = raw_errors_aligned[idx]
                if not existing:
                    df_validated.at[idx, error_col] = raw_msg
                else:
                    df_validated.at[idx, error_col] = f"{existing}; {raw_msg}".strip("; ")

    # Summary: log validation statistics
    total_columns = 0
    total_rules = 0
    skipped_columns = []
    for col_name, col_def in columns_schema.items():
        if not isinstance(col_def, dict):
            continue
        if col_name not in df_validated.columns:
            rules = _normalize_validation_rules(col_def.get('validation', {}))
            if rules:
                skipped_columns.append(col_name)
            continue
        total_columns += 1
        rules = _normalize_validation_rules(col_def.get('validation', {}))
        total_rules += len(rules)
    if skipped_columns:
        logger.warning(
            f"Validation skipped for {len(skipped_columns)} columns (not in DataFrame): {skipped_columns}"
        )
    logger.info(
        f"Validation complete: {total_columns} columns, {total_rules} rules processed"
    )

    return df_validated


def _normalize_validation_rules(validation: TypingAny) -> List[Dict[str, TypingAny]]:
    """Normalize validation config to a list of rule objects."""
    if isinstance(validation, list):
        return [rule for rule in validation if isinstance(rule, dict)]
    if isinstance(validation, dict):
        scalar_keys = {
            'pattern',
            'min_length',
            'max_length',
            'min_value',
            'max_value',
            'format',
            'allowed_values',
        }
        nested_rule_keys = {'schema_reference_check', 'starts_with_schema_reference'}
        rules: List[Dict[str, TypingAny]] = []

        for key in scalar_keys:
            if key in validation:
                rule = {'type': key, key: validation[key]}
                if 'description' in validation:
                    rule['description'] = validation['description']
                rules.append(rule)

        for key in nested_rule_keys:
            value = validation.get(key)
            if isinstance(value, dict):
                rule = {'type': key, **value}
                rules.append(rule)

        return rules
    return []


def _apply_schema_reference_validation(
    df: pd.DataFrame,
    column_name: str,
    allow_null: bool,
    schema_ref: str,
    schema_data: dict,
    data_section: Optional[str] = None,
    field_name: Optional[str] = None,
    exclude_codes: Optional[List[str]] = None,
) -> Optional[pd.Series]:
    """Validate a column against allowed values from a referenced schema."""
    ref_data = schema_data.get(f'{schema_ref}_data', {})
    if not ref_data:
        return None

    allowed_codes = _get_schema_reference_allowed_codes(
        ref_data,
        data_section=data_section,
        field_name=field_name,
    )
    if allowed_codes is not None:
        # Filter out excluded codes (e.g., pending status)
        if exclude_codes:
            excluded_values = set(exclude_codes)
            for entry in ref_data.get('approval', []):
                if entry.get('code') in exclude_codes:
                    excluded_values.update(entry.get('aliases', []))
                    if entry.get('status'):
                        excluded_values.add(entry.get('status'))

            allowed_codes = [c for c in allowed_codes if c not in excluded_values]

        mask = ~df[column_name].isin(allowed_codes)
        if allow_null:
            mask &= df[column_name].notna()
        invalid_count = mask.sum()
        if invalid_count > 0:
            logger.warning(
                f"Schema reference validation failed for {column_name}: "
                f"{invalid_count} values not in {schema_ref}"
            )
        return mask

    if 'choices' in ref_data:
        allowed = ref_data.get('choices', [])
        mask = ~df[column_name].isin(allowed)
        if allow_null:
            mask &= df[column_name].notna()
        invalid_count = mask.sum()
        if invalid_count > 0:
            logger.warning(f"Schema reference validation failed for {column_name}: {invalid_count} invalid values")
        return mask

    return None


def _get_schema_reference_allowed_codes(
    ref_data: Dict[str, TypingAny],
    data_section: Optional[str] = None,
    field_name: Optional[str] = None,
) -> Optional[List[str]]:
    """
    Return allowed values from a referenced schema.

    Preference order:
    1. The explicitly requested `data_section` and `field_name`
    2. The schema's own `data_section` using the explicit field or `code`
    3. The first list containing dict rows with the explicit field or `code`
    """
    target_field = field_name or 'code'
    target_section = data_section or ref_data.get('data_section')

    if isinstance(target_section, str):
        rows = ref_data.get(target_section)
        if isinstance(rows, list):
            return [
                item.get(target_field)
                for item in rows
                if isinstance(item, dict) and item.get(target_field)
            ]

    return None


def _get_column_representative_regex(column_name: str, column_def: dict, schema_data: dict) -> str:
    """
    Helper to get a representative regex for a column based on its validation rules.
    Used by derived_pattern validation.
    """
    validation_rules = _normalize_validation_rules(column_def.get('validation', {}))

    # 1. Check for explicit pattern
    for rule in validation_rules:
        if rule.get('type') == 'pattern' and 'pattern' in rule:
            pat = rule['pattern']
            # Strip anchors
            if pat.startswith('^'):
                pat = pat[1:]
            if pat.endswith('$'):
                pat = pat[:-1]
            return f"({pat})"

    # 2. Check for schema reference
    for rule in validation_rules:
        if rule.get('type') in ['schema_reference_check', 'starts_with_schema_reference']:
            schema_ref = rule.get('reference') or column_def.get('schema_reference')
            if schema_ref:
                ref_data = schema_data.get(f'{schema_ref}_data', {})
                allowed_codes = _get_schema_reference_allowed_codes(
                    ref_data,
                    data_section=rule.get('data_section'),
                    field_name=rule.get('field')
                )
                if allowed_codes:
                    codes_regex = "|".join([re.escape(str(c)) for c in allowed_codes if c is not None])
                    return f"({codes_regex})"

    # Fallback to general schema_reference if no explicit validation rule found
    schema_ref = column_def.get('schema_reference')
    if schema_ref:
        ref_data = schema_data.get(f'{schema_ref}_data', {})
        allowed_codes = _get_schema_reference_allowed_codes(ref_data)
        if allowed_codes:
            codes_regex = "|".join([re.escape(str(c)) for c in allowed_codes if c is not None])
            return f"({codes_regex})"

    # 3. Fallback for columns with no defined pattern or reference
    return r"[^ \-]+"

