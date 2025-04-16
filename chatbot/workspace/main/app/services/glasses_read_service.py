'''
glasses_read_service.py

author: sgkim
since: 2025-03-25
'''
import threading
import logging
from typing import (
    Optional,
    Dict,
    Any
)

from halowing.web.response_model import SearchResponseModel
from halowing.util.properties.application_properties import ApplicationProperties
from halowing.exception.exceptions import NotFoundException

from models  import glasses_models as gm
from repositories.glasses_repository import GlassesRepository

class GlassesReadService:
    ''' Data를 읽고 조회 하는 서비스 '''

    _instance = None
    _lock = threading.Lock()

    _log = logging.getLogger('GlassesReadService')

    def __new__(cls):
        '''
        instance를 singletone으로 생성한다.
        '''
        if cls._instance is not None:
            return cls._instance
        
        with cls._lock:
            if cls._instance is not None:
                return cls._instance
            cls._instance = super(GlassesReadService, cls).__new__(cls)

            cls._property:ApplicationProperties = ApplicationProperties()
            cls._repository = GlassesRepository()

            return cls._instance

    async def get_list(self, 
                       offset:int, limit:int,
                       condition: Optional[Dict[str,Any]]  = None
                       ) -> SearchResponseModel[gm.GlassesSubModel]:
        ''' 
        paged 목록 
        
        :param offset: int, page offset, it is positive number and shoud be zero on first time.
        :param limit: int, page limit, default is 10
        :param conditon: Dict, search condition
        '''
        _conn = self._repository.get_connection()

        total:int = await self._repository.get_total(condition=condition, _conn= _conn)
        rs:SearchResponseModel = SearchResponseModel[gm.GlassesSubModel](offset=offset, limit=limit, 
                                                                  condition=condition, total=total)
        if total == 0:
            return rs
        lst = await self._repository.read_pagenated_list(offset=offset, limit=limit,
                                                        condition=condition, _conn=_conn)

        rs.datas = lst

        return rs

    async def get(self, _id:int) -> gm.GlassesSubModel :
        '''
        상세 정보

        :param _id: str, id of data, it's maybe uuid.uuid4()
        '''
        _conn = self._repository.get_connection()

        _rs = await self._repository.read_one(_id = _id, _conn= _conn)
        if _rs is None:
            raise NotFoundException(_id)
        
        self._log.debug('\n=======\n%s\n========',_rs)

        return _rs
