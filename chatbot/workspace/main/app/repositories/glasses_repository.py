'''
sample_repository.py

author: sgkim
since : 2025-03-25
'''
import logging
import threading
from typing import List, Optional, Dict, Any

# from tortoise.functions import Count

from config.mdb_configuration import MDBConfiguration
from entities.glasses_entities  import GlassesSub
from models import glasses_models as gm

class GlassesRepository:
    '''
    정보 저장소
    '''
    _instance = None
    _lock = threading.Lock()

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
            cls._instance = super(GlassesRepository,cls).__new__(cls)
            
            cls._db_config = MDBConfiguration()
            cls._log = logging.getLogger('GlassesRepository')
            
            return cls._instance
        
    def get_connection(self):
        '''
        DB Connection
        '''
        return self._db_config.get_connection()

    async def read_one(self, _id:str, _conn = None) -> gm.GlassesSubModel:
        '''
        한 개 읽기
        '''
        _rs:GlassesSub = await GlassesSub.get(glasses_sub_id = _id, using_db=_conn).prefetch_related(
            'glasses',
            'color_code', 
            'material_code', 
            'glasses__glasses_type',
            'glasses__glasses_type__face_shapes',
            'glasses__glasses_type__face_shapes__image',
            'images' 
        )

        self._log.debug('\n=======\n%s\n========',_rs)

        _model:gm.GlassesSubModel = gm.GlassesSubModel.model_validate(_rs)
        return _model
    

    async def get_total(self,
                        condition: Optional[Dict[str,Any]] = None ,
                        _conn = None
                        ) -> int :
        ''' total counts in state or all '''
        if condition is None:
            condition = {}

        if len(condition) == 0:
            total = await GlassesSub.all(using_db=_conn).count()
        else:
            total = await GlassesSub.all(using_db=_conn).filter(
                **condition
            ).prefetch_related(
                'glasses',
                'color_code', 
                'material_code', 
                'glasses__glasses_type',
                'glasses__glasses_type__face_shapes',
            ).count()

        return total
    
    async def read_pagenated_list(self,
            offset:int = 0,
            limit: int = 10,
            condition: Optional[Dict[str,str|int]] = None ,
            _conn = None
    ) -> List[gm.GlassesSubModel]:
        '''
        page 된 목록
        '''
        if condition is None:
            condition = {}

        # condition['offset'] = offset
        # condition['limit']  = limit

        if len(condition) == 0:
            data = await GlassesSub.all(using_db=_conn).prefetch_related(
                'glasses',
                'color_code', 
                'material_code', 
                'glasses__glasses_type',
                'glasses__glasses_type__face_shapes',
                'glasses__glasses_type__face_shapes__image',
                'images' 
            ).order_by('glasses_sub_id').offset(offset).limit(limit)
        else:
            data = await GlassesSub.all(using_db=_conn).filter(**condition).prefetch_related(
                'glasses',
                'color_code', 
                'material_code', 
                'glasses__glasses_type',
                'glasses__glasses_type__face_shapes',
                'glasses__glasses_type__face_shapes__image',
                'images' 
            ).order_by('glasses_sub_id').offset(offset).limit(limit)
        
        lst = []
        for item in data:
            lst.append(gm.GlassesSubModel.model_validate(item))
        
        return lst
