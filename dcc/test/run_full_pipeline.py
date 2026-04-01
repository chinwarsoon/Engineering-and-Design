import pandas as pd
import json
import sys
from pathlib import Path
import logging

# Add workflow directory to path to import components
dcc_root = Path(__file__).parent.parent
sys.path.append(str(dcc_root / "workflow"))

from universal_column_mapper import UniversalColumnMapper
from universal_document_processor import UniversalDocumentProcessor

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger("FullPipeline")

def run_integration_test():
    # 1. Config and Paths
    schema_path = dcc_root / "config" / "schemas" / "dcc_register_enhanced.json"
    excel_path = dcc_root / "data" / "Submittal and RFI Tracker Lists.xlsx"
    
    # Initialize Mapper to get parameters
    mapper = UniversalColumnMapper(str(schema_path))
    params = mapper.main_schema.get('parameters', {})
    
    # Use output path from schema
    output_dir = Path(params.get('download_file_path', str(dcc_root / "output")))
    output_path = output_dir / "pipeline_test_output.csv"
    
    # 2. Initialize Components
    logger.info("Initializing Column Mapper and Document Processor...")
    processor = UniversalDocumentProcessor(str(schema_path))
    processor.load_schema()
    
    # 3. Load Data based on Schema Parameters
    params = mapper.main_schema.get('parameters', {})
    sheet_name = params.get('upload_sheet_name', 'Prolog Submittals ')
    start_col = params.get('start_col', 'P')
    end_col = params.get('end_col', 'AP')
    header_row = params.get('header_row_index', 4)
    
    logger.info(f"Loading Excel from {excel_path} [Sheet: {sheet_name}, Range: {start_col}:{end_col}, Header: {header_row}]")
    try:
        # Load data using configured range and header
        # We load a small number of rows for testing
        df_raw = pd.read_excel(
            excel_path, 
            sheet_name=sheet_name, 
            usecols=f"{start_col}:{end_col}",
            header=header_row,
            nrows=50  # Limit to 50 rows for test
        )
        logger.info(f"Loaded {len(df_raw)} rows with {len(df_raw.columns)} headers.")
    except Exception as e:
        logger.error(f"Failed to load Excel data: {e}")
        return

    # 4. Step 1: Column Mapping
    logger.info("Step 1: Mapping columns to schema aliases...")
    mapping_result = mapper.detect_columns(df_raw.columns.tolist())
    
    # Check for missing required columns warning in mapper
    if mapping_result.get('missing_required'):
        logger.warning(f"Mapper identified missing required columns: {mapping_result['missing_required']}")
    
    # Rename DataFrame columns
    df_renamed = mapper.rename_dataframe_columns(df_raw, mapping_result)
    
    # 5. Step 2: Document Processing
    logger.info("Step 2: Processing renamed data set...")
    try:
        df_processed = processor.process_data(df_renamed)
        
        # 6. Export and Results
        logger.info(f"Success! Processed data contains {len(df_processed.columns)} columns.")
        df_processed.to_csv(output_path, index=False)
        logger.info(f"Output saved to {output_path}")
        
        print("\n=== PIPELINE INTEGRATION TEST SUCCESSFUL ===")
        print(f"Original Headers: {len(df_raw.columns)}")
        print(f"Mapped Count:   {mapping_result['matched_count']}")
        print(f"Final Count:    {len(df_processed.columns)}")
        print(f"Result Preview (first 5 rows of Document_ID):\n{df_processed['Document_ID'].head()}")
        
    except ValueError as e:
        logger.error(f"Processor failed validation: {e}")
    except Exception as e:
        logger.error(f"Unexpected error during processing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_integration_test()
