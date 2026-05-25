import json
import sys
from pathlib import Path
from typing import Dict, Any

def compact_log(log_path: str, output_path: str = None):
    """
    Compacts a large debug_log.json by stripping redundant error fields
    and optionally filtering high-verbosity messages.
    """
    p = Path(log_path)
    if not p.exists():
        print(f"Error: {log_path} not found")
        return

    print(f"Reading {p} ({p.stat().st_size / 1024 / 1024:.1f} MB)...")
    try:
        with open(p, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error loading JSON: {e}")
        return

    original_count = len(data.get("errors", []))
    print(f"Processing {original_count} errors and {len(data.get('messages', []))} messages...")

    # 1. Compact Errors (Schema-Driven "Dry" Conversion)
    compacted_errors = []
    for err in data.get("errors", []):
        msg = err.get("message", {})
        if isinstance(msg, dict) and msg.get("error_code"):
            # Strip redundant fields that exist in the error catalogs
            new_msg = {
                "error_code": msg["error_code"],
                "row": msg.get("row"),
                "column": msg.get("column")
            }
            # Remove from top-level err object too if they exist
            err.pop("remediation", None)
            err.pop("remediation_type", None)
            
            err["message"] = new_msg

        # 1.1 Strip massive context objects (THE MAIN BLOAT CAUSE)
        ctx = err.get("context", {})
        if isinstance(ctx, dict):
            ctx.pop("schema_data", None)
            ctx.pop("error_catalog", None)
            ctx.pop("blueprint", None)
            ctx.pop("fill_history", None)
            err["context"] = ctx

        compacted_errors.append(err)
    
    data["errors"] = compacted_errors

    # 2. Filter Messages (Strip Level 3 Trace data if over 100MB)
    original_msg_count = len(data.get("messages", []))
    if p.stat().st_size > 50 * 1024 * 1024:
        print("File is large, stripping Level 3 (Trace) messages...")
        data["messages"] = [m for m in data.get("messages", []) if m.get("level", 2) < 3]
        print(f"Messages reduced from {original_msg_count} to {len(data['messages'])}")

    # 3. Save Minified JSON
    out = Path(output_path) if output_path else p.with_name(p.stem + "_compacted.json")
    print(f"Saving to {out}...")
    try:
        with open(out, 'w', encoding='utf-8') as f:
            # Use separators to remove all whitespace (minification)
            json.dump(data, f, separators=(',', ':'))
    except Exception as e:
        print(f"Error saving JSON: {e}")
        return

    print(f"Done! Final size: {out.stat().st_size / 1024 / 1024:.1f} MB")
    print(f"Reduction: {(1 - (out.stat().st_size / p.stat().st_size)) * 100:.1f}%")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python compact_log.py <path_to_debug_log.json> [output_path]")
    else:
        output = sys.argv[2] if len(sys.argv) > 2 else None
        compact_log(sys.argv[1], output)
