'''
face_repository.py

author: sgkim
since : 2025-04-08
'''
import logging
import threading
from typing import List, Optional, Dict

# from tortoise.functions import Count

from config.mdb_configuration import MDBConfiguration
from entities.code_entities  import FaceShape
from models import glasses_models as gm

class FaceRepository:
    '''
    정보 저장소
    '''
    _instance = None
    _lock = threading.Lock()
    _log = logging.getLogger('FaceRepository')

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
            cls._instance = super(FaceRepository,cls).__new__(cls)

            cls._db_config = MDBConfiguration()

            return cls._instance

    def get_connection(self):
        '''
        DB Connection 생성
        '''
        return  self._db_config.get_connection()

    async def read_one(self, _id:str, conn = None) -> gm.FaceShapeModel:
        '''
        한 개 읽기
        '''
        _rs:FaceShape = await FaceShape.get(face_shape_id = _id, using_db=conn).prefetch_related(
            'image' 
        )

        self._log.debug('\n=======\n%s\n========',_rs)

        _model:gm.FaceShapeModel = gm.FaceShapeModel.model_validate(_rs)
        return _model
    

    async def get_total(self,
                        condition: Optional[Dict[str,str|int]] = None ,
                        conn = None
                        ) -> int :
        ''' total counts in state or all '''
        if condition is None:
            condition = {}

        if len(condition) == 0:
            total = await FaceShape.all(using_db=conn).count()
        else:
            total = await FaceShape.all(using_db=conn).filter(condition).count()

        return total
    
    async def read_pagenated_list(self,
            offset:int = 0,
            limit: int = 10,
            condition: Optional[Dict[str,str|int]] = None ,
            conn = None
    ) -> List[gm.FaceShapeModel]:
        '''
        page 된 목록
        '''
        if condition is None:
            condition = {}

        # condition['offset'] = offset
        # condition['limit']  = limit

        if len(condition) == 0:
            data = await FaceShape.all(using_db=conn).prefetch_related(
                'image'
            ).order_by('face_shape_id').offset(offset).limit(limit)
        else:
            data = await FaceShape.all(using_db=conn).filter(**condition).prefetch_related(
                'image'
            ).order_by('face_shape_id').offset(offset).limit(limit)

        lst = []
        for item in data:
            lst.append(gm.FaceShapeModel.model_validate(item))

        return lst
