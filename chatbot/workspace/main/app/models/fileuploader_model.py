""" 
fileuploader_model.py 

author: sgkim
since : 2025-03-14
"""
from uuid import UUID
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict

from halowing.web.codes import FileState

class FileBaseModel(BaseModel):
    """ 
    FileBaseModel 
    """
    file_id:  Optional[UUID]                = None
    url: Optional[str]                      = None
    filename: str
    file_size: Optional[int]                = None
    file_ext: Optional[str]                 = None
    registed_datetime: Optional[datetime]   = None

    model_config = ConfigDict(from_attributes=True, )

class StoredFileModel(FileBaseModel):
    """
    StoredFileModel
    """
    stored_filename: Optional[str]          = None
    path: Optional[str]                     = None
    state: FileState                       = FileState.UPLOADED

    model_config = ConfigDict(from_attributes=True)
