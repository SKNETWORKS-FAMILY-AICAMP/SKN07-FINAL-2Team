'''
file_repository.py

author: sgkim
since : 2025-03-18
'''
import threading
import logging
from typing import List, Optional, Dict

from tortoise.functions import Count

from halowing.web.codes import FileState

from config.mdb_configuration import MDBConfiguration
from entities.file_entities import StoredFileEntity
from models.fileuploader_model import StoredFileModel

class FileRepository:
    '''
    File 정보 저장소
    '''
    _instance = None
    _lock = threading.Lock()
    _log = logging.getLogger('FileRepository')

    _db_config:MDBConfiguration = None

    def __new__(cls):
        '''
        instance 생성.
        Singletone pattern
        '''
        if cls._instance is not None:
            return cls._instance
        
        with cls._lock:
            if cls._instance is not None:
                return cls._instance
            cls._instance = super(FileRepository,cls).__new__(cls)
            
            cls._db_config = MDBConfiguration()
            
            return cls._instance
        
    def in_transaction(self):
        '''
        in_transaction: Transaction 
        '''
        return self._db_config.in_transaction()

    def get_connection(self):
        '''
        DB Connection
        '''
        return self._db_config.get_connection()

    async def create(self, file_model:StoredFileModel) -> StoredFileModel:
        '''
        file 정보 생성
        '''
        file = await StoredFileEntity.create(
            file_id         = file_model.file_id,
            filename        = file_model.filename,
            file_size       = file_model.file_size,
            file_ext        = file_model.file_ext,
            stored_filename = file_model.stored_filename,
            path            = file_model.path,
            state           = FileState.UPLOADED
        )

        file_model.file_id           = file.file_id
        file_model.registed_datetime = file.registed_datetime
        file_model.state = file.state

        return file_model

    async def read_one(self, file_id:str, _conn=None) -> StoredFileModel:
        '''
        한 개 읽기
        '''
        file_entity:StoredFileEntity = await StoredFileEntity.get(file_id = file_id, using_db=_conn)

        return StoredFileModel.model_validate(file_entity)
    
    async def get_total_groupby_state(self, _conn = None) -> Dict[str, int]:
        ''' state별 total count '''
        _count = await StoredFileEntity.all(using_db=_conn).annotate(
            count=Count('file_id')
        ).group_by('state').values('state','count')

        total_dic:Dict[str,int] = {}
        for item in _count:
            total_dic[ FileState(item['state'])] = item['count']
        return total_dic

    async def get_total(self, state: Optional[FileState] = None, conn= None) -> int :
        ''' total counts in state or all '''
        if state is not None:
            _count = await StoredFileEntity.all(using_db=conn).filter(state = state).count()
        else:    
            _count = await StoredFileEntity.all(using_db=conn).count()
        return _count

    async def read_pagenated_list(self,
            offset:int = 0,
            limit: int = 10,
            state: Optional[FileState] = None,
            conn = None
    ) -> List[StoredFileModel]:
        '''
        page 된 목록
        '''
        if state is None:
            data = await StoredFileEntity.all(using_db=conn).order_by('-registed_datetiem').offset(offset).limit(limit)
        else:
            data = await StoredFileEntity.all(using_db=conn).filter(state=state).order_by('-registed_datetiem').offset(offset).limit(limit)
        lst = []
        for item in data:
            lst.append(StoredFileModel.model_validate(item))
        
        return lst

    async def update_state(self, file_id:str, state:FileState, conn=None) -> StoredFileModel:
        '''
        file 정보 변경
        '''
        self._log.debug('update_state:request_state= %s', state)
        async with self._db_config.in_transaction(conn):
            file_entity:StoredFileEntity = await StoredFileEntity.get(file_id = file_id)
            file_entity.state = state

            self._log.debug('update_state:file_entity= %s', file_entity.state)

            await file_entity.save()

        return StoredFileModel.model_validate(file_entity)
    
    async def delete_one(self, file_id:str, _conn = None) -> bool:
        '''
        파일 한개 삭제
        '''
        async with self._db_config.in_transaction(_conn):
            file_entity:StoredFileEntity = await StoredFileEntity.get(file_id = file_id)
            if file_entity.state == FileState.DELETED:
                return True
            file_entity.state = FileState.DELETED
            file_entity.save()
        return True
