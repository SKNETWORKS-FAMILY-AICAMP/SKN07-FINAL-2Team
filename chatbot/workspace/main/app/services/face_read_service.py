'''
face_read_service.py

author: sgkim
since: 2025-04-08
'''

import threading
import logging
from typing import (
    Optional,
    Dict,
)

from halowing.web.response_model import SearchResponseModel
from halowing.util.properties.application_properties import ApplicationProperties
from halowing.exception.exceptions import NotFoundException

from models  import glasses_models as gm
from repositories.face_repository import FaceRepository

class FaceReadService:
    ''' 얼굴형 Data 읽고 조회 하는 서비스 '''

    _instance = None
    _lock = threading.Lock()

    _log = logging.getLogger('FaceReadService')

    def __new__(cls):
        '''
        instance를 singletone으로 생성한다.
        '''
        if cls._instance is not None:
            return cls._instance
        
        with cls._lock:
            if cls._instance is not None:
                return cls._instance
            cls._instance = super(FaceReadService, cls).__new__(cls)

            cls._property:ApplicationProperties = ApplicationProperties()
            cls._repository = FaceRepository()

            return cls._instance
        
    async def get_list(self,
                       offset:int, limit:int,
                       condition: Optional[Dict[str,str|int]]  = None
                       ) -> SearchResponseModel[gm.FaceShapeModel]:
        ''' 
        paged 목록 
        
        :param offset: int, page offset, it is positive number and shoud be zero on first time.
        :param limit: int, page limit, default is 10
        :param conditon: Dict, search condition
        '''
        _conn = self._repository.get_connection()

        total:int = await self._repository.get_total(conn=_conn)
        rs:SearchResponseModel = SearchResponseModel[gm.FaceShapeModel](offset=offset, limit=limit, 
                                                                  condition=condition, total=total)
        if total == 0:
            return rs
        lst = await self._repository.read_pagenated_list(offset=offset, limit=limit, 
                                                        condition=condition,
                                                        conn=_conn)

        rs.datas = lst

        return rs

    async def get(self, _id:int) -> gm.FaceShapeModel :
        '''
        상세 정보

        :param _id: int, id of data
        '''
        _conn = self._repository.get_connection()

        _rs = await self._repository.read_one(_id, conn = _conn)
        if _rs is None:
            raise NotFoundException(id)
        
        self._log.debug('\n=======\n%s\n========',_rs)

        return _rs
    
    async def find_one(self, _face_type:str) -> gm.FaceShapeModel :
        '''
        상세 정보

        :param _face_type:(str) face_type
        '''
        _conn = self._repository.get_connection()
        
        _condition:Dict[str,str] = {'face_shape_name':_face_type}
        _rs = await self._repository.read_pagenated_list(offset=0, limit=1,
                                                         condition=_condition,
                                                         conn= _conn)
        if _rs is None or len(_rs) == 0:
            return None
        
        self._log.debug('\n=======\n%s\n========',_rs)

        return _rs[0]
