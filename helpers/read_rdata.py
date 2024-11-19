import pandas as pd
from models.sequencing_upload import SequencingUpload
from models.otu_data import OtuData
import logging

# Get the logger instance from app.py
logger = logging.getLogger("my_app_logger")

def read_and_insert_otu_data(filename, upload_id, analysis_type_id):
    """Reads the OTU table CSV file and inserts the data into the OTUs table."""
    
    # Step 1: Read the CSV file using pandas
    df = pd.read_csv(filename, index_col=0)  # Ensure the first column is treated as the index (OTU IDs)
    logger.info(f"CSV file '{filename}' read successfully.")

    # Get the samples associated with the given upload_id
    samples = SequencingUpload.get_samples(upload_id)
    
    # Extract the relevant fields (id and SampleID) from the samples
    sample_ids = {sample['SampleID']: sample['id'] for sample in samples}

    if not sample_ids:
        logger.error(f"No samples found for upload_id {upload_id}.")
        return False

    logger.info(f"Retrieved {len(sample_ids)} samples for upload_id {upload_id}.")

    # Step 3: Prepare the data and insert into the OTUs table
    records_inserted = 0
    for otu_id in df.index:  # Here we use the actual OTU ID from the index
        for sample_name, count in df.loc[otu_id].items():
            if count == 0:  # Skip insertion if the count is 0
                continue

            sample_id = sample_ids.get(sample_name)
            if sample_id:
                # Use OTU.create method to insert data
                OtuData.create(otu_id=otu_id, sample_id=sample_id, count=int(count), analysis_type_id=analysis_type_id)
                records_inserted += 1

    logger.info(f"Inserted {records_inserted} OTU records into the database.")
    return True
