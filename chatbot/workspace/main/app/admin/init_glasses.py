'''
안경 데이터 초기화 프로그램.
'''
import asyncio
import logging
from dotenv import load_dotenv

from config.mdb_configuration import MDBConfiguration
from config.glasses_vectordb_configuration import GlassesVectorDBConfiguration
import config.logging_configuration 
from repositories.glasses_repository import GlassesRepository

load_dotenv()

class GlassesVectorInitManager:
    '''
    안경 데이터를 초기화 함.
    '''
    _log = logging.getLogger('GlassesVectorInitManager')

    def __init__(self):
        _config = GlassesVectorDBConfiguration()
        self._vector_store = _config.get_vector_store()
        self._collection_name = _config.get_collection_name()
        self._glasses_repository = GlassesRepository()

    async def init_data(self) -> None:
        '''
        ChromaDB Client를 초기화 한다.

        '''
        self._log.debug('[%s] start initing ChromaDB. collectin_name is %s', self, self._collection_name)

        _db = MDBConfiguration()
        await _db.init_connection()

        # 명령어와 임베딩 모델 초기화
        _conn = self._glasses_repository.get_connection()
        _total = await self._glasses_repository.get_total(_conn=_conn)
        offset = 0
        limit = 100
        _documents = {}
        _pattern = '{}은 {} 브랜드에서 제작하였습니다. {}형태의 안경입니다. 색상은 {} 이고, 재질 또는 소재는 {} 으로 만들어 졌습니다. 가격은 {} 입니다. 자세한 정보를 원하시면 {} 에 방문 해 보세요'
        while offset < _total:
            _lst = await self._glasses_repository.read_pagenated_list(offset=offset,limit=limit)
            offset += limit
            for item in _lst:
                self._vector_store.add_texts(
                    texts=[_pattern.format(
                        item.product_name,
                        item.brand_name,
                        item.glasses_type.glasses_type,
                        item.color_code.color_name,
                        item.material_code.material_name,
                        item.price,
                        item.url
                        )],
                    ids=[f"{item.glasses_sub_id}"]
                )

    def clean(self) -> None:
        '''
        Clear Collection 
        '''
        self._log.debug('[%s] start clearning ChromaDB. collectin_name is %s',
                         __name__, self._collection_name)
        try:
            self._vector_store.reset_collection()
        except ValueError as ex:
            self._log.error('[%s] %s',self, ex)
        except Exception as ex:
            self._log.error('[%s] %s',self, ex)

        self._log.debug('[%s] End clearning ChromaDB. collectin_name is %s',
                         __name__, self._collection_name)
        
if '__main__' == __name__:
    _manager = GlassesVectorInitManager()
    print(' ===================== Start init. ===================== ')
    _manager.clean()
    print(' ===================== End clean.  ===================== ')
    asyncio.run(_manager.init_data())
    print(' ===================== End init.   ===================== ')