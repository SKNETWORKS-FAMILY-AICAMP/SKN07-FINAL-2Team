""" 
file_list_model.py 

author: sgkim
since : 2025-03-24
"""
from typing import List, Optional, Dict
from pydantic import BaseModel, ConfigDict

from models.fileuploader_model import FileBaseModel

class SearchResponseModel(BaseModel):
    ''' SearchResponseModel '''
    datas : List[FileBaseModel]         = []
    query: Optional[Dict[str,str|int]]  = None
    offset: int                         = 0
    limit: int                          = 10
    total: int                          = 0

    model_config = ConfigDict(from_attributes=True, )
