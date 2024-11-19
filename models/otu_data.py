import logging
from helpers.dbm import connect_db, get_session
from models.db_model import OTUDataTable, OTUTable
from models.otu import Otu

# Get the logger instance from app.py
logger = logging.getLogger("my_app_logger")  

class OtuData:
    def __init__(self, **kwargs):
        # Initialize the instance with the provided arguments (fields)
        self.__dict__.update(kwargs)

    @classmethod
    def create(cls, otu_id, sample_id, count, analysis_type_id):
        """Create a new OTU entry or update the count if it already exists."""
        db_engine = connect_db()
        session = get_session(db_engine)

        try:
            # Check if the OTU already exists in the OTUTable
            otu = Otu.get(otu_id)
            if not otu:
                # If OTU doesn't exist, create it
                otu = Otu.create(otu_id=otu_id)
            otu_id_db = otu.id  # Retrieve the actual OTU id from OTUTable

            # Check if an OTUData entry with the same otu_id, sample_id, and analysis_type_id exists
            existing_otu_data = (
                session.query(OTUDataTable)
                .filter_by(otu_id=otu_id_db, sample_id=sample_id, analysis_type_id=analysis_type_id)
                .first()
            )

            if existing_otu_data:
                # If the entry exists, update the count (or handle it as needed)
                existing_otu_data.count = count
                session.commit()
                logger.info(f"Updated OTUData with OTU id {otu_id_db} and sample_id {sample_id}.")
                return existing_otu_data
            else:
                # Create a new OTUDataTable instance
                otu_data = OTUDataTable(
                    otu_id=otu_id_db, sample_id=sample_id, count=count, analysis_type_id=analysis_type_id
                )
                session.add(otu_data)
                session.commit()

                logger.info(f"OTUData created successfully with OTU id {otu_id_db} and sample_id {sample_id}.")
                return otu_data
        except Exception as e:
            logger.error(f"Error creating or updating OTUData: {e}")
            session.rollback()
            return None
        finally:
            session.close()

    @classmethod
    def get(cls, id):
        """Retrieve an OTU by its ID."""
        db_engine = connect_db()
        session = get_session(db_engine)

        try:
            # Query for the OTU by its ID
            otu_data = session.query(OTUDataTable).filter_by(id=id).first()

            if not otu_data:
                logger.warning(f"OTU with ID {id} not found.")
                return None

            # Convert the retrieved OTU to a dictionary
            otu_data_dict = otu_data.__dict__

            # Remove internal keys (those that start with '_')
            filtered_dict = {
                key: value
                for key, value in otu_data_dict.items()
                if not key.startswith("_")
            }

            # Create and return an instance of OTU using the dictionary
            return OTU(**filtered_dict)
        except Exception as e:
            logger.error(f"Error retrieving OTU with ID {id}: {e}")
            return None
        finally:
            session.close()

    @classmethod
    def get_all_by_sample(cls, sample_id):
        """Retrieve all OTU entries for a specific sample."""
        db_engine = connect_db()
        session = get_session(db_engine)

        try:
            # Query for all OTU entries associated with a specific sample
            otu_data = session.query(OTUDataTable).filter_by(sample_id=sample_id).all()

            # If no data found, log and return an empty list
            if not otu_data:
                logger.warning(f"No OTU data found for sample ID {sample_id}.")
                return []

            # Convert the retrieved OTUs to dictionaries and return them
            return [
                {
                    "id": otu.id,
                    "otu_id": otu.otu_id,
                    "count": otu.count
                }
                for otu in otu_data
            ]
        except Exception as e:
            logger.error(f"Error retrieving OTU data for sample ID {sample_id}: {e}")
            return []
        finally:
            session.close()
