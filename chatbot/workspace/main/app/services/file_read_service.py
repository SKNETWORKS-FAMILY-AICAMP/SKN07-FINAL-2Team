'''
file_read_service.py

author: sgkim
since: 2025-03-19
'''
import threading
from typing import (
    List,
    Optional
)
import logging

from halowing.util.properties.application_properties import ApplicationProperties
from halowing.exception.exceptions import NotFoundException
from halowing.web.codes import FileState

from models.fileuploader_model import FileBaseModel, StoredFileModel
from models.file_list_model import SearchResponseModel
from repositories.file_repository import FileRepository

from services.service_helper import FileServiceHelper as fsh

class FileReadService:
    '''
    File 목록을 읽고 조회 하는 서비스
    '''

    _instance = None
    _lock = threading.Lock()

    _log = logging.getLogger('FileReadService')
    _repository:FileRepository = None

    def __new__(cls):
        if cls._instance is not None:
            return cls._instance
        
        with cls._lock:
            if cls._instance is not None:
                return cls._instance
            cls._instance = super(FileReadService, cls).__new__(cls)
            cls._repository = FileRepository()
            cls._property:ApplicationProperties = ApplicationProperties()
            return cls._instance

    async def get_completed_list(self, offset:int, limit:int) -> List[FileBaseModel]:
        ''' 상태가 Completed 인 것의 목록 '''
        _conn = self._repository.get_connection()
        
        return await self.get_list(offset, limit, FileState.COMPLETED, conn = _conn)

    async def get_list(self, offset:int, limit:int, 
                         state: Optional[FileState] = None,
                         conn = None
                         ) -> SearchResponseModel:
        ''' paged 목록 '''
        conn = conn if conn is not None else self._repository.get_connection()

        _total = await self._repository.get_total(state,conn=conn)
        rs = SearchResponseModel(offset=offset, limit=limit)
        if _total == 0:
            return rs
        lst = await self._repository.read_pagenated_list(offset, limit, state, conn=conn)
        for item in lst:
            fsh.set_url(item)

        rs.total=_total
        rs.datas = lst

        return rs

    async def get(self, file_id:str) -> StoredFileModel:
        '''
        상세 정보
        '''
        self._log.debug('file_id = %s',file_id)

        _conn = self._repository.get_connection()

        item = await self._repository.read_one(file_id,_conn=_conn)
        if item is None:
            raise NotFoundException(file_id)
        fsh.set_url(item)
        return item
