import json
import os
import logging
from helpers.dbm import connect_db, get_session
from models.db_model import UploadTable
from sqlalchemy import desc, or_
from pathlib import Path
from fnmatch import fnmatch

# Get the logger instance from app.py
logger = logging.getLogger("my_app_logger")  # Use the same name as in app.py

class Upload():
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self.path = Path("uploads", self.uploads_folder)
        self.extract_directory = Path("processing", self.uploads_folder)

    @classmethod
    def get(self, id):
        db_engine = connect_db()
        session = get_session(db_engine)
        
        upload_db = session.query(UploadTable).filter_by(id=id).first()
        
        session.close()
        
        if not upload_db:
            return None

        # Assuming upload_db is an instance of some SQLAlchemy model
        upload_db_dict = upload_db.__dict__

        # Remove keys starting with '_'
        filtered_dict = {key: value for key, value in upload_db_dict.items() if not key.startswith('_')}

        # Create an instance of YourClass using the dictionary
        upload = Upload(**filtered_dict)
        
        return upload

    @classmethod
    def get_latest_unfinished_process(cls, user_id):
        db_engine = connect_db()
        session = get_session(db_engine)

        latest_upload = (
            session.query(UploadTable)
            .filter(
                UploadTable.user_id == user_id,
                or_(
                    UploadTable.renamed_sent_to_bucket == False,
                    UploadTable.renamed_sent_to_bucket.is_(None)
                )
            )
            .order_by(desc(UploadTable.updated_at))  # Get the latest based on updated_at
            .first()
        )

        session.close()

        return latest_upload

    @classmethod
    def create(self, user_id, csv_filename, uploads_folder):
        db_engine = connect_db()
        session = get_session(db_engine)
        
        new_upload = UploadTable(user_id=user_id, csv_filename=csv_filename, csv_uploaded=True, uploads_folder=uploads_folder)
        
        session.add(new_upload)
        session.commit()
        
        # Refresh the object to get the updated ID
        session.refresh(new_upload)
        
        new_upload_id = new_upload.id
        
        session.close()
        
        return new_upload_id

    @classmethod
    def mark_field_as_true(cls, upload_id, field_name):
        db_engine = connect_db()
        session = get_session(db_engine)

        upload = session.query(UploadTable).filter_by(id=upload_id).first()

        if upload and hasattr(upload, field_name):
            setattr(upload, field_name, True)
            session.commit()
            session.close()
            return True
        else:
            session.close()
            return False

    @classmethod
    def update_fastqc_process_id(cls, upload_id, fastqc_process_id):
        db_engine = connect_db()
        session = get_session(db_engine)

        upload = session.query(UploadTable).filter_by(id=upload_id).first()

        if upload:
            upload.fastqc_process_id = fastqc_process_id
            session.commit()
            session.close()
            return True
        else:
            session.close()
            return False

    @classmethod
    def update_gz_filename(cls, upload_id, gz_filename):
        db_engine = connect_db()
        session = get_session(db_engine)

        upload = session.query(UploadTable).filter_by(id=upload_id).first()

        if upload:
            upload.gz_filename = gz_filename
            session.commit()
            session.close()
            return True
        else:
            session.close()
            return False


    @classmethod
    def update_gz_filedata(cls, upload_id, gz_filedata):
        logger.info('############### 222222222 ############')
        logger.info('2. We should add the gz_filedata for upload id ' + str(upload_id))
        
        logger.info(gz_filedata)
        
        db_engine = connect_db()
        session = get_session(db_engine)
        upload = session.query(UploadTable).filter_by(id=upload_id).first()
        # one_file_json_data = json.dumps(one_filedata)
        filename = gz_filedata['form_filename']

        if upload:
            existing_gz_filedata_db = upload.gz_filedata
            if (existing_gz_filedata_db):
                new_gz_filedata = json.loads(existing_gz_filedata_db)
            else:
                new_gz_filedata = {}
            new_gz_filedata[filename] = gz_filedata
                
            upload.gz_filedata = json.dumps(new_gz_filedata)
            logger.info('And now it is')
            logger.info(upload.gz_filedata)
            session.commit()
            session.close()
            logger.info('############### 333333333 ############')
            return True
        else:
            session.close()
            return False
        

    @classmethod
    def get_gz_filedata(cls, upload_id):
        db_engine = connect_db()
        session = get_session(db_engine)

        upload = session.query(UploadTable).filter_by(id=upload_id).first()

        uploads_folder = upload.uploads_folder
        upload_fullpath = Path("uploads", uploads_folder)
        gz_filedata = {}
        if upload.gz_filedata:
            gz_filedata = json.loads(upload.gz_filedata)
            for form_filename, file_data in gz_filedata.items():
                
                form_filechunks = 0
                if 'form_filechunks' in file_data:
                    form_filechunks = file_data['form_filechunks']

                # count how many parts are already uploaded:
                pattern = f"{form_filename}.part*"
                
                files_in_upload_dir = os.listdir(upload_fullpath)
                part_files = [file for file in files_in_upload_dir if fnmatch(file, pattern)]
                nr_parts = len(part_files)
                percent_uploaded = 0
                if form_filechunks:
                    percent_uploaded = round(int(nr_parts) / int(form_filechunks) * 100, 2)
                    
            gz_filedata[form_filename]['nr_parts'] = nr_parts
            gz_filedata[form_filename]['percent_uploaded'] = percent_uploaded

        return gz_filedata

    @classmethod
    def update_gz_sent_to_bucket_progress(cls, upload_id, progress, filename):
        db_engine = connect_db()
        session = get_session(db_engine)

        upload = session.query(UploadTable).filter_by(id=upload_id).first()

        if upload:
            if upload.gz_filedata:
                gz_filedata = json.loads(upload.gz_filedata)
                if filename in gz_filedata:
                    gz_filedata[filename]['gz_sent_to_bucket_progress']=progress
                    upload.gz_filedata = json.dumps(gz_filedata)
            
            session.commit()
            session.close()
            return True
        else:
            session.close()
            return False

    @classmethod
    def update_gz_unziped_progress(cls, upload_id, progress):
        db_engine = connect_db()
        session = get_session(db_engine)

        upload = session.query(UploadTable).filter_by(id=upload_id).first()

        if upload:
            upload.gz_unziped_progress = progress
            session.commit()
            session.close()
            return True
        else:
            session.close()
            return False
            
    @classmethod
    def update_fastqc_files_progress(cls, upload_id, progress):
        db_engine = connect_db()
        session = get_session(db_engine)

        upload = session.query(UploadTable).filter_by(id=upload_id).first()

        if upload:
            upload.fastqc_files_progress = progress
            session.commit()
            session.close()
            return True
        else:
            session.close()
            return False        
                
    @classmethod
    def update_renamed_sent_to_bucket_progress(cls, upload_id, progress):
        db_engine = connect_db()
        session = get_session(db_engine)

        upload = session.query(UploadTable).filter_by(id=upload_id).first()

        if upload:
            upload.renamed_sent_to_bucket_progress = progress
            session.commit()
            session.close()
            return True
        else:
            session.close()
            return False
            
    @classmethod
    def update_files_json(cls, upload_id, files_dict):
        logger.info('Inside update_files_json we will try to update with the files_dict:')
        logger.info(files_dict)
        db_engine = connect_db()
        session = get_session(db_engine)
        files_json = json.dumps(files_dict)

        upload = session.query(UploadTable).filter_by(id=upload_id).first()

        if upload:
            upload.files_json = files_json
            session.commit()
            session.close()
            return True
        else:
            session.close()
            return False   
            
    @classmethod
    def get_uploads_by_user(cls, user_id):
        db_engine = connect_db()
        session = get_session(db_engine)
        
        uploads = session.query(UploadTable).filter_by(user_id=user_id).all()
        
        session.close()
        
        if not uploads:
            return []
        
        uploads_list = [
            cls(**{key: getattr(upload, key) for key in upload.__dict__.keys() if not key.startswith('_')})
            for upload in uploads
        ]
        
        return uploads_list   