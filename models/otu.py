import logging
from helpers.dbm import connect_db, get_session
from models.db_model import OTUTable

# Get the logger instance from app.py
logger = logging.getLogger("my_app_logger")

class Otu:
    def __init__(self, **kwargs):
        # Initialize the instance with the provided arguments (fields)
        self.__dict__.update(kwargs)

    @classmethod
    def create(cls, otu_id):
        """Create a new OTU entry."""
        db_engine = connect_db()
        session = get_session(db_engine)

        try:
            # Check if the OTU already exists by otu_id
            existing_otu = session.query(OTUTable).filter_by(otu_id=otu_id).first()
            if existing_otu:
                logger.info(f"OTU {otu_id} already exists.")
                return existing_otu

            # Create a new OTUTable instance
            otu = OTUTable(otu_id=otu_id)
            session.add(otu)
            session.commit()

            logger.info(f"OTU {otu_id} created successfully.")
            return otu
        except Exception as e:
            logger.error(f"Error creating OTU: {e}")
            session.rollback()
            return None
        finally:
            session.close()

    @classmethod
    def get(cls, otu_id):
        """Retrieve an OTU entry by its ID."""
        db_engine = connect_db()
        session = get_session(db_engine)

        try:
            otu = session.query(OTUTable).filter_by(otu_id=otu_id).first()
            if otu:
                logger.info(f"OTU {otu_id} found.")
                return otu
            else:
                logger.info(f"OTU {otu_id} not found.")
                return None
        except Exception as e:
            logger.error(f"Error retrieving OTU {otu_id}: {e}")
            return None
        finally:
            session.close()

    @classmethod
    def get_all(cls):
        """Retrieve all OTU entries."""
        db_engine = connect_db()
        session = get_session(db_engine)

        try:
            otus = session.query(OTUTable).all()
            logger.info(f"Retrieved {len(otus)} OTU entries.")
            return otus
        except Exception as e:
            logger.error(f"Error retrieving OTUs: {e}")
            return []
        finally:
            session.close()
