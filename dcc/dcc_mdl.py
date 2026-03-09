import tkinter as tk
from tkinter import filedialog
import pandas as pd
import os

# to load DCC Register Excel file

def load_excel_file():
    # Hide the main tkinter window
    root = tk.Tk()
    root.withdraw()

    # Open the file selection dialog
    file_path = filedialog.askopenfilename(
        title="Select an Excel File",
        initialdir="/mnt/c/",
        filetypes=[
            ("Excel files", "*.xlsx *.xls"),
            ("All files", "*.*")
        ]
    )

    # Check if a file was selected
    if file_path:
        print(f"Loading file: {file_path}")
        try:
            # First, read the Excel file to get the sheet names
            xls = pd.ExcelFile(file_path)
            sheet_names = xls.sheet_names
            
            # Prompt the user to select a sheet using a GUI popup
            selected_sheet = [None]  # Use a list to store the selection so it can be updated inside the function

            def on_select():
                try:
                    # Get the selected index from the listbox
                    idx = listbox.curselection()[0]
                    selected_sheet[0] = sheet_names[idx]
                    popup.destroy()
                except IndexError:
                    print("No worksheet selected. Please select one.")

            # Create a Toplevel popup
            popup = tk.Toplevel()
            popup.title("Select Worksheet")
            popup.geometry("300x250")
            
            # Make sure it appears above the hidden root window and stays in focus
            popup.attributes('-topmost', True)
            popup.grab_set()

            tk.Label(popup, text="Select the worksheet to load:", pady=10).pack()

            # Create a Listbox and populate it with sheet names
            listbox = tk.Listbox(popup, width=40, height=10)
            listbox.pack(padx=10, pady=5)
            for sheet in sheet_names:
                listbox.insert(tk.END, sheet)
            
            # Select the first sheet by default
            if sheet_names:
                listbox.selection_set(0)

            # Add a button to confirm selection
            select_button = tk.Button(popup, text="Select", command=on_select)
            select_button.pack(pady=10)

            # Wait for the popup window to be closed
            popup.wait_window()
            
            # If the user closed the window without selecting
            if selected_sheet[0] is None:
                print("Worksheet selection cancelled.")
                return None
                
            selected_sheet = selected_sheet[0]
            
            print(f"\nLoading worksheet: {selected_sheet}...")
            # Load the chosen worksheet into a pandas DataFrame
            # header=4 means row 5 is the header (0-indexed)
            # usecols="A:AP" loads columns A through AP
            df = pd.read_excel(file_path, sheet_name=selected_sheet, header=4, usecols="A:AP")
            
            # Remove all empty rows
            df.dropna(how='all', inplace=True)
            
            # Remove all empty columns
            df.dropna(axis=1, how='all', inplace=True)
            
            # If a cell is empty, copy from the previous row (forward fill)
            df.ffill(inplace=True)
            
            print("Successfully loaded the Excel file!")
            print(df.head())
            print("\nFirst row of data:")
            print(df.iloc[0])
            return df, file_path
        except Exception as e:
            print(f"Error loading the Excel file: {e}")
            return None, None
    else:
        print("No file selected.")
        return None, None

def generate_doc_id(df):
    """
    Creates a new 'Doc ID' column by concatenating 'Proj. Code', 'Proj. Prefix',
    'Doc Type', 'Discipline', and 'Number' with a hyphen separator.
    """
    if df is not None and not df.empty:
        # Define the exact target column names to concatenate
        target_columns = ['Proj. Code', 'Proj. Prefix', 'Doc Type', 'Discipline', 'Number']
        
        # Check if all required columns exist in the DataFrame
        missing_cols = [col for col in target_columns if col not in df.columns]
        if missing_cols:
            print(f"Warning: Cannot generate 'Doc ID'. Missing columns: {missing_cols}")
            return df
            
        # Ensure the columns are treated as strings and replace NaNs with empty string
        # then join them with '-'
        df['Doc ID'] = df[target_columns].fillna('').astype(str).agg('-'.join, axis=1)
        
        # Strip any dangling hyphens (e.g. if some fields were completely empty)
        df['Doc ID'] = df['Doc ID'].str.strip('-')
        
        print("\nSuccessfully generated 'Doc ID' column!")
        
    return df

def export_to_excel(df, output_dir, filename='Processed_Submittal_Tracker.xlsx'):
    """
    Exports the given DataFrame to an Excel file in the specified directory.
    """
    if df is not None and not df.empty:
        # Construct the full output path
        output_path = os.path.join(output_dir, filename)
        
        print(f"\nExporting data to {output_path}...")
        try:
            # We use index=False so we don't save the numerical pandas index
            df.to_excel(output_path, index=False)
            print("Successfully exported the Excel file!")
        except Exception as e:
            print(f"Failed to export DataFrame to Excel: {e}")

if __name__ == "__main__":
    df, original_file_path = load_excel_file()
    if df is not None and original_file_path is not None:
        # Generate the Doc ID column if possible
        df = generate_doc_id(df)
        
        print("\nFinal DataFrame head (with Doc ID):")
        print(df.head())
        
        print("\nDataFrame Headers and Data Types:")
        print(df.dtypes)
        
        # Get the directory of the originally loaded file
        output_directory = os.path.dirname(original_file_path)
        
        # Export the final processed dataframe to that same directory
        export_to_excel(df, output_dir=output_directory)

