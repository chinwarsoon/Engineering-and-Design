# Generated from dcc_mdl.ipynb
# This file contains all code cells from the notebook

# ===== CELL 1 =====
# P.1 Import necessary libraries and set debug mode

debug_dev_mode = False

def status_print(*args, **kwargs):
    builtins.print(*args, **kwargs)

def debug_print(*args, **kwargs):
    if debug_dev_mode:
        builtins.print(*args, **kwargs)

def cell_done(message):
    if not debug_dev_mode:
        status_print(f"Completed: {message}.")

def debug_display(value):
    if debug_dev_mode and display is not None:
        display(value)

import_errors = []

try:
    import builtins
except Exception as e:
    builtins = None
    import_errors.append(f"builtins: {e}")

try:
    import os
except Exception as e:
    os = None
    import_errors.append(f"os: {e}")

try:
    import sys
except Exception as e:
    sys = None
    import_errors.append(f"sys: {e}")

try:
    import pandas as pd
except Exception as e:
    pd = None
    import_errors.append(f"pandas: {e}")

try:
    import numpy as np
except Exception as e:
    np = None
    import_errors.append(f"numpy: {e}")

try:
    from IPython.display import display, clear_output
except Exception as e:
    display = None
    clear_output = None
    import_errors.append(f"IPython.display: {e}")

try:
    from pandas.tseries.offsets import BDay
except Exception as e:
    BDay = None
    import_errors.append(f"pandas.tseries.offsets.BDay: {e}")

try:
    from datetime import datetime, timedelta
except Exception as e:
    datetime = None
    timedelta = None
    import_errors.append(f"datetime: {e}")

try:
    import argparse
except Exception as e:
    argparse = None
    import_errors.append(f"argparse: {e}")

try:
    import shutil
except Exception as e:
    shutil = None
    import_errors.append(f"shutil: {e}")

try:
    import duckdb
except Exception as e:
    duckdb = None
    import_errors.append(f"duckdb: {e}")

try:
    import matplotlib.pyplot as plt
except Exception as e:
    plt = None
    import_errors.append(f"matplotlib.pyplot: {e}")

try:
    import seaborn as sns
except Exception as e:
    sns = None
    import_errors.append(f"seaborn: {e}")

try:
    import json
except Exception as e:
    json = None
    import_errors.append(f"json: {e}")

try:
    from pathlib import Path
except Exception as e:
    Path = None
    import_errors.append(f"pathlib.Path: {e}")

try:
    from ipywidgets import widgets
except Exception as e:
    widgets = None
    import_errors.append(f"ipywidgets.widgets: {e}")

try:
    import google.colab
    from google.colab import files, drive
    google_colab_available = True
except Exception as e:
    google_colab = None
    files = None
    drive = None
    google_colab_available = False
    import_errors.append(f"google.colab: {e}")

try:
    import tkinter as tk
    from tkinter import filedialog
    tkinter_available = True
except Exception as e:
    tk = None
    filedialog = None
    tkinter_available = False
    import_errors.append(f"tkinter: {e}")

try:
    import xlsxwriter
except Exception as e:
    xlsxwriter = None
    import_errors.append(f"xlsxwriter: {e}")

if import_errors:
    status_print("Library import check completed with issues:")
    for error_message in import_errors:
        status_print(f"- {error_message}")
else:
    debug_print("All libraries imported successfully.")

# P.1.1 Validate critical dependencies
critical_imports = {'pandas': pd, 'numpy': np, 'os': os, 'sys': sys}
missing_critical = [name for name, module in critical_imports.items() if module is None]

if missing_critical:
    status_print(f"CRITICAL ERROR: Missing essential libraries: {', '.join(missing_critical)}")
    status_print("Cannot proceed without these dependencies. Please install them and restart the kernel.")
    raise ImportError(f"Missing critical dependencies: {', '.join(missing_critical)}")
else:
    debug_print("All critical dependencies validated successfully.")
    debug_print(f"Python: {sys.version}")
    debug_print(f"Pandas: {pd.__version__}")
    debug_print(f"NumPy: {np.__version__}")

# ===== CELL 2 =====
# P.2 define Global variables for the notebook.
# Note: Global declarations are not needed at module level - module-level variables are automatically global

is_colab = False
overwrite_existing_downloads = True # Set to True to overwrite existing files, False to skip
debug_dev_mode = False

# Auto-detect schema_register.json from the current working directory
schema_register_candidates = [
    Path.cwd() / 'schema_register.json',
    Path.cwd() / 'dcc' / 'schema_register.json',
]
schema_register_file = next((str(path) for path in schema_register_candidates if path.exists()), None)
if schema_register_file:
    status_print(f"✓ Auto-detected schema_register.json at: {schema_register_file}")
else:
    debug_print("schema_register.json not found in current directory; will use native definitions")

uploaded_file_name = None
sheet_names = None

# Setup file paths based on environment
# Use pathlib.Path for cross-platform compatibility
pc_name = "CESL-22120"

# Windows-specific paths (default)
win_upload_file = Path(r"K:\J Submission\Submittal and RFI Tracker Lists.xlsx")
win_download_path = Path(r"K:\J Submission\AI Tools and Report")

# Linux/Colab paths (fallback)
linux_upload_file = Path.home() / "dsai" / "Engineering-and-Design" / "dcc" / "data" / "Submittal and RFI Tracker Lists.xlsx"
linux_download_path = Path.home() / "dsai" / "Engineering-and-Design" / "dcc" / "output"

# Colab-specific path
colab_upload_file = Path("/content/sample_data/Submittal and RFI Tracker Lists.xlsx")
colab_download_path = Path("/content/output")

# Select paths based on environment
if google_colab_available and google_colab is not None:
    is_colab = True
    upload_file_name = str(colab_upload_file)
    download_file_path = str(colab_download_path)
    debug_print("Running in Google Colab environment")
elif sys.platform == 'win32' and win_upload_file.exists():
    # Windows with correct paths
    upload_file_name = str(win_upload_file)
    download_file_path = str(win_download_path)
    debug_print(f"Running on Windows, using K: drive paths")
else:
    # Linux/Mac or Windows without K: drive
    if not linux_upload_file.exists():
        status_print(f"WARNING: Default input file not found at {linux_upload_file}")
        status_print("You may need to set upload_file_name manually or ensure the file exists.")
    upload_file_name = str(linux_upload_file)
    download_file_path = str(linux_download_path)
    debug_print(f"Running on {sys.platform}, using home directory paths")

# Sheet name to load
upload_sheet_name = "Prolog Submittals "

# Ensure download directory exists
try:
    Path(download_file_path).mkdir(parents=True, exist_ok=True)
    debug_print(f"Download path ready: {download_file_path}")
except Exception as e:
    status_print(f"WARNING: Could not create download directory: {e}")

# Define column range to be loaded.
start_col = 'P'
end_col = 'AP'
header_row_index = 4

# define nickname used for 'PEN' in excel file
pending_status = "Awaiting S.O.'s response"

# Define duration
duration_is_working_day = True
first_review_duration = 20
second_review_duration = 14
resubmission_duration = 14

# file loading stage
progress_stage = "not_start"

# Print all variables and confirm the progress is complete
status_print(f"Debug/Dev Mode: {debug_dev_mode}")
debug_print(f"Environment: {'Google Colab' if is_colab else 'Local'}")
debug_print(f"Upload File: {upload_file_name}")
debug_print(f"Download Path: {download_file_path}")
debug_print(f"Start Column: {start_col}")
debug_print(f"End Column: {end_col}")
debug_print(f"Header Row Index: {header_row_index}")
debug_print(f"Pending Status: {pending_status}")
debug_print(f"Duration is working day: {duration_is_working_day}")
debug_print(f"First Review Duration: {first_review_duration}")
debug_print(f"Second Review Duration: {second_review_duration}")
debug_print(f"Resubmission Duration: {resubmission_duration}")
debug_print(f"Progress Stage: {progress_stage}")
debug_print(f"Overwrite Existing Downloads: {overwrite_existing_downloads}")
debug_print(f"Schema Register File: {schema_register_file}")
status_print("All parameters are loaded.")

# ===== CELL 3 =====
# P.3 display current environment


print(f"Python Version: {sys.version}")
print(f"Pandas Version: {pd.__version__}")
print(f"NumPy Version: {np.__version__}")

if sys.platform.startswith('linux'):
    print("Running on Linux")
else:
    print(f"Running on {sys.platform}")

if google_colab_available:
    is_colab = True
    print("Environment: Google Colab")
else:
    is_colab = False
    print("Environment: Local (e.g., VS Code, Jupyter, or other local IDE)")

# ===== CELL 4 =====
# P.4 Define the parser to allow user to give Excel File path and output file path when run python file from terminal
parser = argparse.ArgumentParser(description="Process DCC Register Excel file and generate reports.")

# Add arguments for file paths and sheet name
parser.add_argument('--upload_file', type=str, help='Path to the input Excel file (e.g., "Submittal and RFI Tracker Lists.xlsx")')
parser.add_argument('--upload_sheet', type=str, help='Name of the sheet to process in the Excel file (e.g., "Prolog Submittals ")')
parser.add_argument('--download_path', type=str, help='Path to the output directory for generated files (e.g., "K:\\J Submission\\AI Tools and Report")')
parser.add_argument('--overwrite', type=str, choices=['True', 'False'], help='If overwrite if files exists (True/False)')
parser.add_argument('--debug_mode', type=str, choices=['True', 'False'], help='Enable debug/development print statements (True/False)')
parser.add_argument('--schema_register', type=str, help='Path to an alternative schema register JSON file')

# Use parse_known_args() to handle arguments that are not defined by our parser (e.g., kernel arguments in Colab)
# This prevents SystemExit errors when running interactively in environments like Colab if kernel args are present.
args, unknown_args = parser.parse_known_args()

# Now, 'args' will contain the values for 'upload_file', 'upload_sheet', and 'download_path'.
# If no arguments were provided by the user, these attributes will be None. The DummyArgs class is no longer necessary.

# Pass arguments to global parameters if they are provided
if args.upload_file:
    upload_file_name = args.upload_file
    status_print(f"Global 'upload_file_name' set to: {upload_file_name}")
if args.upload_sheet:
    upload_sheet_name = args.upload_sheet
    status_print(f"Global 'upload_sheet_name' set to: {upload_sheet_name}")
if args.download_path:
    download_file_path = args.download_path
    status_print(f"Global 'download_file_path' set to: {download_file_path}")
if args.overwrite:
    overwrite_existing_downloads = True if args.overwrite == 'True' else False
    status_print(f"Global 'overwrite_existing_downloads' set to: {overwrite_existing_downloads}")
if args.debug_mode:
    debug_dev_mode = True if args.debug_mode == 'True' else False
    status_print(f"Global 'debug_dev_mode' set to: {debug_dev_mode}")
if args.schema_register:
    schema_register_file = args.schema_register
    status_print(f"Global 'schema_register_file' set to: {schema_register_file}")

# ===== CELL 5 =====
# P.5 Define local 'Schema', approval_code_mapping, and other constants. 

# in case no external schema register is given, use the default schema defined below.
# The schema register will be used to dynamically generate the schema and approval code mapping used in the notebook,
# which allows more flexibility for future changes of the DCC register format and content.

schema = {
    #Document Information
    'Document_ID' : ['CES_SALCON-SDC JV Cor Ref No'],
    'Document_Title' : ['Document Description'], # DCC register did not record correct Document_Title, which shall be further extracted from MDL
    'Document_Revision' : ['Rev ', 'This Revision'],
    'Department' : ['Dept'],
    'Discipline' : ['Discipline'],
    'Project_Code' : ['Proj. Code'],
    'Facility_Code' : ['Proj. Prefix'],
    'Document_Type' : ['Doc Type'],
    'Document_Sequence_Number' : ['Number'],
    'Submitted_By' : ['Document Owner'],
    'Archive_Location' : ['File Path'],
    #Submission Information
    'Submission_Session' : ['Prolog Submittal No.','Prolog Submittal No..1'],
    'Submission_Session_Subject' : ['Document Description / Drawing Title'],
    'Submission_Session_Revision' : ['Prolog Rev.', 'Prolog Rev..1'],
    'Transmittal_Number' : ['Project Wise Transmittal No.  (WIP)'],
    'Submission_Date' : ['Date Submit'],
    'Resubmission_Forecast_Date' : ['Target date to resubmit'],
    'Submission_Reference_1' : ['Submission Reference 1'],
    'Submission_Closed' : ['Closed'],
    #Review Information
    'Reviewer' : ['Reviewer'],
    'Review_Return_Actual_Date' : ['Actual Date S.O. Response'],
    'Review_Status' : ['SO Review Status', 'This Revision Approval Status'],
    'Review_Comments' : ['S.O. Review and Comments'],
    'Resubmission_Required' : ['To Resubmit (Yes/No)'],
    #Other Information
    'Internal_Reference' : ['Internal Reference'],
    'Notes' : ['Notes', 'Note', 'Other Notes','Remark'],
    #Calculated Columns
    'All_Approval_Code': ['All Approval Code'],
    'Approval_Code' : ['Approval Code'],
    'Review_Status_Code' : ['Review Status Code'],
    'First_Submittion_Date': ['1st Submittion Date'],
    'This_Submission_Date': ['This Submission Date'],
    'This_Review Return_Date': ['This Review Return Date'],
    'This_Submission_Approval_Status': ['This Submission Approval Status'],
    'This_Submission_Approval_Code': ['This Submission Approval Code'],
    'Latest_Submittion_Date': ['Latest Submittion Date'],
    'Latest_Revision': ['Latest Revision'],
    'Latest_Approval_Status' : ['Latest Approval Status'],
    'All_Submission_Sessions': ['All Submission Sessions'],
    'All_Submission_Dates': ['All Submission Dates'],
    'All_Submission_Session_Revisions': ['All Submission Session Revisions'],
    'Count_of_Submissions': ['Count of Submissions', '# of Submissions'],
    'Review_Return_Plan_Date' : ['Date S.O. to Response (20 Working Days/ 14 Working Days)', 'Date S.O. to Response\n(20 Working Days/\n 14 Working Days)'],
    'Resubmission_Plan_Date' : ['Date CES to Response(14 Working Days)', 'Date CES to Response\n(14 Working Days)'],
    'Resubmission_Overdue_Status' : ['Overdue to resubmit'],
    'Delay_of_Resubmission' : ['Delays to resubmit'],
    'Duration_of_Review': ['SO Response Variance'],

}

# define Approval_Code mapping
raw_mapping ={
    ('Rejected', 'REJ') : 'REJ',
    ('Not Approved - Revise and resubmit', 'Not Approved') : 'NAP',
    ('Approved with Comments', 'Approved as noted') : 'AWC',
    ('Approved', 'APP') : 'APP',
    ('For Information', 'INF') : 'INF',
    ('Void', '(VOID / NOT IN USE)', '(VOID  NOT IN USE)') : 'VOID',
    ('Pending Review', 'Pending', "Awaiting S.O.'s response",'Awaiting S.O. Review') : 'PEN',
}
approval_code_mapping = {}
for variations, code in raw_mapping.items():
    for item in variations:
        approval_code_mapping[item] = code

print("Schema:")
print(schema)
print("Approval_Code Mapping:")
print(approval_code_mapping)
cell_done("Default schema and approval code mapping prepared")


# ===== CELL 6 =====
# P.6 Load schema, parameters, and row mapping from JSON config when available.

# Prefer schema_register.json as the single source of truth.
# Fall back to global_parameters.json only for backward compatibility.
# Otherwise, keep using the default schema and parameters defined above.
# Print the effective schema map and approval code mapping for checking.

default_parameters = {
    'start_col': start_col,
    'end_col': end_col,
    'header_row_index': header_row_index,
    'pending_status': pending_status,
    'duration_is_working_day': duration_is_working_day,
    'first_review_duration': first_review_duration,
    'second_review_duration': second_review_duration,
    'resubmission_duration': resubmission_duration,
    'progress_stage': progress_stage,
    'pc_name': pc_name,
    'upload_file_name': upload_file_name,
    'upload_colab_file_name': upload_colab_file_name,
    'upload_sheet_name': upload_sheet_name,
    'download_file_path': download_file_path,
    'overwrite_existing_downloads': overwrite_existing_downloads,
    'is_colab': is_colab,
}

global_parameters_candidates = [
    Path('global_parameters.json'),
    Path('dcc/global_parameters.json'),
    Path.cwd() / 'global_parameters.json',
    Path.cwd() / 'dcc' / 'global_parameters.json',
]

schema_register_candidates = []
if schema_register_file:
    schema_register_candidates.append(Path(schema_register_file))
schema_register_candidates.extend([
    Path('schema_register.json'),
    Path('dcc/schema_register.json'),
    Path.cwd() / 'schema_register.json',
    Path.cwd() / 'dcc' / 'schema_register.json',
])

schema_register_path = next((path for path in schema_register_candidates if path.exists()), None)
global_parameters_path = next((path for path in global_parameters_candidates if path.exists()), None)
effective_parameters = default_parameters.copy()
effective_row_mapping = None

if schema_register_path:
    with schema_register_path.open('r', encoding='utf-8') as f:
        schema_register = json.load(f)

    if isinstance(schema_register, dict):
        file_schema = schema_register.get('schema', schema_register)
        file_parameters = schema_register.get('parameters', {})
        effective_row_mapping = schema_register.get('row_mapping', {})
    else:
        file_schema = schema
        file_parameters = {}
        effective_row_mapping = {}

    if isinstance(file_schema, dict) and file_schema:
        schema = file_schema

    if isinstance(file_parameters, dict) and file_parameters:
        effective_parameters.update(file_parameters)
        for parameter_name, parameter_value in file_parameters.items():
            globals()[parameter_name] = parameter_value

    if isinstance(effective_row_mapping, dict) and effective_row_mapping:
        approval_code_mapping = {}
        for approval_code, aliases in effective_row_mapping.items():
            if isinstance(aliases, list):
                for alias in aliases:
                    approval_code_mapping[alias] = approval_code

    status_print(f"Success! Register file loaded successfully from: {schema_register_path}")
elif global_parameters_path:
    with global_parameters_path.open('r', encoding='utf-8') as f:
        file_parameters = json.load(f)

    if isinstance(file_parameters, dict) and file_parameters:
        effective_parameters.update(file_parameters)
        for parameter_name, parameter_value in file_parameters.items():
            globals()[parameter_name] = parameter_value

    status_print(f"Success! Register file loaded successfully from fallback parameters file: {global_parameters_path}")
else:
    status_print("No JSON config found. Using default notebook schema and parameters.")

print("Schema:")
print(schema)
print("Parameters:")
print(effective_parameters)
print("Approval_Code Mapping:")
print(approval_code_mapping)
cell_done("Schema, parameters, and row mapping loaded")


# ===== CELL 7 =====
# 1.1.1 load the excel file based on the environment and user input.

# to check if 'upload_file_name' is "", if not, check if this file exsit and load the file to 'uploaded_file_name', otherwise,
# ask user to upload an excel file, try google.colab first, then fall back to non-colab environemnt to ask user to select an excel file.

progress_stage = "start"
status_print(f"Progress: {progress_stage} - initialising file upload")

current_uploaded_file_name = None # Initialize a variable to hold the determined file name

# Use the global 'is_colab' value determined by the earlier environment check cell.
if is_colab:
    status_print("Environment: Google Colab detected.")
    if upload_colab_file_name: # Check if a Colab-specific path is provided
        if not os.path.exists('/content/drive'):
            drive.mount('/content/drive')
        if os.path.exists(upload_colab_file_name):
            current_uploaded_file_name = upload_colab_file_name
            status_print(f"Success! Local file loaded successfully from Colab path: '{upload_colab_file_name}'.")
            progress_stage = "colab-preselected-found"
        else:
            status_print(f"Path not found for pre-configured Colab file '{upload_colab_file_name}'. Attempting user upload as a fallback.")
            current_uploaded_file_name = None # Reset if pre-configured not found

    # If file still not determined and still in Colab, prompt user to upload via Colab's file uploader
    if current_uploaded_file_name is None:
        progress_stage = "colab-prepare"
        status_print(f"Progress: {progress_stage} - waiting for file upload")
        status_print("Please upload the 'Submittal and RFI Tracker Lists.xlsx' file.")
        uploaded_dict = files.upload() # files.upload() returns a dictionary
        if uploaded_dict:
            current_uploaded_file_name = list(uploaded_dict.keys())[0]
            progress_stage = "colab-uploaded"
            status_print(f"Progress: {progress_stage} - Local file loaded successfully: '{current_uploaded_file_name}'.")
        else:
            progress_stage = "colab-no-file"
            status_print("Progress: colab-no-file - No file was uploaded.")

else: # Not in Colab (local environment)
    status_print("Environment: Local (e.g., VS Code, Jupyter, or other local IDE) detected.")

    default_data_file = None
    local_data_candidates = [
        Path("dcc/data") / "Submittal and RFI Tracker Lists.xlsx",
        Path("data") / "Submittal and RFI Tracker Lists.xlsx",
    ]
    if upload_file_name:
        upload_file_basename = Path(upload_file_name).name
        local_data_candidates = [
            Path("dcc/data") / upload_file_basename,
            Path("data") / upload_file_basename,
        ] + local_data_candidates
    default_data_file = next((str(path) for path in local_data_candidates if path.exists()), None)

    if upload_file_name and os.path.exists(upload_file_name):
        # Scenario for local execution: check if a local path is pre-configured
        current_uploaded_file_name = upload_file_name
        progress_stage = "local-preselected-found"
        status_print(f"Success! Local file loaded successfully: '{upload_file_name}'.")
    elif default_data_file:
        current_uploaded_file_name = default_data_file
        progress_stage = "local-default-data-found"
        status_print(f"Success! Local file loaded successfully from development fallback: '{current_uploaded_file_name}'.")
    else:
        if upload_file_name: # if it was specified but not found
            status_print(f"Path not found for pre-configured local file '{upload_file_name}'. Attempting user selection as a fallback.")

        root = None
        try:
            if not tkinter_available or tk is None or filedialog is None:
                raise ImportError("tkinter is not available")
            root = tk.Tk()
            root.withdraw() # Hide the main window
            progress_stage = "gui-prompt"
            status_print(f"Progress: {progress_stage} - Opening file selection dialog...")
            current_uploaded_file_name = filedialog.askopenfilename(
                title="Select 'Submittal and RFI Tracker Lists.xlsx'",
                filetypes=[("Excel files", "*.xlsx *.xls")]
            )
            if current_uploaded_file_name:
                progress_stage = "gui-selected"
                status_print(f"Progress: {progress_stage} - Local file loaded successfully via GUI: '{current_uploaded_file_name}'.")
            else:
                progress_stage = "gui-no-selection"
                fallback_cancelled_selection_candidates = [
                    Path("dcc/data") / "Submittal and RFI Tracker Lists.xlsx",
                    Path("data") / "Submittal and RFI Tracker Lists.xlsx",
                ]
                fallback_cancelled_selection_file = next((path for path in fallback_cancelled_selection_candidates if path.exists()), None)
                if fallback_cancelled_selection_file is not None:
                    current_uploaded_file_name = str(fallback_cancelled_selection_file)
                    progress_stage = "gui-fallback-default"
                    status_print(f"Progress: {progress_stage} - GUI selection cancelled. Local fallback file loaded successfully: '{current_uploaded_file_name}'.")
                else:
                    status_print("Progress: gui-no-selection - No file was selected via GUI and no fallback file was found. Please enter the full path manually.")
        except Exception as gui_error:
            progress_stage = "tkinter-missing"
            status_print(f"Progress: tkinter-missing - GUI file selection is unavailable: {gui_error}")
            status_print("Please enter the full path to your Excel file:")
        finally:
            if root is not None:
                try:
                    root.destroy()
                except Exception:
                    pass

        if not current_uploaded_file_name: # If GUI selection failed or Tkinter not found
            progress_stage = "manual-input"
            current_uploaded_file_name = input("File path: ")
            status_print(f"Progress: {progress_stage} - Local file loaded successfully from provided path: '{current_uploaded_file_name}'. Please ensure the file exists at this path.")
        elif current_uploaded_file_name:
            progress_stage = "manual-success"
            status_print(f"Progress: {progress_stage} - Local file loaded successfully from selected path: '{current_uploaded_file_name}'.")

# Assign to global variable and report final status
uploaded_file_name = current_uploaded_file_name
if uploaded_file_name:
    status_print(f"Success! Local file loaded successfully and ready for processing: '{uploaded_file_name}'.")
else:
    status_print("Progress: Final check - no file selected or uploaded.")

# ===== CELL 8 =====
# 1.1.2 list down the sheet names
# in the uploaded excel file to help user select the correct sheet name for loading the data.

xls = pd.ExcelFile(uploaded_file_name)
sheet_names = xls.sheet_names
status_print("Sheet names in the Excel file:")
for i, name in enumerate(sheet_names):
    status_print(f"{i+1}. {name}")

# ===== CELL 9 =====
# 1.1.3 upload the sheet.
 
# no forward fill. assign null to black cells.
# Create a dropdown widget to allow the user to select a different sheet if needed.
# Header is on row 5 (index 4), so we will use header=4 when loading the sheet to ensure the correct header is used and blank cells are assigned null.
# define global variables to hold the selected sheet name and the corresponding DataFrame

df_selected_sheet_filled = None  # Initialize to prevent NameError in non-interactive mode

if upload_sheet_name is None:
    if widgets is None:
        status_print("ipywidgets is not available. Using fallback: first sheet will be loaded.")
        # Fallback: use first sheet if widgets not available
        if sheet_names and len(sheet_names) > 0:
            selected_sheet = sheet_names[0]
            try:
                df_selected_sheet_filled = pd.read_excel(uploaded_file_name, sheet_name=selected_sheet, header=header_row_index)
                status_print(f"\nSuccessfully loaded data from worksheet: '{selected_sheet}' (fallback mode). Blank cells are now null.")
                debug_print("First 5 rows of the processed DataFrame for the selected sheet:")
                debug_display(df_selected_sheet_filled.head())
            except Exception as e:
                status_print(f"CRITICAL ERROR: Failed to load fallback sheet '{selected_sheet}': {e}")
                df_selected_sheet_filled = None
        else:
            status_print("CRITICAL ERROR: No sheet names available in the workbook.")
            df_selected_sheet_filled = None
    else:
        # Create a dropdown widget for sheet selection (interactive mode)
        try:
            sheet_selector = widgets.Dropdown(
                options=sheet_names,
                description='Select a different sheet:',
                disabled=False,
                value=None # Set initial value to None so the user explicitly selects
            )

            def on_sheet_select(change):
                global selected_sheet, df_selected_sheet_filled
                clear_output(wait=True)
                selected_sheet = change.new
                if selected_sheet:
                    try:
                        # Load the selected sheet into a DataFrame, applying header=header_row_index. Blank cells will be null.
                        df_selected_sheet_filled = pd.read_excel(uploaded_file_name, sheet_name=selected_sheet, header=header_row_index)
                        status_print(f"\nSuccessfully loaded data from worksheet: '{selected_sheet}'. Blank cells are now null.")
                        debug_print("First 5 rows of the processed DataFrame for the selected sheet:")
                        debug_display(df_selected_sheet_filled.head())
                    except Exception as e:
                        status_print(f"Error loading sheet '{selected_sheet}': {e}")
                        df_selected_sheet_filled = None
                else:
                    status_print("Please select a sheet.")

            sheet_selector.observe(on_sheet_select, names='value')

            status_print("Please select Prolog Submittals from the dropdown below:")
            display(sheet_selector)
        except Exception as e:
            status_print(f"CRITICAL ERROR initializing widget: {e}. Using fallback: first sheet will be loaded.")
            # Fallback if widget creation fails
            if sheet_names and len(sheet_names) > 0:
                selected_sheet = sheet_names[0]
                try:
                    df_selected_sheet_filled = pd.read_excel(uploaded_file_name, sheet_name=selected_sheet, header=header_row_index)
                    status_print(f"\nSuccessfully loaded data from worksheet: '{selected_sheet}' (fallback mode). Blank cells are now null.")
                    debug_print("First 5 rows of the processed DataFrame for the selected sheet:")
                    debug_display(df_selected_sheet_filled.head())
                except Exception as e:
                    status_print(f"CRITICAL ERROR: Failed to load fallback sheet '{selected_sheet}': {e}")
                    df_selected_sheet_filled = None
else:
    # Use pre-defined sheet name
    selected_sheet = upload_sheet_name
    try:
        df_selected_sheet_filled = pd.read_excel(uploaded_file_name, sheet_name=selected_sheet, header=header_row_index)
        status_print(f"\nSuccessfully loaded data from worksheet: '{selected_sheet}'. Blank cells are now null.")
        debug_print("First 10 rows of the processed DataFrame for the selected sheet:")
        debug_display(df_selected_sheet_filled.head(10))
        cell_done(f"Worksheet '{selected_sheet}' loaded")
    except Exception as e:
        status_print(f"CRITICAL ERROR: Failed to load specified sheet '{selected_sheet}': {e}")
        df_selected_sheet_filled = None

# Final validation: ensure df_selected_sheet_filled is populated
if df_selected_sheet_filled is None:
    status_print("CRITICAL ERROR: No valid data loaded. df_selected_sheet_filled is None. Cannot continue.")

# ===== CELL 10 =====
# 1.2.1 Read selected worksheet

# load data to df_cleaned_and_filtered dataframe.
# Assign null to blank cells.
# Remove empty rows and columns.

# 1. Load the selected sheet into a DataFrame, applying header=4 and limiting columns by Excel label range
df_cleaned_and_filtered = pd.read_excel(
    uploaded_file_name,
    sheet_name=selected_sheet,
    header=header_row_index,
    usecols=f"{start_col}:{end_col}"
)

# 2. Remove empty rows
df_cleaned_and_filtered = df_cleaned_and_filtered.dropna(how='all')

# 3. Remove empty columns
df_cleaned_and_filtered = df_cleaned_and_filtered.dropna(axis=1, how='all')

status_print(f"\nSuccessfully loaded, and cleaned data from worksheet: '{selected_sheet}', row '{header_row_index}' as header, column '{start_col}' to '{end_col}'. Blank cells are now null.")
print("First 5 rows of the consolidated and cleaned DataFrame:")
debug_display(df_cleaned_and_filtered.head())

# summarize the number of null values in each column to check data quality
print("\nNull values in each column:")
null_counts = df_cleaned_and_filtered.isnull().sum()
for col, count in null_counts.items():
    status_print(f"{col}: {count} null values")
cell_done("Worksheet data loaded and cleaned")


# ===== CELL 11 =====
# 1.2.2 check if all column nicknames are available in schema. This will ensure complete column header mapping later.

# Create a list of all column names that are expected in the DataFrame, based on the schema.
# These are the standard names we want to ensure exist after renaming.
expected_column_headers = list(schema.keys())
print(f"Standard Column names are: '{expected_column_headers}'")

# Get the actual columns present in the DataFrame after initial loading and renaming.
actual_column_headers = df_cleaned_and_filtered.columns.tolist()
print(f"Actual Column names are: '{actual_column_headers}'")

# Get all 'nicknames' from 'schema'
expected_column_header_nicknames = [item for sublist in schema.values() for item in sublist]
print(f"Standard Column nicknames are: '{expected_column_header_nicknames}'")

# check for columns in the DataFrame that are not in the schema
# (though the initial filtering by usecols and renaming should handle this to some extent).
unexpected_column_headers = [col for col in actual_column_headers if col not in expected_column_headers and col not in [item for sublist in schema.values() for item in sublist]]
if unexpected_column_headers:
    status_print("Warning: The following columns are in the DataFrame but not defined in the schema:")
    for col in unexpected_column_headers:
        status_print(f"- {col}")
else:
    print("All expected columns nicknames in the DataFrame are present in the Schema.")

# list proposed column nickname mapping for checking
# Generate the Checking Result
check_results = []
for target_name, nicknames in schema.items():
    # A: Check if the Target Name itself is already correct in the Excel
    if target_name in actual_column_headers:
        found_name = target_name
        status = "✅ Already Correct"
    else:
        # B: Check if any of the nicknames exist
        match = next((nick for nick in nicknames if nick in actual_column_headers), None)
        if match:
            found_name = match
            status = "🔗 Match Found"
        else:
            found_name = "---"
            status = "❌ NOT FOUND"

    check_results.append({
        'Target Column': target_name,
        'Detected Header': found_name,
        'Result': status
    })
# Create and display the report
report_df = pd.DataFrame(check_results)
print("--- Column Mapping Pre-Check ---")
display(report_df)
# Final Verification Logic
missing_mandatory = report_df[report_df['Result'] == "❌ NOT FOUND"]['Target Column'].tolist()
if not missing_mandatory:
    status_print("\nAll target columns are accounted for. Ready to proceed!")
else:
    status_print(f"\nError: The following Target Names could not be mapped: {missing_mandatory}")

cell_done("Column mapping pre-check completed")


# Find columns from the schema that are missing in the DataFrame.
# missing_columns = [col for col in expected_columns if col not in actual_columns]

# Report the findings.
#if missing_columns:
#    print("Warning: The following columns from the schema are not found in the DataFrame:")
#    for col in missing_columns:
#        print(f"- {col}")
#else:
#    print("All expected columns from the schema are present in the DataFrame.")



# ===== CELL 12 =====
df_cleaned_and_filtered.info()

# ===== CELL 13 =====
# Based on the 'Schema' defined above, rename the columns in the loaded DataFrame to match the standard column names defined in the schema.
# This will help ensure consistency in column naming for further analysis and processing.
# create a mapping from original column names to standard column names based on the schema, and then use this mapping to rename the columns in the DataFrame.
# Note: If there are multiple original column names mapping to the same standard column name, prioritize the first match found in the schema.
# Create a mapping from original column names to standard column names based on the schema
# when print out new column header information, also show corresponding old column header names for checking
column_mapping = {}
for standard_col, original_cols in schema.items():
    for original_col in original_cols:
        if original_col in df_cleaned_and_filtered.columns:
            column_mapping[original_col] = standard_col;
            break # Stop after the first match to prioritize the first found original column
# Rename the columns in the DataFrame using the mapping
df_cleaned_and_filtered = df_cleaned_and_filtered.rename(columns=column_mapping);
print("\nColumns after renaming based on schema:")
print(df_cleaned_and_filtered.columns.tolist());

# Display the column renaming map as a DataFrame for clearer side-by-side checking
column_mapping_df = pd.DataFrame(list(column_mapping.items()), columns=['Original Column', 'Standardized Column'])
print("\nColumn Renaming Map (Original Name -> Standardized Name):")
display(column_mapping_df);

df_cleaned_and_filtered.info()
cell_done("Columns renamed to the schema standard")

# ===== CELL 14 =====
# Assign "NA" if any of the columns used to generate 'Document_ID' have null values, to avoid issues in downstream processing.
# This way, we can still generate a 'Document_ID' even if some components are missing, and we can easily identify which ones had missing data.
# check null data in 'Project_Code', 'Facility_Code', 'Document_Type', 'Discipline', 'Document_Sequence_Number' which are used to generate 'Document_ID'
df_cleaned_and_filtered['Project_Code'] = df_cleaned_and_filtered['Project_Code'].fillna('NA')
df_cleaned_and_filtered['Facility_Code'] = df_cleaned_and_filtered['Facility_Code'].fillna('NA')
df_cleaned_and_filtered['Document_Type'] = df_cleaned_and_filtered['Document_Type'].fillna('NA')
df_cleaned_and_filtered['Discipline'] = df_cleaned_and_filtered['Discipline'].fillna('NA')
df_cleaned_and_filtered['Document_Sequence_Number'] = df_cleaned_and_filtered['Document_Sequence_Number'].fillna('NA')

# check 'Document_Sequence_Number value' one by one, if 'Document_Sequence_Number' data type in a cell is number,
# change it to str showing like 0001
df_cleaned_and_filtered['Document_Sequence_Number'] = df_cleaned_and_filtered['Document_Sequence_Number'].apply(lambda x: str(x).zfill(4) if str(x).isdigit() else str(x))


columns_to_check = ['Project_Code', 'Facility_Code', 'Document_Type', 'Discipline', 'Document_Sequence_Number']
for col in columns_to_check:
    num_nulls = df_cleaned_and_filtered[col].isnull().sum()
    if num_nulls > 0:
        status_print(f"There are {num_nulls} null values in the '{col}' column.")
        status_print(f"Rows with null '{col}' values:")
        debug_display(df_cleaned_and_filtered[df_cleaned_and_filtered[col].isnull()].head())
    else:
        status_print(f"No null values found in the '{col}' column.")

# Generate 'Document_ID' by concatenating the specified columns with a separator.
df_cleaned_and_filtered['Document_ID'] = (
    df_cleaned_and_filtered['Project_Code'].fillna('').astype(str) + '-' +
    df_cleaned_and_filtered['Facility_Code'].fillna('').astype(str) + '-' +
    df_cleaned_and_filtered['Document_Type'].fillna('').astype(str) + '-' +
    df_cleaned_and_filtered['Discipline'].fillna('').astype(str) + '-' +
    df_cleaned_and_filtered['Document_Sequence_Number'].fillna('').astype(str)
)

print("DataFrame after updating 'Document_ID' column:")
debug_display(df_cleaned_and_filtered.head())

# check if any null value in 'Document_ID'
num_null_doc_id = df_cleaned_and_filtered['Document_ID'].isnull().sum()

if num_null_doc_id > 0:
    status_print(f"There are {num_null_doc_id} null values in the 'Document_ID' column.")
    status_print("Rows with null 'Document_ID' values:")
    display(df_cleaned_and_filtered[df_cleaned_and_filtered['Document_ID'].isnull()])
else:
    status_print("No null values found in the 'Document_ID' column.")

cell_done("Document_ID updated")

# ===== CELL 15 =====
# check and update 'Submission_Session' and 'Submission_Session_Revision' per the follwoing conditions:
# forward fill for column 'Submission_Session'. Change 'Submission_Session' to string and format like '000001' etc.
# forward fill for column 'Submission_Session_Revision' per 'Submission_Session'. if still null after forward fill, assign 0 as default revision number.
# Change 'Submission_Session_Revision' to string and format like '00', '01', etc.
df_cleaned_and_filtered['Submission_Session'] = df_cleaned_and_filtered['Submission_Session'].ffill().astype(int).astype(str).str.zfill(6)
df_cleaned_and_filtered['Submission_Session_Revision'] = df_cleaned_and_filtered.groupby('Submission_Session')['Submission_Session_Revision'].ffill().fillna(0).astype(int).astype(str).str.zfill(2)
print("DataFrame after forward filling 'Submission_Session' and 'Submission_Session_Revision':")
debug_display(df_cleaned_and_filtered[['Submission_Session', 'Submission_Session_Revision']].head())

# check if there are still any null values in 'Submission_Session' and 'Submission_Session_Revision' after forward filling
num_null_submission_session = df_cleaned_and_filtered['Submission_Session'].isnull().sum()
num_null_submission_session_revision = df_cleaned_and_filtered['Submission_Session_Revision'].isnull().sum()
if num_null_submission_session > 0:
    status_print(f"There are {num_null_submission_session} null values in the 'Submission_Session' column after forward filling.")
    status_print("Rows with null 'Submission_Session' values:")
    display(df_cleaned_and_filtered[df_cleaned_and_filtered['Submission_Session'].isnull()])
else:
    status_print("No null values found in the 'Submission_Session' column after forward filling.")
if num_null_submission_session_revision > 0:
    status_print(f"There are {num_null_submission_session_revision} null values in the 'Submission_Session_Revision' column after forward filling.")
    status_print("Rows with null 'Submission_Session_Revision' values:")
    display(df_cleaned_and_filtered[df_cleaned_and_filtered['Submission_Session_Revision'].isnull()])
else:
    status_print("No null values found in the 'Submission_Session_Revision' column after forward filling.")

cell_done("Submission session fields updated")


# ===== CELL 16 =====
# Group by 'Document_ID' and aggregate unique 'Submission_Session' values (separated by "&&" if multiple).
df_submission_sessions = df_cleaned_and_filtered.groupby('Document_ID')['Submission_Session'].apply(lambda x: '&&'.join(x.unique())).reset_index()
df_submission_sessions = df_submission_sessions.rename(columns={'Submission_Session': 'All_Submission_Sessions'})
print("DataFrame with aggregated 'All_Submission_Session' values for each 'Document_ID':")
debug_display(df_submission_sessions.head())

# Check the number of unique 'Document_ID' before the merge
num_unique_doc_id_before_merge = df_cleaned_and_filtered['Document_ID'].nunique()

# Merge the aggregated 'Submission_Session' values back to the main DataFrame to have a comprehensive view of all_Submission_Sessions for each document.
df_cleaned_and_filtered = df_cleaned_and_filtered.merge(df_submission_sessions, on='Document_ID', how='left')
print("DataFrame after merging aggregated 'Submission_Session' values:")
debug_display(df_cleaned_and_filtered.head())

# Now we have a new column 'All_Submission_Sessions' that contains all unique Submission_Sessions for each document, separated by "&&". This will allow us to easily see all the Submission_Sessions associated with each document in one place.
#check if the merge caused any duplication of rows by comparing the number of unique 'Document_ID' before and after the merge.
num_unique_doc_id_after_merge = df_cleaned_and_filtered['Document_ID'].nunique()
if num_unique_doc_id_before_merge == num_unique_doc_id_after_merge:
    print("No duplication of rows after merging aggregated 'Submission_Session' values.")
else:
    status_print(f"Warning: The number of unique 'Document_ID' changed from {num_unique_doc_id_before_merge} to {num_unique_doc_id_after_merge} after merging, indicating potential duplication of rows.")

# check null values in the new column 'All_Submission_Sessions'
num_null_all_submission_sessions = df_cleaned_and_filtered['All_Submission_Sessions'].isnull().sum()
if num_null_all_submission_sessions > 0:
    status_print(f"There are {num_null_all_submission_sessions} null values in the 'All_Submission_Sessions' column after merging.")
    status_print("Rows with null 'All_Submission_Sessions' values:")
    display(df_cleaned_and_filtered[df_cleaned_and_filtered['All_Submission_Sessions'].isnull()])
else:
    status_print("No null values found in the 'All_Submission_Sessions' column after merging.")

cell_done("All submission sessions aggregated")

# ===== CELL 17 =====
# update 'Transmittal_Number' column per the followin rules:
# is NA if 'Transmittal_Number' is null, else
# is NA if 'Transmittal_Number'="N.A." or "N.A"

if 'Transmittal_Number' in df_cleaned_and_filtered.columns:
    # Convert column to string type to handle mixed data types consistently
    df_cleaned_and_filtered['Transmittal_Number'] = df_cleaned_and_filtered['Transmittal_Number'].astype(str)

    # Replace 'N.A.' or 'N.A' (and similar variations) with 'NA'
    df_cleaned_and_filtered['Transmittal_Number'] = df_cleaned_and_filtered['Transmittal_Number'].replace(['N.A.', 'N.A', 'nan'], 'NA', regex=False)

    # Fill any remaining nulls (which might be 'nan' strings after conversion, or actual NaN if not converted earlier)
    df_cleaned_and_filtered['Transmittal_Number'] = df_cleaned_and_filtered['Transmittal_Number'].fillna('NA')

    print("DataFrame after updating 'Transmittal_Number' column:")
    debug_display(df_cleaned_and_filtered[['Document_ID', 'Transmittal_Number']].head())

    # Check null data in 'Transmittal_Number'
    num_null_transmittal_number = df_cleaned_and_filtered['Transmittal_Number'].isnull().sum()
    if num_null_transmittal_number > 0:
        status_print(f"There are {num_null_transmittal_number} null values in the 'Transmittal_Number' column after updating.")
        status_print("Rows with null 'Transmittal_Number' values:")
        debug_display(df_cleaned_and_filtered[df_cleaned_and_filtered['Transmittal_Number'].isnull()].head())
    else:
        status_print("No null values found in the 'Transmittal_Number' column after updating.")
else:
    status_print("Column 'Transmittal_Number' not found. Skipping update for 'Transmittal_Number'.")

cell_done("Transmittal number update completed")

# ===== CELL 18 =====
# Check and convert 'Submission_Date' to datetime if not already in datetime format, coercing errors to NaT (Not a Time) for any non-convertible values. This will help ensure that the 'Submission_Date' column is in a consistent datetime format for further analysis and processing.
if not pd.api.types.is_datetime64_any_dtype(df_cleaned_and_filtered['Submission_Date']):
    df_cleaned_and_filtered['Submission_Date'] = pd.to_datetime(df_cleaned_and_filtered['Submission_Date'], errors='coerce')
    print("Converted 'Submission_Date' to datetime format, with non-convertible values set to NaT.")
else:
    print("'Submission_Date' is already in datetime format.")


# Forward fill missing 'Submission_Date' per 'Submission_Session' and 'Submission_Session_Revision', then per 'Submission_Session'.
if 'Submission_Session' in df_cleaned_and_filtered.columns and 'Submission_Session_Revision' in df_cleaned_and_filtered.columns:
    df_cleaned_and_filtered['Submission_Date'] = df_cleaned_and_filtered.groupby(['Submission_Session', 'Submission_Session_Revision'])['Submission_Date'].ffill()
    df_cleaned_and_filtered['Submission_Date'] = df_cleaned_and_filtered.groupby('Submission_Session')['Submission_Date'].ffill()
    print("Forward filled missing 'Submission_Date' values per 'Submission_Session' and 'Submission_Session_Revision', then per 'Submission_Session'.")
else:
    status_print("Columns 'Submission_Session' and/or 'Submission_Session_Revision' not found. Skipping forward fill for 'Submission_Date'.")

# Check how many null values remain in Submission_Date.
num_nulls_submission_date = df_cleaned_and_filtered['Submission_Date'].isna().sum()
status_print(f"After forward fill, 'Submission_Date' has {num_nulls_submission_date} null values.")

# print rows with null 'Submission_Date' to check if there are any patterns or issues with the data that might explain why these values are missing.
if num_nulls_submission_date > 0:
    status_print("Rows with null 'Submission_Date' after forward fill:")
    display(df_cleaned_and_filtered[df_cleaned_and_filtered['Submission_Date'].isna()])
else:
    status_print("No null values found in 'Submission_Date' after forward fill.")

cell_done("Submission date processing completed")


# ===== CELL 19 =====
# Find earlist 'Submission_Date' for each 'Document_ID' and store it in a new column 'First_Submittion_Date'.
df_cleaned_and_filtered['First_Submittion_Date'] = df_cleaned_and_filtered.groupby('Document_ID')['Submission_Date'].transform('min')
print("DataFrame after adding 'First_Submittion_Date' column with the earliest 'Submission_Date' for each 'Document_ID':")
debug_display(df_cleaned_and_filtered[['Document_ID', 'Submission_Date', 'First_Submittion_Date']].head(10))

# check if there are any null values in 'First_Submittion_Date' and print those rows to investigate potential data quality issues.
num_null_first_submission_date = df_cleaned_and_filtered['First_Submittion_Date'].isna().sum()
if num_null_first_submission_date > 0:
    status_print(f"There are {num_null_first_submission_date} null values in the 'First_Submittion_Date' column.")
    status_print("Rows with null 'First_Submittion_Date' values:")
    display(df_cleaned_and_filtered[df_cleaned_and_filtered['First_Submittion_Date'].isna()])
else:
    status_print("No null values found in the 'First_Submittion_Date' column.")

cell_done("First submission date added")


# ===== CELL 20 =====
# Find latest 'Submission_Date' for each 'Document_ID',
# and store it in a new column 'Latest_Submittion_Date'.

df_cleaned_and_filtered['Latest_Submittion_Date'] = df_cleaned_and_filtered.groupby('Document_ID')['Submission_Date'].transform('max')
print("DataFrame after adding 'Latest_Submittion_Date' column with the latest 'Submission_Date' for each 'Document_ID':")
debug_display(df_cleaned_and_filtered[['Document_ID', 'Submission_Date', 'Latest_Submittion_Date']].head(10))
# check if there are any null values in 'Latest_Submittion_Date' and print those rows to investigate potential data quality issues.
num_null_latest_submission_date = df_cleaned_and_filtered['Latest_Submittion_Date'].isna().sum()
if num_null_latest_submission_date > 0:
    status_print(f"There are {num_null_latest_submission_date} null values in the 'Latest_Submittion_Date' column.")
    status_print("Rows with null 'Latest_Submittion_Date' values:")
    display(df_cleaned_and_filtered[df_cleaned_and_filtered['Latest_Submittion_Date'].isna()])
else:
    status_print("No null values found in the 'Latest_Submittion_Date' column.")

cell_done("Latest submission date added")


# ===== CELL 21 =====
# check if 'Document_Revision' column exists before performing forward fill operations, and if it does,
# perform forward fill to ensure consistent revision information for each document per the following hierarchy:
# 1. Check "Document_Revision" Column, if null, forward fill "Document_Revision" Per "Document_ID", and "Submission_Session", and "Submission_Session_Revision".
# 2. Then forward fill per "Document_ID", and "Submission_Session"if still null after previous forward fill.
# 3. Then forward fill per "Document_ID" if still null after previous forward fills.
# 4. Then fill "NA" if still null after all forward fills.
# This will help ensure that the 'Document_Revision' column has consistent values for each document, even if some rows had missing revision information.
# After then we will check if there are still any null values in 'Document_Revision' and print those rows to investigate potential data quality issues.

if 'Document_Revision' in df_cleaned_and_filtered.columns:
    df_cleaned_and_filtered['Document_Revision'] = df_cleaned_and_filtered.groupby(['Document_ID', 'Submission_Session', 'Submission_Session_Revision'])['Document_Revision'].ffill()
    df_cleaned_and_filtered['Document_Revision'] = df_cleaned_and_filtered.groupby(['Document_ID', 'Submission_Session'])['Document_Revision'].ffill()
    df_cleaned_and_filtered['Document_Revision'] = df_cleaned_and_filtered.groupby('Document_ID')['Document_Revision'].ffill()
    df_cleaned_and_filtered['Document_Revision'] = df_cleaned_and_filtered['Document_Revision'].fillna("NA")
    print("Forward filled 'Document_Revision' column per the defined hierarchy.")
    # print the 'Document_ID', 'Submission_Session', 'Submission_Session_Revision', and 'Document_Revision' columns to check the results of the forward fill operations and ensure that the revision information is now consistent across the relevant groupings.
    print("DataFrame after forward filling 'Document_Revision':")
    debug_display(df_cleaned_and_filtered[['Document_ID', 'Submission_Session', 'Submission_Session_Revision', 'Document_Revision']].head())

    # Check if there are still any null values in 'Document_Revision' after forward filling and print those rows to investigate potential data quality issues.
    num_null_document_revision = df_cleaned_and_filtered['Document_Revision'].isna().sum()
    if num_null_document_revision > 0:
        status_print(f"There are {num_null_document_revision} null values in the 'Document_Revision' column after forward filling.")
        status_print("Rows with null 'Document_Revision' values:")
        display(df_cleaned_and_filtered[df_cleaned_and_filtered['Document_Revision'].isna()])
    else:
        status_print("No null values found in the 'Document_Revision' column after forward filling.")
else:
    status_print("Column 'Document_Revision' not found. Skipping forward fill for 'Document_Revision'.")

cell_done("Document revision update completed")


# ===== CELL 22 =====
# Find "Document_Revision" corresponding to the latest "Submission_Date" for each "Document_ID" and store it in a new column "Latest_Revision".
# if "Document_Revision" is "NA", check previouse 'Submission_Date' till a non "NA" found.
# if all "Document_Revision" for a "Document_ID" are "NA", then assign "NA" to "Latest_Revision".

df_sorted = df_cleaned_and_filtered.sort_values(['Document_ID', 'Submission_Date'], ascending=[True, False])
latest_rev_map = (
    df_sorted[df_sorted['Document_Revision'] != "NA"]
    .groupby('Document_ID')['Document_Revision']
    .first()
)
df_cleaned_and_filtered['Latest_Revision'] = (
    df_cleaned_and_filtered['Document_ID']
    .map(latest_rev_map)
    .fillna("NA") # If an ID has absolutely zero valid revisions
)
print("DataFrame after adding 'Latest_Revision' column with the Latest_Revision corresponding to the latest Submission_Date for each document:")
debug_display(df_cleaned_and_filtered[['Document_ID', 'Submission_Date', 'Document_Revision', 'Latest_Revision']].head(5))
# check if there are any null values in 'Latest_Revision' and print those rows to investigate potential data quality issues.
num_null_latest_revision = df_cleaned_and_filtered['Latest_Revision'].isna().sum()
if num_null_latest_revision > 0:
    status_print(f"There are {num_null_latest_revision} null values in the 'Latest_Revision' column.")
    status_print("Rows with null 'Latest_Revision' values:")
    display(df_cleaned_and_filtered[df_cleaned_and_filtered['Latest_Revision'].isna()])
else:
    status_print("No null values found in the 'Latest_Revision' column.")

cell_done("Latest revision added")





# ===== CELL 23 =====
# If the "Review_Status" column exists, then
# forward fill "Review_Status" per "Submission_Session" and "Submission_Session_Revision.
# if "Revsion Staus" is still null, fill pending_status.
# even 'Submission_Closed' is "YES", 'Review_Status' will be remained.
if 'Review_Status' in df_cleaned_and_filtered.columns:
    df_cleaned_and_filtered['Review_Status'] = df_cleaned_and_filtered.groupby(['Submission_Session', 'Submission_Session_Revision'])['Review_Status'].ffill()
    df_cleaned_and_filtered['Review_Status'] = df_cleaned_and_filtered['Review_Status'].fillna(pending_status)
    print(f"Forward filled 'Review_Status' per 'Submission_Session' and 'Submission_Session_Revision', and filled remaining nulls with '{pending_status}'.")
    # print the 'Submission_Session', 'Submission_Session_Revision', and 'Review_Status' columns to check the results of the forward fill operations and ensure that the Review_Status information is now consistent across the relevant groupings.
    print("DataFrame after forward filling 'Review_Status':")
    debug_display(df_cleaned_and_filtered[['Submission_Session', 'Submission_Session_Revision', 'Review_Status']].head(5))

    # Check if there are still any null values in 'Review_Status' after forward filling and print those rows to investigate potential data quality issues.
    num_null_review_status = df_cleaned_and_filtered['Review_Status'].isna().sum()
    if num_null_review_status > 0:
        status_print(f"There are {num_null_review_status} null values in the 'Review_Status' column after forward filling.")
        status_print("Rows with null 'Review_Status' values:")
        display(df_cleaned_and_filtered[df_cleaned_and_filtered['Review_Status'].isna()])
    else:
        status_print("No null values found in the 'Review_Status' column after forward filling.")
else:
    status_print("Column 'Review_Status' not found. Skipping forward fill for 'Review_Status'.")

cell_done("Review status update completed")

# ===== CELL 24 =====
# add 'Review_Status_Code' per 'Review_Status' and 'approval_code_mapping' which is defined above
df_cleaned_and_filtered['Review_Status_Code'] = df_cleaned_and_filtered['Review_Status'].map(approval_code_mapping)
print("DataFrame after adding 'Review_Status_Code' column:")
debug_display(df_cleaned_and_filtered[['Review_Status', 'Review_Status_Code']].head())

# check null value in 'Review Staus Code'
num_null_review_status_code = df_cleaned_and_filtered['Review_Status_Code'].isnull().sum()
if num_null_review_status_code > 0:
    status_print(f"There are {num_null_review_status_code} null values in the 'Review_Status_Code' column.")
    status_print("Rows with null 'Review_Status_Code' values:")
    display(df_cleaned_and_filtered[df_cleaned_and_filtered['Review_Status_Code'].isnull()])
else:
    status_print("No null values found in the 'Review_Status_Code' column.")

cell_done("Review status code added")

# ===== CELL 25 =====
# Define a custom aggregation function to get the latest non-pending_status status for each 'Document_ID'.
# add 'Latest_Approval_Status' Coumn to store the result for each 'Document_ID'.

# Map the columns first so 'Latest_Approval_Status' exists
# (Assuming 'Status' is the header in your Excel file)

df_cleaned_and_filtered['Latest_Approval_Status'] = df_cleaned_and_filtered['Review_Status']

# Pre-clean the status to handle backslashes and casing
df_cleaned_and_filtered['Latest_Approval_Status'] = (
    df_cleaned_and_filtered['Latest_Approval_Status']
    .astype(str)
    .str.replace(r'[\\/]', '', regex=True)
    .str.strip()
)

# NOW run your mapping logic
def get_latest_non_awaiting_status(group):
    # Sort the group by 'Submission_Date' in descending order to ensure 'latest' is at the top
    sorted_group = group.sort_values(by='Submission_Date', ascending=False)
    # Filter out the "Awaiting" rows from the sorted group
    valid_statuses = sorted_group[sorted_group['Latest_Approval_Status'] != pending_status]
    if not valid_statuses.empty:
        # Return the 'Latest_Approval_Status' from the top row (which is the latest non-pending)
        return valid_statuses.iloc[0]['Latest_Approval_Status']
    # If all statuses in the group are 'Awaiting S.O.'s response', return 'Awaiting S.O.'s response'
    return pending_status

latest_approval_status_map = (
    df_cleaned_and_filtered
    .groupby('Document_ID')
    .apply(get_latest_non_awaiting_status, include_groups=False)
.to_dict()
)

# Apply this custom aggregation to find the 'Latest_Approval_Status' for each 'Doc ID'
# BUG FIX: Changed from Submission_Session to Document_ID since the map keys are Document_IDs
df_cleaned_and_filtered['Latest_Approval_Status'] = df_cleaned_and_filtered['Document_ID'].map(latest_approval_status_map)

print(f"DataFrame after updating 'Latest_Approval_Status' column with non-'{pending_status}' values:")
debug_display(df_cleaned_and_filtered[['Submission_Session', 'Submission_Date', 'Review_Status', 'Latest_Approval_Status']].head())

#check if there are any null value in 'Latest_Approval_Status'.
num_null_latest_approval_status = df_cleaned_and_filtered['Latest_Approval_Status'].isna().sum()
if num_null_latest_approval_status > 0:
    status_print(f"There are {num_null_latest_approval_status} null values in the 'Latest_Approval_Status' column.")
else:
    status_print("No null values found in the 'Latest_Approval_Status' column.")
# print out 5 records for 'Latest Approval Stats' is null for checking
if num_null_latest_approval_status > 0:
    status_print("Rows with null 'Latest_Approval_Status' values:")
    debug_display(df_cleaned_and_filtered[df_cleaned_and_filtered['Latest_Approval_Status'].isna()].head())

cell_done("Latest approval status updated")

# ===== CELL 26 =====
# Calculate the number of submissions for each 'Document_ID'
submission_counts = df_cleaned_and_filtered.groupby('Document_ID')['Document_ID'].transform('count')

# Add the 'Count_of_Submissions' column
df_cleaned_and_filtered['Count_of_Submissions'] = submission_counts

print("DataFrame after adding 'Count_of_Submissions' column:")
debug_display(df_cleaned_and_filtered[['Document_ID', 'Count_of_Submissions']].head(5))

#check null data in 'Count_of_Submissions'
num_null_submission_counts = df_cleaned_and_filtered['Count_of_Submissions'].isnull().sum()
if num_null_submission_counts > 0:
    status_print(f"There are {num_null_submission_counts} null values in the 'Count_of_Submissions' column.")
    status_print("Rows with null 'Count_of_Submissions' values:")
    debug_display(df_cleaned_and_filtered[df_cleaned_and_filtered['Count_of_Submissions'].isnull()].head())
else:
    status_print("No null values found in the 'Count_of_Submissions' column.")

cell_done("Submission counts added")


# ===== CELL 27 =====
#check if 'Submitted_By' column exists before performing forward fill operations, and if it does,
#forward fill "Submitted_By" per "Submission_Session" and "Submission_Session_Revision", then per "Submission_Session".
# Then fill "NA" if still null after all forward fills.

if 'Submitted_By' not in df_cleaned_and_filtered.columns:
    df_cleaned_and_filtered['Submitted_By'] = 'NA' # Create the column with default 'NA' if it doesn't exist
    status_print("Column 'Submitted_By' not found in original data after renaming. Created with default 'NA' values.")
else:
    df_cleaned_and_filtered['Submitted_By'] = df_cleaned_and_filtered.groupby(['Submission_Session', 'Submission_Session_Revision'])['Submitted_By'].ffill()
    df_cleaned_and_filtered['Submitted_By'] = df_cleaned_and_filtered.groupby('Submission_Session')['Submitted_By'].ffill()
    #fill "NA" if "Submitted_By" is still null after forward fill
    df_cleaned_and_filtered['Submitted_By'] = df_cleaned_and_filtered['Submitted_By'].fillna('NA')
    print("DataFrame after forward-filling 'Submitted_By' column:")

debug_display(df_cleaned_and_filtered[['Document_ID', 'Submitted_By']].head())
# check null data in 'Submitted_By'
num_null_submitted_By = df_cleaned_and_filtered['Submitted_By'].isnull().sum()
if num_null_submitted_By > 0:
    status_print(f"There are {num_null_submitted_By} null values in the 'Submitted_By' column.")
    status_print("Rows with null 'Submitted_By' values:")
    debug_display(df_cleaned_and_filtered[df_cleaned_and_filtered['Submitted_By'].isnull()].head())
else:
    status_print("No null values found in the 'Submitted_By' column.")

cell_done("Submitted_By update completed")

# ===== CELL 28 =====
# Check if 'Submission_Session_Subject' column exists before performing forward fill operations, and if it does,
# perform forward fill per 'Submission_Session' and 'Submission_Session_Revision', then per 'Submission_Session'.

if 'Submission_Session_Subject' in df_cleaned_and_filtered.columns:
    df_cleaned_and_filtered['Submission_Session_Subject'] = df_cleaned_and_filtered.groupby(['Submission_Session', 'Submission_Session_Revision'])['Submission_Session_Subject'].ffill()
    df_cleaned_and_filtered['Submission_Session_Subject'] = df_cleaned_and_filtered.groupby('Submission_Session')['Submission_Session_Subject'].ffill()

print("DataFrame after grouped forward-filling 'Submission_Session_Subject' column:")
debug_display(df_cleaned_and_filtered[['Document_ID', 'Submission_Session', 'Submission_Session_Revision', 'Submission_Session_Subject']].head())

# check null data in 'Submission_Session_Subject'
num_null_document_title = df_cleaned_and_filtered['Submission_Session_Subject'].isnull().sum()
if num_null_document_title > 0:
    status_print(f"There are {num_null_document_title} null values in the 'Submission_Session_Subjecte' column.")
    status_print("Rows with null 'Submission_Session_Subject' values:")
    debug_display(df_cleaned_and_filtered[df_cleaned_and_filtered['Submission_Session_Subject'].isnull()].head())
else:
    status_print("No null values found in the 'Submission_Session_Subject' column.")

cell_done("Submission session subject updated")


# ===== CELL 29 =====

# Group by 'Submission_Session_Subject' and aggregate unique 'Submission_Session_Subject' values (separated by " && " if multiple). Enclose each title in double quotes.
# Enclose each individual title in double quotes before joining them
# Store the result in a new column 'Consolidated_Submission_Session_Subject'

consolidated_Subject_title = df_cleaned_and_filtered.groupby('Document_ID')['Submission_Session_Subject'].agg(lambda x: ' && '.join([f'"{item}"' for item in x.dropna().astype(str).unique().tolist()])).reset_index()
consolidated_Subject_title.rename(columns={'Submission_Session_Subject': 'Consolidated_Submission_Session_Subject'}, inplace=True)

# Merge this back into the main DataFrame
df_cleaned_and_filtered = pd.merge(
    df_cleaned_and_filtered,
    consolidated_Subject_title,
    on='Document_ID',
    how='left'
)

print("DataFrame after updating 'Consolidated_Submission_Session_Subject' column:")
debug_display(df_cleaned_and_filtered[['Document_ID', 'Consolidated_Submission_Session_Subject', ]].head())

# check null data in 'Consolidated_Submission_Session_Subject' after consolidation
num_null_document_title = df_cleaned_and_filtered['Consolidated_Submission_Session_Subject'].isnull().sum()
if num_null_document_title > 0:
    status_print(f"There are {num_null_document_title} null values in the 'Consolidated_Submission_Session_Subject' column after consolidation.")
else:
    status_print("No null values found in the 'Consolidated_Submission_Session_Subject' column after consolidation.")

cell_done("Consolidated submission subject added")



# ===== CELL 30 =====
#check if 'Review_Return_Actual_Date' column exists before performing forward fill operations, and if it does,
# Ensure 'Review_Return_Actual_Date' is in datetime format for proper forward-filling




# (It's already datetime64[ns] according to info, but good to ensure if it was changed in prior steps)
if 'Review_Return_Actual_Date' in df_cleaned_and_filtered.columns:
    df_cleaned_and_filtered['Review_Return_Actual_Date'] = pd.to_datetime(df_cleaned_and_filtered['Review_Return_Actual_Date'], errors='coerce')

    # Convert 'Submission_Session_Revision' to string for consistent grouping, handling potential floats/NaT
    df_cleaned_and_filtered['Submission_Session_Revision'] = df_cleaned_and_filtered['Submission_Session_Revision'].astype(str)

    # Forward fill 'Review_Return_Actual_Date' based on 'Submission_Session' and 'Submission_Session_Revision'
    df_cleaned_and_filtered['Review_Return_Actual_Date'] = df_cleaned_and_filtered.groupby(
        ['Submission_Session', 'Submission_Session_Revision']
        )['Review_Return_Actual_Date'].ffill()

    print("DataFrame after grouped forward-filling 'Review_Return_Actual_Date':")
    debug_display(df_cleaned_and_filtered[['Document_ID', 'Submission_Session', 'Submission_Session_Revision', 'Review_Return_Actual_Date']].head())
    # Check null data in 'Review_Return_Actual_Date' after forward fill
    num_null_review_return_actual_date = df_cleaned_and_filtered['Review_Return_Actual_Date'].isnull().sum()
    if num_null_review_return_actual_date > 0:
        status_print(f"There are {num_null_review_return_actual_date} null values in the 'Review_Return_Actual_Date' column after forward filling.")
        status_print("Rows with null 'Review_Return_Actual_Date' values:")
        debug_display(df_cleaned_and_filtered[df_cleaned_and_filtered['Review_Return_Actual_Date'].isnull()].head())
    else:
        status_print("No null values found in the 'Review_Return_Actual_Date' column after forward filling.")
else:
    status_print("Column 'Review_Return_Actual_Date' is already in datetime format. Skipping conversion and forward fill for 'Review_Return_Actual_Date'.")

cell_done("Review return actual date update completed")



# ===== CELL 31 =====
# Get apporval code from 'Latest_Approval_Status' column per 'approval_code_mapping' above , and store it in a new column 'Latest_Approval_Code'.
# update 'Submission_Closed' column per the following conditoins:
# change data in 'Submission_Closed' to capital letters and fill null with "NO",
# If 'Submission_Closed'=='YES', then 'Submission_Closed'=="YES', otherwise,
# if 'Latest_Approval_Code' is "APP' or 'VOID' or 'INF', then 'Submission_Closed' == "YES", otherwise "NO"

# Map 'Latest_Approval_Status' to 'Latest_Approval_Code' using the provided mapping
# Remove '/' from value
df_cleaned_and_filtered['Latest_Approval_Status'] = (df_cleaned_and_filtered['Latest_Approval_Status']
    .str.replace('/', '', regex=False)
    .str.strip()
)
df_cleaned_and_filtered['Latest_Approval_Code'] = df_cleaned_and_filtered['Latest_Approval_Status'].map(approval_code_mapping)
# Update 'Submission_Closed' column based on the specified conditions
df_cleaned_and_filtered['Submission_Closed'] = df_cleaned_and_filtered['Submission_Closed'].str.upper().fillna("NO")
df_cleaned_and_filtered['Submission_Closed'] = df_cleaned_and_filtered.apply(
    lambda row: "YES" if row['Submission_Closed'] == "YES" else ("YES" if row['Latest_Approval_Code'] in ["APP", "VOID", "INF"] else "NO"),
    axis=1
)
print("DataFrame after adding 'Latest_Approval_Code' column and updating 'Submission_Closed' column:")
debug_display(df_cleaned_and_filtered[['Document_ID', 'Latest_Approval_Status', 'Latest_Approval_Code', 'Submission_Closed']].head())
# check null data in 'Latest_Approval_Code'
num_null_latest_approval_code = df_cleaned_and_filtered['Latest_Approval_Code'].isnull().sum()
if num_null_latest_approval_code > 0:
    status_print(f"There are {num_null_latest_approval_code} null values in the 'Latest_Approval_Code' column.")
    status_print("Rows with null 'Latest_Approval_Code' values:")
    debug_display(df_cleaned_and_filtered[df_cleaned_and_filtered['Latest_Approval_Code'].isnull()].head())
else:
    status_print("No null values found in the 'Latest_Approval_Code' column.")
# check null data in 'Submission_Closed'
num_null_submission_closed = df_cleaned_and_filtered['Submission_Closed'].isnull().sum()
if num_null_submission_closed > 0:
    status_print(f"There are {num_null_submission_closed} null values in the 'Submission_Closed' column.")
    status_print("Rows with null 'Submission_Closed' values:")
    debug_display(df_cleaned_and_filtered[df_cleaned_and_filtered['Submission_Closed'].isnull()].head())
else:
    status_print("No null values found in the 'Submission_Closed' column.")

cell_done("Latest approval code and submission closed fields updated")






# ===== CELL 32 =====
#list down unique values in 'Latest_Approval_Status'
unique_latest_approval_status = df_cleaned_and_filtered['Latest_Approval_Status'].unique()
print("Unique values in 'Latest_Approval_Status':")
for status in unique_latest_approval_status:
    print(status)

cell_done("Latest approval status values reviewed")

# ===== CELL 33 =====
# Update 'Resubmission_Plan_Date' column based on the following conditions:
# if duration_is_working_day = True, then calculate 'Resubmission_Plan_Date' based on working days, otherwise calculate it based on calendar days.
# if 'Submission_Closed' is 'YES', then 'Resubmission_Plan_Date' should be null, otherwise,
# if 'Review_Return_Actual_Date' is not Null, then 'Resubmission_Plan_Date' == 'Review_Return_Actual_Date' plus 14 days (working or calendar); otherwise,
# if 'Latest Submission_Date'=='Date Submit', then 'Resubmission_Plan_Date' == 'Date Submit' plus 34 days (working or calendar); otherwise
# 'Resubmission_Plan_Date' == 'Date Submit' plus 28 days (working or calendar).
# check Null in 'Resubmission_Plan_Date' after updating


# check if duration_is_working_day = True, 'offset' is BDay, otherwise 'offset' is per canlendar day
if duration_is_working_day:
    def calculate_resubmission_plan_date(row):
        if row['Submission_Closed'] == "YES":
            return pd.NaT
        elif pd.notna(row['Review_Return_Actual_Date']):
            return row['Review_Return_Actual_Date'] + pd.offsets.BDay(resubmission_duration)
        elif row['Latest_Submittion_Date'] == row['Submission_Date']:
            return row['Submission_Date'] + pd.offsets.BDay(first_review_duration+resubmission_duration)
        else:
            return row['Submission_Date'] + pd.offsets.BDay(second_review_duration+resubmission_duration)
else:
    def calculate_resubmission_plan_date(row):
        if row['Submission_Closed'] == "YES":
            return pd.NaT
        elif pd.notna(row['Review_Return_Actual_Date']):
            return row['Review_Return_Actual_Date'] + pd.Timedelta(days=resubmission_duration)
        elif row['Latest_Submittion_Date'] == row['Submission_Date']:
            return row['Submission_Date'] + pd.Timedelta(days=first_review_duration+resubmission_duration)
        else:
            return row['Submission_Date'] + pd.Timedelta(days=second_review_duration+resubmission_duration)

# update 'Resubmission_Plan_Date' column
df_cleaned_and_filtered['Resubmission_Plan_Date'] = df_cleaned_and_filtered.apply(calculate_resubmission_plan_date, axis=1)
print("DataFrame after updating 'Resubmission_Plan_Date' column:")
debug_display(df_cleaned_and_filtered[['Document_ID', 'Submission_Closed', 'Review_Return_Actual_Date', 'Latest_Submittion_Date', 'Submission_Date', 'Resubmission_Plan_Date']].head())

# Check null data in 'Resubmission_Plan_Date' after calculation
num_null_resubmission_plan_date = df_cleaned_and_filtered['Resubmission_Plan_Date'].isnull().sum()
if num_null_resubmission_plan_date > 0:
    status_print(f"There are {num_null_resubmission_plan_date} null values in the 'Resubmission_Plan_Date' column after calculation.")
    status_print("Rows with null 'Resubmission_Plan_Date' values:")
    debug_display(df_cleaned_and_filtered[df_cleaned_and_filtered['Resubmission_Plan_Date'].isnull()].head())
else:
    status_print("No null values found in the 'Resubmission_Plan_Date' column after calculation.")

cell_done("Resubmission plan date updated")





# ===== CELL 34 =====
# fill up "" if 'Notes' is null
df_cleaned_and_filtered['Notes'] = df_cleaned_and_filtered['Notes'].fillna("")
print("DataFrame after filling null values in 'Notes' column with empty strings:")
debug_display(df_cleaned_and_filtered[['Document_ID', 'Notes']].head())
cell_done("Notes column cleaned")

# ===== CELL 35 =====
# 'Resubmission_Overdue_Status' == "Resubmitted" if 'Review_Return_Actual_Date' is not null, Otherwise
# 'Resubmission_Overdue_Status' == "Overdue" if 'Submission_Closed' is not 'YES', and 'Resubmission_Plan_Date' is before today,
# otherwise "NO"

def calculate_overdue_status(row):
    if pd.notnull(row['Review_Return_Actual_Date']):
        return "Resubmitted"
    elif row['Submission_Closed'] != 'YES' and pd.notnull(row['Resubmission_Plan_Date']) and row['Resubmission_Plan_Date'] < datetime.now():
        return "Overdue"
    else:
        return "NO"
df_cleaned_and_filtered['Resubmission_Overdue_Status'] = df_cleaned_and_filtered.apply(calculate_overdue_status, axis=1)
print("DataFrame after updating 'Resubmission_Overdue_Status' column:")
debug_display(df_cleaned_and_filtered[['Document_ID', 'Review_Return_Actual_Date', 'Submission_Closed', 'Resubmission_Plan_Date', 'Resubmission_Overdue_Status']].head())
# check null data in 'Resubmission_Overdue_Status' column
num_null_overdue_status = df_cleaned_and_filtered['Resubmission_Overdue_Status'].isnull().sum()
if num_null_overdue_status > 0:
    status_print(f"There are {num_null_overdue_status} null values in the 'Resubmission_Overdue_Status' column.")
    status_print("Rows with null 'Resubmission_Overdue_Status' values:")
    debug_display(df_cleaned_and_filtered[df_cleaned_and_filtered['Resubmission_Overdue_Status'].isnull()].head())
else:
    status_print("No null values found in the 'Resubmission_Overdue_Status' column.")

cell_done("Resubmission overdue status updated")



# ===== CELL 36 =====
# update 'Resubmission_Required' column based on the following conditions:
# if 'Resubmission_Required'=='NO', then 'Resubmission_Required'=='NO', otherwise
# if 'Submission_Closed'=='YES', then 'Resubmission_Required'=="NO", otherwise 'YES'.

def update_resubmission_required(row):
    if row['Resubmission_Required'] == 'NO':
        return "NO"
    elif row['Submission_Closed'] == 'YES':
        return "NO"
    else:
        return "YES"
df_cleaned_and_filtered['Resubmission_Required'] = df_cleaned_and_filtered.apply(update_resubmission_required, axis=1)
print("DataFrame after updating 'Resubmission_Required' column:")
debug_display(df_cleaned_and_filtered[['Document_ID', 'Submission_Closed', 'Resubmission_Required']].head())
# check null data in 'Resubmission_Required' column
num_null_resubmission_required = df_cleaned_and_filtered['Resubmission_Required'].isnull().sum()
if num_null_resubmission_required > 0:
    status_print(f"There are {num_null_resubmission_required} null values in the 'Resubmission_Required' column.")
    status_print("Rows with null 'Resubmission_Required' values:")
    debug_display(df_cleaned_and_filtered[df_cleaned_and_filtered['Resubmission_Required'].isnull()].head())
else:
    status_print("No null values found in the 'Resubmission_Required' column.")

cell_done("Resubmission required flag updated")


# ===== CELL 37 =====
# update 'Delay_of_Resubmission' column based on the following conditions:
# if 'Submission_Closed'=='YES', then 'Delay_of_Resubmission'==0, otherwise,
# if previous 'Submission_Date' for the same 'Document_ID' exists, then 'Delay_of_Resubmission' is the difference between 'Submission_Date' in the current row and the latest previous 'Resubmission_Plan_Date' for the same 'Document_ID'. Ensure no negative values, if the calculated delay is negative, set it to 0. Otherwise,
# 'Delay_of_Resubmission' is 0 since there is no previous submission to compare with.
# check  null data in 'Delay_of_Resubmission' column after calculation.
# notes: for the calculation of delay of resubmission, we will compare the 'Submission_Date' with the latest previous 'Resubmission_Plan_Date' instead of 'Submission_Date' because 'Resubmission_Plan_Date' represents the planned date for resubmission, which is more relevant for calculating the delay in resubmission. Comparing with the latest previous 'Submission_Date' may not accurately reflect the intended resubmission timeline, especially if there are multiple submissions for the same document. By using 'Resubmission_Plan_Date', we can better assess whether the current submission is delayed based on the planned resubmission schedule.
# notes: if there are multiple previous submissions for the same 'Document_ID', we will consider the latest previous 'Resubmission_Plan_Date' for the delay calculation, as it represents the most recent planned resubmission date that the current submission should be compared against to determine if there is a delay.
# notes: if there is no previous submission for the same 'Document_ID', we will set 'Delay_of_Resubmission' to 0, as there is no prior submission to compare with for calculating the delay.
# notes: if 'Submission_Closed' is 'YES', we will set 'Delay_of_Resubmission' to 0, as the submission is already closed and there is no delay to calculate for resubmission.
# notes: find previous submissions for the same 'Document_ID' based on submission date, not per previous row.

def calculate_delay_of_resubmission(row, df_for_lookup):
    if row['Submission_Closed'] == 'YES':
        return 0
    
    # Check for previous submissions for the same Document_ID (based on submission date)
    same_doc_rows = df_for_lookup[df_for_lookup['Document_ID'] == row['Document_ID']]
    
    # Filter for submissions with earlier submission dates
    if pd.notna(row['Submission_Date']):
        previous_submissions = same_doc_rows[
            (same_doc_rows['Submission_Date'] < row['Submission_Date']) & 
            (pd.notna(same_doc_rows['Submission_Date']))
        ]
        
        if not previous_submissions.empty:
            # Get latest previous Resubmission_Plan_Date
            valid_previous = previous_submissions[pd.notna(previous_submissions['Resubmission_Plan_Date'])]
            if not valid_previous.empty:
                latest_previous_resubmission_date = valid_previous['Resubmission_Plan_Date'].max()
                delay = (row['Submission_Date'] - latest_previous_resubmission_date).days
                return max(delay, 0)  # Ensure delay is not negative
    
    # No previous submission exists, set delay to 0
    return 0

df_cleaned_and_filtered['Delay_of_Resubmission'] = df_cleaned_and_filtered.apply(
    lambda row: calculate_delay_of_resubmission(row, df_cleaned_and_filtered), axis=1
)
print("DataFrame after updating 'Delay_of_Resubmission' column:")
debug_display(df_cleaned_and_filtered[['Document_ID', 'Submission_Closed', 'Submission_Date', 'Resubmission_Plan_Date', 'Delay_of_Resubmission']].head())
# check null data in 'Delay_of_Resubmission' column after calculation
num_null_delay_of_resubmission = df_cleaned_and_filtered['Delay_of_Resubmission'].isnull().sum()
if num_null_delay_of_resubmission > 0:
    status_print(f"There are {num_null_delay_of_resubmission} null values in the 'Delay_of_Resubmission' column.")
    status_print("Rows with null 'Delay_of_Resubmission' values:")
    debug_display(df_cleaned_and_filtered[df_cleaned_and_filtered['Delay_of_Resubmission'].isnull()].head())
else:
    status_print("No null values found in the 'Delay_of_Resubmission' column.")

cell_done("Delay of resubmission calculated")

# ===== CELL 38 =====
# update 'Department' column, use forward filling, per 'Submission_Session' and 'Submission_Session_Revision' as reference first;
# and then use 'Submission_Session' as reference for forward filling;
# and assign 'NA' finally.
# Check null data in 'Department' column after forward filling.
if 'Department' in df_cleaned_and_filtered.columns:
    df_cleaned_and_filtered['Department'] = df_cleaned_and_filtered.groupby(['Submission_Session', 'Submission_Session_Revision'])['Department'].ffill()
    df_cleaned_and_filtered['Department'] = df_cleaned_and_filtered.groupby('Submission_Session')['Department'].ffill()
    df_cleaned_and_filtered['Department'] = df_cleaned_and_filtered['Department'].fillna("NA")
    print("DataFrame after forward-filling 'Department' column:")
    debug_display(df_cleaned_and_filtered[['Document_ID', 'Submission_Session', 'Submission_Session_Revision', 'Department']].head())

    # Check null data in 'Department' column after forward filling
    num_null_department = df_cleaned_and_filtered['Department'].isnull().sum()
    if num_null_department > 0:
        status_print(f"There are {num_null_department} null values in the 'Department' column after forward filling.")
        status_print("Rows with null 'Department' values:")
        debug_display(df_cleaned_and_filtered[df_cleaned_and_filtered['Department'].isnull()].head())
    else:
        status_print("No null values found in the 'Department' column after forward filling.")
else:
    status_print("Column 'Department' not found. Skipping forward fill for 'Department'.")

cell_done("Department update completed")




# ===== CELL 39 =====
# Update 'Review_Comments', use forward filling, per 'Submission_Session' and 'Submission_Session_Revision' as reference first;
# and then use 'Submission_Session' as reference for forward filling;
# and assign 'NA' finally.
# Check null data in 'Review_Comments' column after forward filling.
if 'Review_Comments' in df_cleaned_and_filtered.columns:
    df_cleaned_and_filtered['Review_Comments'] = df_cleaned_and_filtered.groupby(['Submission_Session', 'Submission_Session_Revision'])['Review_Comments'].ffill()
    df_cleaned_and_filtered['Review_Comments'] = df_cleaned_and_filtered.groupby('Submission_Session')['Review_Comments'].ffill()
    df_cleaned_and_filtered['Review_Comments'] = df_cleaned_and_filtered['Review_Comments'].fillna("NA")
    print("DataFrame after forward-filling 'Review_Comments' column:")
    debug_display(df_cleaned_and_filtered[['Document_ID', 'Submission_Session', 'Submission_Session_Revision', 'Review_Comments']].head())

    # Check null data in 'Review_Comments' column after forward filling
    num_null_review_comments = df_cleaned_and_filtered['Review_Comments'].isnull().sum()
    if num_null_review_comments > 0:
        status_print(f"There are {num_null_review_comments} null values in the 'Review_Comments' column after forward filling.")
        status_print("Rows with null 'Review_Comments' values:")
        debug_display(df_cleaned_and_filtered[df_cleaned_and_filtered['Review_Comments'].isnull()].head())
    else:
        status_print("No null values found in the 'Review_Comments' column after forward filling.")
else:
    status_print("Column 'Review_Comments' not found. Skipping forward fill for 'Review_Comments'.")

cell_done("Review comments update completed")






# ===== CELL 40 =====
# Make sure 'Review_Return_Actual_Date', 'Submission_Date', and 'Resubmission_Plan_Date' are in datetime format for proper calculation of working day differences.
# update 'Duration_of_Review' column based on the following conditions:
# if 'Review_Return_Actual_Date' is not null, then calculate the working day difference between 'Review_Return_Actual_Date' and 'Submission_Date', otherwise,
# the working day differenc between today and 'Submission_Date'. Ensure that the calculated variance is not negative.
# check null data in 'Duration_of_Review' column after calculation.

# 1. Convert columns to datetime objects
date_cols = ['Review_Return_Actual_Date', 'Submission_Date', 'Resubmission_Plan_Date']
for col in date_cols:
    df_cleaned_and_filtered[col] = pd.to_datetime(df_cleaned_and_filtered[col])

# 2. Prepare the End Dates
# Use 'Review_Return_Actual_Date' if available, otherwise use Today
today = np.datetime64(datetime.now().date())
end_dates = df_cleaned_and_filtered['Review_Return_Actual_Date'].fillna(today)

# 3. Create the NumPy arrays for business day calculation
# We convert to 'datetime64[D]' format which np.busday_count requires
start_arr = df_cleaned_and_filtered['Submission_Date'].values.astype('datetime64[D]')
end_arr = end_dates.values.astype('datetime64[D]')

# 4. Create a "Mask" to handle Nulls (NaT)
# This prevents the TypeError by ensuring we only process rows where both dates exist
valid_mask = ~np.isnat(start_arr) & ~np.isnat(end_arr)

# 5. Initialize the Duration column with 0 or NaN
durations = np.zeros(len(df_cleaned_and_filtered))

# 6. Perform the calculation only on valid rows
# np.where ensures that if start > end (negative result), it returns 0
if valid_mask.any():
    raw_counts = np.busday_count(start_arr[valid_mask], end_arr[valid_mask])
    durations[valid_mask] = np.maximum(raw_counts, 0)

# 7. Assign back to DataFrame
df_cleaned_and_filtered['Duration_of_Review'] = durations

# 8. Set Duration to NaN where the Submission_Date was missing (Optional but recommended)
df_cleaned_and_filtered.loc[~valid_mask, 'Duration_of_Review'] = np.nan


print("DataFrame after updating 'Duration_of_Review' column:")
debug_display(df_cleaned_and_filtered[['Document_ID', 'Submission_Date', 'Review_Return_Actual_Date', 'Duration_of_Review']].head())
# check null data in 'Duration_of_Review' column after calculation
num_null_duration_of_review = df_cleaned_and_filtered['Duration_of_Review'].isnull().sum()
if num_null_duration_of_review > 0:
    status_print(f"There are {num_null_duration_of_review} null values in the 'Duration_of_Review' column.")
    status_print("Rows with null 'Duration_of_Review' values:")
    debug_display(df_cleaned_and_filtered[df_cleaned_and_filtered['Duration_of_Review'].isnull()].head())
else:
    status_print("No null values found in the 'Duration_of_Review' column.")

cell_done("Duration of review calculated")



# ===== CELL 41 =====
# for each non-date column, add "'" at the beginning of all values
#non_date_columns = df_cleaned_and_filtered.select_dtypes(exclude=['datetime64[ns]']).columns
#df_cleaned_and_filtered[non_date_columns] = df_cleaned_and_filtered[non_date_columns].astype(str)
#df_cleaned_and_filtered[non_date_columns] = df_cleaned_and_filtered[non_date_columns].apply(lambda x: "'" + x + "'")
#
#print("DataFrame after adding single quotes to non-date columns:")
#display(df_cleaned_and_filtered[non_date_columns].head())



# ===== CELL 42 =====
# df_cleaned_and_filtered = df_cleaned_and_filtered.reset_index()
df_cleaned_and_filtered.info()

# summary null value after all the updating and filling
status_print("Summary of null values in each column after all updates and filling:")
null_summary = df_cleaned_and_filtered.isnull().sum()
status_print(null_summary)
cell_done("Final dataframe validation summary prepared")


# ===== CELL 43 =====
output_file_name = 'Processed_Submittal_Tracker.xlsx'

# Always save the file first (creates it in the current working directory)
df_cleaned_and_filtered.to_excel(output_file_name, index=False)

# Construct the full path where the file *would be* in the download_file_path directory
destination_full_path = os.path.join(download_file_path, output_file_name)

# Environment-specific feedback and actions
if is_colab:
    status_print(f"DataFrame successfully saved to '{output_file_name}' in Colab.")
    status_print("A download prompt will appear shortly.")
    # Download to local machine via Colab's file download mechanism
    files.download(output_file_name)

    # Ensure the download_file_path directory exists
    os.makedirs(download_file_path, exist_ok=True)

    # Compare absolute paths to avoid SameFileError
    if os.path.abspath(output_file_name) == destination_full_path and not overwrite_existing_downloads:
        status_print(f"The file '{output_file_name}' is already at the destination '{download_file_path}'. Skipping redundant copy.")
    elif os.path.exists(destination_full_path) and not overwrite_existing_downloads:
        status_print(f"File '{output_file_name}' already exists at '{download_file_path}'. Overwrite is disabled, skipping copy.")
    else:
        shutil.copy(output_file_name, download_file_path)
        status_print(f"The file '{output_file_name}' has been copied to '{download_file_path}'.")
else: # Local environment
    status_print(f"DataFrame successfully saved to '{output_file_name}' in your local directory.")

    # Ensure the download_file_path directory exists
    os.makedirs(download_file_path, exist_ok=True)

    # Compare absolute paths to avoid SameFileError
    if os.path.abspath(output_file_name) == destination_full_path and not overwrite_existing_downloads:
        status_print(f"The file '{output_file_name}' is already at the destination '{download_file_path}'. Skipping redundant copy.")
    elif os.path.exists(destination_full_path) and not overwrite_existing_downloads:
        status_print(f"File '{output_file_name}' already exists at '{download_file_path}'. Overwrite is disabled, skipping copy.")
    else:
        shutil.copy(output_file_name, download_file_path)
        status_print(f"The file '{output_file_name}' has been copied to '{download_file_path}'.")

# ===== CELL 44 =====
# export data frame to DuctDB

db_file_name = 'Processed_Submittal_Tracker.duckdb'
table_name = 'Processed_Submittal_Tracker'

# Construct the full path for the DuckDB file
db_full_path = os.path.join(download_file_path, db_file_name)

# Standardize column names (removes spaces/special chars that SQL hates)
df_cleaned_and_filtered.columns = [c.replace(' ', '_').replace('.', '').strip() for c in df_cleaned_and_filtered.columns]

# Connect to DuckDB (creates the file if it doesn't exist)
con = duckdb.connect(database=db_full_path, read_only=False)

# Fix the "Object/Str" issue for DuckDB (ensure string columns are consistent)
for col in df_cleaned_and_filtered.columns:
    # Convert 'object' types (mixed text/numbers) to string
    if df_cleaned_and_filtered[col].dtype == 'object':
        df_cleaned_and_filtered[col] = df_cleaned_and_filtered[col].astype(str)

    # Replace the literal string "nan" with an actual empty string
    df_cleaned_and_filtered[col] = df_cleaned_and_filtered[col].replace('nan', '', regex=False)

# Register the Pandas DataFrame as a view in DuckDB
con.register('df_cleaned_and_filtered_view', df_cleaned_and_filtered)

# Create or Replace the table in DuckDB from the registered view
con.execute(f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM df_cleaned_and_filtered_view")

status_print(f"Successfully updated DuckDB table: {table_name}")

# Get table header information
columns_info = con.execute(f"PRAGMA table_info('{table_name}')").fetchdf()
print(f"\nTable '{table_name}' header information:")
for index, row in columns_info.iterrows():
    print(f"- {row['name']} ({row['type']})")

# Close the connection
con.close()

status_print(f"\nDataFrame successfully exported to DuckDB file '{db_full_path}' as table '{table_name}'.")

# ===== CELL 45 =====
# download DuctDB file to local Download folder and download_file_path folder
db_file_name = 'Processed_Submittal_Tracker.duckdb'
db_full_path = os.path.join(download_file_path, db_file_name)

# download to local Download folder
if is_colab:
    status_print(f"Downloading '{db_full_path}' to local Download folder...")
    files.download(db_full_path)
    status_print(f"The DuckDB file '{db_full_path}' is ready for download.")
else:
    status_print(f"The DuckDB file '{db_full_path}' has already been saved to '{download_file_path}'.")


# ===== CELL 46 =====
df_cleaned_and_filtered['Submission_Date'] = pd.to_datetime(df_cleaned_and_filtered['Submission_Date'], errors='coerce')
df_cleaned_and_filtered['Review_Return_Actual_Date'] = pd.to_datetime(df_cleaned_and_filtered['Review_Return_Actual_Date'], errors='coerce')
df_cleaned_and_filtered['Submission Month-Year'] = df_cleaned_and_filtered['Submission_Date'].dt.to_period('M')

print("DataFrame after converting 'Submission_Date' and 'Review_Return_Actual_Date' to datetime and adding 'Submission Month-Year':")
debug_display(df_cleaned_and_filtered[['Submission_Date', 'Review_Return_Actual_Date', 'Submission Month-Year', 'Latest_Approval_Code']].head())
cell_done("Monthly reporting dates prepared")

# ===== CELL 47 =====
output_monthly_excel_filename = 'Monthly Submission.xlsx'

# Define the columns for the monthly report
columns_for_monthly_report = [
    'Submission_Session',
    'Submission_Session_Subject',
    'Consolidated_Submission_Session_Subject',
    'Submission_Date',
    'Review_Return_Actual_Date',
    'Latest_Approval_Status',
    'Latest_Approval_Code',
    'Submitted_By',
    'Latest_Revision',
    'Count_of_Submissions'
]

# Check which of the desired columns actually exist in the DataFrame
existing_columns = [col for col in columns_for_monthly_report if col in df_cleaned_and_filtered.columns]

if len(existing_columns) < len(columns_for_monthly_report):
    status_print("Warning: Some specified columns for the monthly report do not exist in the DataFrame.")
    status_print(f"Missing columns: {list(set(columns_for_monthly_report) - set(existing_columns))}")

# Get unique month-year values and sort them
unique_months = sorted(df_cleaned_and_filtered['Submission Month-Year'].dropna().unique())

if xlsxwriter is None:
    status_print("xlsxwriter is not available. Monthly submission export requires xlsxwriter to be installed.")
    raise ImportError("xlsxwriter is required for monthly submission export")

# Create an ExcelWriter object
with pd.ExcelWriter(output_monthly_excel_filename, engine='xlsxwriter') as writer:
    for month_year in unique_months:
        # Filter data for the current month
        monthly_df = df_cleaned_and_filtered[df_cleaned_and_filtered['Submission Month-Year'] == month_year]

        # Select only the specified columns
        monthly_df_report = monthly_df[existing_columns]

        # Convert 'Period' type to string for sheet name
        sheet_name = str(month_year)

        # Write the monthly DataFrame to a new sheet
        monthly_df_report.to_excel(writer, sheet_name=sheet_name, index=False)

        # Optional: Auto-adjust column width for readability
        for column in monthly_df_report:
            column_length = max(monthly_df_report[column].apply(lambda x: len(str(x))).max(), len(column))
            col_idx = monthly_df_report.columns.get_loc(column)
            writer.sheets[sheet_name].set_column(col_idx, col_idx, column_length + 2)

status_print(f"Monthly submission reports saved to '{output_monthly_excel_filename}' in separate worksheets.")
cell_done("Monthly submission workbook generated")

# ===== CELL 48 =====
if is_colab:
    status_print(f"Downloading '{output_monthly_excel_filename}' to local Download folder...")
    files.download(output_monthly_excel_filename)
    status_print(f"The '{output_monthly_excel_filename}' file is ready for download.")
    # Ensure the download_file_path directory exists
    os.makedirs(download_file_path, exist_ok=True)
    destination_full_path = os.path.join(download_file_path, output_monthly_excel_filename)
    if os.path.abspath(output_monthly_excel_filename) == destination_full_path and not overwrite_existing_downloads:
        status_print(f"The file '{output_monthly_excel_filename}' is already at the destination '{download_file_path}'. Skipping redundant copy.")
    elif os.path.exists(destination_full_path) and not overwrite_existing_downloads:
        status_print(f"File '{output_monthly_excel_filename}' already exists at '{download_file_path}'. Overwrite is disabled, skipping copy.")
    else:
        shutil.copy(output_monthly_excel_filename, download_file_path)
        status_print(f"The '{output_monthly_excel_filename}' file has been copied to '{download_file_path}'.")
else:
    status_print(f"Downloading '{output_monthly_excel_filename}' to '{download_file_path}' folder...")
    # Ensure the download_file_path directory exists
    os.makedirs(download_file_path, exist_ok=True)
    destination_full_path = os.path.join(download_file_path, output_monthly_excel_filename)
    if os.path.abspath(output_monthly_excel_filename) == destination_full_path and not overwrite_existing_downloads:
        status_print(f"The file '{output_monthly_excel_filename}' is already at the destination '{download_file_path}'. Skipping redundant copy.")
    elif os.path.exists(destination_full_path) and not overwrite_existing_downloads:
        status_print(f"File '{output_monthly_excel_filename}' already exists at '{download_file_path}'. Overwrite is disabled, skipping copy.")
    else:
        shutil.copy(output_monthly_excel_filename, download_file_path)
        status_print(f"The '{output_monthly_excel_filename}' file has been copied to '{download_file_path}'.")

# ===== CELL 49 =====
summary_df = df_cleaned_and_filtered.groupby(['Document_ID', 'Discipline'])['Latest_Approval_Status'].agg(
    status_counts=lambda x: str(x.value_counts().to_dict()),
    unique_statuses=lambda x: ', '.join(x.dropna().unique().astype(str)) if not x.dropna().empty else 'N/A',
    most_frequent_status=lambda x: x.mode()[0] if not x.mode().empty else 'N/A'
).reset_index()

print("First 5 rows of the summary_df:")
debug_display(summary_df.head())
cell_done("Approval status summary dataframe created")

# ===== CELL 50 =====
print("Head of summary_df:")
debug_display(summary_df.head())

print("\nColumns in summary_df:")
print(summary_df.columns)
cell_done("Approval summary dataframe checked")

# ===== CELL 51 =====

def add_percentage_labels(ax, data_series):
    total = len(data_series.dropna()) # Use len() for countplot to get total number of items
    for p in ax.patches:
        percentage = '{:.1f}%'.format(100 * p.get_width()/total)
        x = p.get_x() + p.get_width() + 0.1 # Position slightly to the right of the bar
        y = p.get_y() + p.get_height()/2 # Center vertically
        ax.annotate(percentage, (x, y), ha='left', va='center', fontsize=9)

plt.figure(figsize=(12, 6))
ax = sns.countplot(data=summary_df, y='most_frequent_status', order=summary_df['most_frequent_status'].value_counts().index)
plt.title('Distribution of Most Frequent Approval Status per Document/Discipline')
plt.xlabel('Count')
plt.ylabel('Most Frequent Approval Status')
add_percentage_labels(ax, summary_df['most_frequent_status']) # Call the helper function
plt.savefig('overall_status_distribution.pdf') # Save as PDF
plt.show()

print("\nThis plot shows the overall distribution of the most frequent approval statuses, which can highlight common outcomes (e.g., 'Approved', 'Approved with Comments') and potential areas for review (e.g., 'Pending', 'To Check', 'Rejected').")
status_print("The chart has been exported to 'overall_status_distribution.pdf'.")
cell_done("Overall approval status chart generated")

# ===== CELL 52 =====
if is_colab:
    status_print("Downloading 'overall_status_distribution.pdf' to local Download folder...")
    files.download('overall_status_distribution.pdf')
    status_print("The 'overall_status_distribution.pdf' file is ready for download.")
    # Ensure the download_file_path directory exists
    os.makedirs(download_file_path, exist_ok=True)
    destination_full_path = os.path.join(download_file_path, 'overall_status_distribution.pdf')
    if os.path.abspath('overall_status_distribution.pdf') == destination_full_path and not overwrite_existing_downloads:
        status_print(f"The file 'overall_status_distribution.pdf' is already at the destination '{download_file_path}'. Skipping redundant copy.")
    elif os.path.exists(destination_full_path) and not overwrite_existing_downloads:
        status_print(f"File 'overall_status_distribution.pdf' already exists at '{download_file_path}'. Overwrite is disabled, skipping copy.")
    else:
        shutil.copy('overall_status_distribution.pdf', download_file_path)
        status_print(f"The 'overall_status_distribution.pdf' file has been copied to '{download_file_path}'.")
else:
    status_print("Downloading 'overall_status_distribution.pdf' to '{download_file_path}' folder...")
    # Ensure the download_file_path directory exists
    os.makedirs(download_file_path, exist_ok=True)
    destination_full_path = os.path.join(download_file_path, 'overall_status_distribution.pdf')
    if os.path.abspath('overall_status_distribution.pdf') == destination_full_path and not overwrite_existing_downloads:
        status_print(f"The file 'overall_status_distribution.pdf' is already at the destination '{download_file_path}'. Skipping redundant copy.")
    elif os.path.exists(destination_full_path) and not overwrite_existing_downloads:
        status_print(f"File 'overall_status_distribution.pdf' already exists at '{download_file_path}'. Overwrite is disabled, skipping copy.")
    else:
        shutil.copy('overall_status_distribution.pdf', download_file_path)
        status_print(f"The 'overall_status_distribution.pdf' file has been copied to '{download_file_path}'.")

# ===== CELL 53 =====

unique_disciplines = summary_df['Discipline'].unique()
num_disciplines = len(unique_disciplines)

# Determine the number of rows and columns for subplots
# +1 for the overall plot
num_plots = num_disciplines + 1
num_cols = 3 # Adjust as needed for better layout
num_rows = (num_plots + num_cols - 1) // num_cols # Ceiling division

plt.figure(figsize=(num_cols * 6, num_rows * 5)) # Adjust figure size dynamically
plt.suptitle('Distribution of Most Frequent Approval Status', fontsize=16, y=1.02)

# Helper function to add percentage labels to horizontal bar charts
def add_percentage_labels(ax, data_series):
    total = len(data_series.dropna()) # Use len() instead of sum() for countplot
    for p in ax.patches:
        percentage = '{:.1f}%'.format(100 * p.get_width()/total)
        x = p.get_x() + p.get_width() + 0.1 # Position slightly to the right of the bar
        y = p.get_y() + p.get_height()/2 # Center vertically
        ax.annotate(percentage, (x, y), ha='left', va='center', fontsize=9)

# Plot 1: Overall Distribution
ax_overall = plt.subplot(num_rows, num_cols, 1)
sns.countplot(data=summary_df, y='most_frequent_status', order=summary_df['most_frequent_status'].value_counts().index, ax=ax_overall)
ax_overall.set_title('Overall Distribution')
ax_overall.set_xlabel('Count')
ax_overall.set_ylabel('Most Frequent Approval Status')
add_percentage_labels(ax_overall, summary_df['most_frequent_status'])

# Plot for each discipline
for i, discipline in enumerate(unique_disciplines):
    ax_discipline = plt.subplot(num_rows, num_cols, i + 2) # Start from the second subplot
    discipline_df = summary_df[summary_df['Discipline'] == discipline]
    if not discipline_df.empty:
        sns.countplot(data=discipline_df, y='most_frequent_status', order=discipline_df['most_frequent_status'].value_counts().index, ax=ax_discipline)
        ax_discipline.set_title(f'Discipline: {discipline}')
        ax_discipline.set_xlabel('Count')
        ax_discipline.set_ylabel('Most Frequent Approval Status')
        add_percentage_labels(ax_discipline, discipline_df['most_frequent_status'])
    else:
        ax_discipline.set_title(f'Discipline: {discipline} (No Data)')
        ax_discipline.text(0.5, 0.5, 'No data available', horizontalalignment='center', verticalalignment='center', transform=ax_discipline.transAxes)

plt.tight_layout(rect=[0, 0.03, 1, 0.98]) # Adjust layout to prevent title overlap
plt.savefig('discipline_approval_status_dashboard.pdf') # Save as PDF
plt.show()
cell_done("Discipline approval status dashboard generated")

# ===== CELL 54 =====
if is_colab:
    status_print("Downloading 'discipline_approval_status_dashboard.pdf' to local Download folder...")
    files.download('discipline_approval_status_dashboard.pdf')
    status_print("The 'discipline_approval_status_dashboard.pdf' file is ready for download.")
    # Ensure the download_file_path directory exists
    os.makedirs(download_file_path, exist_ok=True)
    destination_full_path = os.path.join(download_file_path, 'discipline_approval_status_dashboard.pdf')
    if os.path.abspath('discipline_approval_status_dashboard.pdf') == destination_full_path and not overwrite_existing_downloads:
        status_print(f"The file 'discipline_approval_status_dashboard.pdf' is already at the destination '{download_file_path}'. Skipping redundant copy.")
    elif os.path.exists(destination_full_path) and not overwrite_existing_downloads:
        status_print(f"File 'discipline_approval_status_dashboard.pdf' already exists at '{download_file_path}'. Overwrite is disabled, skipping copy.")
    else:
        shutil.copy('discipline_approval_status_dashboard.pdf', download_file_path)
        status_print(f"The 'discipline_approval_status_dashboard.pdf' file has been copied to '{download_file_path}'.")
else:
    status_print("Downloading 'discipline_approval_status_dashboard.pdf' to '{download_file_path}' folder...")
    # Ensure the download_file_path directory exists
    os.makedirs(download_file_path, exist_ok=True)
    destination_full_path = os.path.join(download_file_path, 'discipline_approval_status_dashboard.pdf')
    if os.path.abspath('discipline_approval_status_dashboard.pdf') == destination_full_path and not overwrite_existing_downloads:
        status_print(f"The file 'discipline_approval_status_dashboard.pdf' is already at the destination '{download_file_path}'. Skipping redundant copy.")
    elif os.path.exists(destination_full_path) and not overwrite_existing_downloads:
        status_print(f"File 'discipline_approval_status_dashboard.pdf' already exists at '{download_file_path}'. Overwrite is disabled, skipping copy.")
    else:
        shutil.copy('discipline_approval_status_dashboard.pdf', download_file_path)
        status_print(f"The 'discipline_approval_status_dashboard.pdf' file has been copied to '{download_file_path}'.")

# ===== CELL 55 =====
# Apply the mapping to create Latest_Approval_Code from Latest_Approval_Status
df_cleaned_and_filtered['Latest_Approval_Code'] = df_cleaned_and_filtered['Latest_Approval_Status'].map(approval_code_mapping)

status_print("Applied Latest_Approval_Code mapping")
status_print("Latest_Approval_Code null count: " + str(df_cleaned_and_filtered['Latest_Approval_Code'].isna().sum()))
status_print("Latest_Approval_Code unique values: " + str(df_cleaned_and_filtered['Latest_Approval_Code'].unique()))

# ===== CELL 56 =====
df_cleaned_and_filtered['Submission_Date'] = pd.to_datetime(df_cleaned_and_filtered['Submission_Date'], format='%d/%m/%Y', errors='coerce')
df_cleaned_and_filtered['Submission Month-Year'] = df_cleaned_and_filtered['Submission_Date'].dt.to_period('M')

print("DataFrame after converting 'Submission_Date' to datetime and adding 'Submission Month-Year':")
debug_display(df_cleaned_and_filtered[['Submission_Date', 'Submission Month-Year', 'Latest_Approval_Code']].head())
cell_done("Approval trend dates prepared")

# ===== CELL 57 =====
# Create 'Submission Month-Year' column from 'Submission_Date' if it doesn't exist
if 'Submission Month-Year' not in df_cleaned_and_filtered.columns:
    df_cleaned_and_filtered['Submission Month-Year'] = pd.to_datetime(df_cleaned_and_filtered['Submission_Date']).dt.to_period('M')

# Group by 'Submission Month-Year' and 'Latest_Approval_Code' and count occurrences
trend_data = df_cleaned_and_filtered.groupby(['Submission Month-Year', 'Latest_Approval_Code']).size().unstack(fill_value=0)

# DEBUG: Check the data
print(f"trend_data shape: {trend_data.shape}")
print(f"trend_data dtypes:\n{trend_data.dtypes}")
print(f"trend_data:\n{trend_data}")
print(f"trend_data.empty: {trend_data.empty}")

# Sort the index to ensure chronological order
trend_data = trend_data.sort_index()

# Create a stacked bar chart
plt.figure(figsize=(15, 8))
ax = trend_data.plot(kind='bar', stacked=True, figsize=(15, 8))
plt.title('Approval Status Trends Over Time')
plt.xlabel('Submission Month-Year')
plt.ylabel('Number of Submissions')
plt.xticks(rotation=45, ha='right')
plt.legend(title='Latest_Approval_Code', bbox_to_anchor=(1.05, 1), loc='upper left')

# Add total counts on top of each stacked bar
for container in ax.containers:
    # Only annotate the last container (top segment of each bar) to get total height
    for i, p in enumerate(container):
        total_sum = trend_data.iloc[i].sum() # Sum of all segments for the current bar
        if p.get_height() > 0: # Only annotate if there's a bar segment
            ax.annotate(f'{total_sum:.0f}',
                        (p.get_x() + p.get_width() / 2., total_sum),
                        ha='center', va='bottom',
                        xytext=(0, 3),
                        textcoords='offset points')

plt.tight_layout()
plt.savefig('approval_trends_over_time.pdf') # Save the plot as a PDF
plt.show()

status_print("Stacked bar chart showing 'Approval_Code' trends over time has been generated.")
status_print("The chart has been exported to 'approval_trends_over_time.pdf'.")
cell_done("Approval trends chart generated")

# ===== CELL 58 =====
if is_colab:
    status_print("Downloading 'approval_trends_over_time.pdf' to local Download folder...")
    files.download('approval_trends_over_time.pdf')
    status_print("The 'approval_trends_over_time.pdf' file is ready for download.")
    # Ensure the download_file_path directory exists
    os.makedirs(download_file_path, exist_ok=True)
    destination_full_path = os.path.join(download_file_path, 'approval_trends_over_time.pdf')
    if os.path.abspath('approval_trends_over_time.pdf') == destination_full_path and not overwrite_existing_downloads:
        status_print(f"The file 'approval_trends_over_time.pdf' is already at the destination '{download_file_path}'. Skipping redundant copy.")
    elif os.path.exists(destination_full_path) and not overwrite_existing_downloads:
        status_print(f"File 'approval_trends_over_time.pdf' already exists at '{download_file_path}'. Overwrite is disabled, skipping copy.")
    else:
        shutil.copy('approval_trends_over_time.pdf', download_file_path)
        status_print(f"The 'approval_trends_over_time.pdf' file has been copied to '{download_file_path}'.")
else:
    status_print("Downloading 'approval_trends_over_time.pdf' to '{download_file_path}' folder...")
    # Ensure the download_file_path directory exists
    os.makedirs(download_file_path, exist_ok=True)
    destination_full_path = os.path.join(download_file_path, 'approval_trends_over_time.pdf')
    if os.path.abspath('approval_trends_over_time.pdf') == destination_full_path and not overwrite_existing_downloads:
        status_print(f"The file 'approval_trends_over_time.pdf' is already at the destination '{download_file_path}'. Skipping redundant copy.")
    elif os.path.exists(destination_full_path) and not overwrite_existing_downloads:
        status_print(f"File 'approval_trends_over_time.pdf' already exists at '{download_file_path}'. Overwrite is disabled, skipping copy.")
    else:
        shutil.copy('approval_trends_over_time.pdf', download_file_path)
        status_print(f"The 'approval_trends_over_time.pdf' file is ready for download.")

# ===== CELL 59 =====
# Generate submision curve over time


# Ensure 'This Submission_Date' is in datetime format for plotting
# (It might have been converted to string for dd/mm/yyyy display earlier, so re-convert if needed)
if not pd.api.types.is_datetime64_any_dtype(df_cleaned_and_filtered['Submission_Date']):
    df_cleaned_and_filtered['Submission_Date'] = pd.to_datetime(df_cleaned_and_filtered['Submission_Date'], format='%d/%m/%Y', errors='coerce')

# Aggregate submissions by date
daily_submissions = df_cleaned_and_filtered.groupby('Submission_Date').size().reset_index(name='Count_of_Submissions')

# Sort by date to ensure proper curve plotting
daily_submissions = daily_submissions.sort_values('Submission_Date')

plt.figure(figsize=(15, 7))
sns.lineplot(data=daily_submissions, x='Submission_Date', y='Count_of_Submissions')
plt.title('Count_of_Submissions Over Time')
plt.xlabel('Submission_Date')
plt.ylabel('Count_of_Submissions')
plt.grid(True, linestyle='--', alpha=0.7)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('submissions_over_time_curve.pdf') # Save as PDF
plt.show()

status_print("A curve showing the number of submissions over time has been generated.")
status_print("The chart has been exported to 'submissions_over_time_curve.pdf'.")
cell_done("Submission curve generated")

# ===== CELL 60 =====
if is_colab:
    status_print("Downloading 'submissions_over_time_curve.pdf' to local Download folder...")
    files.download('submissions_over_time_curve.pdf')
    status_print("The 'submissions_over_time_curve.pdf' file is ready for download.")
    # Ensure the download_file_path directory exists
    os.makedirs(download_file_path, exist_ok=True)
    destination_full_path = os.path.join(download_file_path, 'submissions_over_time_curve.pdf')
    if os.path.abspath('submissions_over_time_curve.pdf') == destination_full_path and not overwrite_existing_downloads:
        status_print(f"The file 'submissions_over_time_curve.pdf' is already at the destination '{download_file_path}'. Skipping redundant copy.")
    elif os.path.exists(destination_full_path) and not overwrite_existing_downloads:
        status_print(f"File 'submissions_over_time_curve.pdf' already exists at '{download_file_path}'. Overwrite is disabled, skipping copy.")
    else:
        shutil.copy('submissions_over_time_curve.pdf', download_file_path)
        status_print(f"The 'submissions_over_time_curve.pdf' file has been copied to '{download_file_path}'.")
else:
    status_print("Downloading 'submissions_over_time_curve.pdf' to '{download_file_path}' folder...")
    # Ensure the download_file_path directory exists
    os.makedirs(download_file_path, exist_ok=True)
    destination_full_path = os.path.join(download_file_path, 'submissions_over_time_curve.pdf')
    if os.path.abspath('submissions_over_time_curve.pdf') == destination_full_path and not overwrite_existing_downloads:
        status_print(f"The file 'submissions_over_time_curve.pdf' is already at the destination '{download_file_path}'. Skipping redundant copy.")
    elif os.path.exists(destination_full_path) and not overwrite_existing_downloads:
        status_print(f"File 'submissions_over_time_curve.pdf' already exists at '{download_file_path}'. Overwrite is disabled, skipping copy.")
    else:
        shutil.copy('submissions_over_time_curve.pdf', download_file_path)
        status_print(f"The 'submissions_over_time_curve.pdf' file is already at the destination '{download_file_path}'. Skipping redundant copy.")

# ===== CELL 61 =====
# check records which have "Pending" in 'this revision approval status' and null value in 'this review return date', list down records which has 'this Submission_Date' one month ago.

# Ensure 'Submission_Date' and 'Review_Return_Actual_Date' are datetime objects
df_cleaned_and_filtered['Submission_Date'] = pd.to_datetime(df_cleaned_and_filtered['Submission_Date'], errors='coerce')
df_cleaned_and_filtered['Review_Return_Actual_Date'] = pd.to_datetime(df_cleaned_and_filtered['Review_Return_Actual_Date'], errors='coerce')

# Calculate one month ago from today
one_month_ago = datetime.now() - timedelta(days=30) # Using 30 days as an approximation for 'one month'

# Filter for records based on the criteria
overdue_reviews_df = df_cleaned_and_filtered[
    (df_cleaned_and_filtered['Review_Status_Code'] == 'PEN') &
    (df_cleaned_and_filtered['Review_Return_Actual_Date'].isnull()) &
    (df_cleaned_and_filtered['Submission_Date'] < one_month_ago)
]

if not overdue_reviews_df.empty:
    status_print(f"Found {len(overdue_reviews_df)} records for overdue reviews (more than one month ago):")
    debug_display(overdue_reviews_df.head())
else:
    status_print("No overdue review records found matching the criteria.")

# ===== CELL 62 =====
# Define the columns to extract
selected_columns_for_overdue_report = [
    'Submission_Session',
    'Submission_Session_Revision',
    'Submission_Session_Subject',
    'Submission_Date',
    'Review_Status',
    'Submitted_By'
]

# Create a new DataFrame with only the selected columns
overdue_report_df = overdue_reviews_df[selected_columns_for_overdue_report]

# Remove duplicate records from the new DataFrame
overdue_report_df = overdue_report_df.drop_duplicates()

output_overdue_file_name = 'Overdue_Submission_Records.xlsx'

# Save the DataFrame to an Excel file (creates it in the current working directory)
overdue_report_df.to_excel(output_overdue_file_name, index=False)

status_print(f"Overdue submission records successfully saved to '{output_overdue_file_name}'.")
status_print("A download prompt will appear shortly.")

# Construct the full path where the file *would be* in the download_file_path directory
destination_full_path = os.path.join(download_file_path, output_overdue_file_name)

# Trigger the download
if is_colab:
    status_print(f"Downloading '{output_overdue_file_name}' to local Download folder...")
    files.download(output_overdue_file_name)
    status_print(f"The '{output_overdue_file_name}' file is ready for download.")

    # Ensure the download_file_path directory exists
    os.makedirs(download_file_path, exist_ok=True)

    if os.path.abspath(output_overdue_file_name) == destination_full_path and not overwrite_existing_downloads:
        status_print(f"The file '{output_overdue_file_name}' is already at the destination '{download_file_path}'. Skipping redundant copy.")
    elif os.path.exists(destination_full_path) and not overwrite_existing_downloads:
        status_print(f"File '{output_overdue_file_name}' already exists at '{download_file_path}'. Overwrite is disabled, skipping copy.")
    else:
        shutil.copy(output_overdue_file_name, download_file_path)
        status_print(f"The '{output_overdue_file_name}' file has been copied to '{download_file_path}'.")
else:
    status_print(f"Downloading '{output_overdue_file_name}' to '{download_file_path}' folder...")
    # Ensure the download_file_path directory exists
    os.makedirs(download_file_path, exist_ok=True)

    if os.path.abspath(output_overdue_file_name) == destination_full_path and not overwrite_existing_downloads:
        status_print(f"The file '{output_overdue_file_name}' is already at the destination '{download_file_path}'. Skipping redundant copy.")
    elif os.path.exists(destination_full_path) and not overwrite_existing_downloads:
        status_print(f"File '{output_overdue_file_name}' already exists at '{download_file_path}'. Overwrite is disabled, skipping copy.")
    else:
        shutil.copy(output_overdue_file_name, download_file_path)
        status_print(f"The '{output_overdue_file_name}' file has been copied to '{download_file_path}'.")

