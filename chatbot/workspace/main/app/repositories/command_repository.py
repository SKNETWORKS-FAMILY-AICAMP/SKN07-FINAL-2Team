'''
command_repository.py

author: sgkim
since: 2025-04-01
'''
import threading
from logging import getLogger
from typing import Optional, List

from config.command_vectordb_configuration import CommandVectorDBConfiguration
from models.chat_models import ChatModel
from repositories.ai_command_search import AiCommanderSearch


class CommandRepository:
    '''
    CommandRepository. 명령 구분
    '''
    _instance = None
    _lock = threading.Lock()

    _log = getLogger('CommandRepository')

    def __new__(cls):
        if cls._instance is not None:
            return cls._instance
        
        with cls._lock:
            if cls._instance is not None:
                return cls._instance
            cls._instance = super(CommandRepository, cls).__new__(cls)

            cls._config = CommandVectorDBConfiguration()

            cls._ai = AiCommanderSearch()

            cls._T1X = {
                'T11': '첫 번째',
                'T12': '두 번째',
                'T13': '세 번째',
                'T14': '네 번째',
                'T15': '다섯 번째',
                'T16': '여섯 번째',
            }
            
            return cls._instance
        
    def add_command(self, command: str, synonyms) -> None:
        '''
        명령어를 추가한다.
        :param command: str, 명령어
        :param synonyms: List[str], 동의어 리스트
        '''
        # 명령어 임베딩 생성 및 ChromaDB에 데이터 추가
        self._config.get_vector_store().add_texts(
            texts=synonyms,
            ids=[f"{command}_{i}" for i in range(len(synonyms))]
        )
           

    def get_command(
            self,
            user_msg: str,
            chat_list :List[ChatModel]
        ) -> tuple [str, str]:
        '''
        사용자가 입력한 문장을 분석하여 명령어를 찾는다.
        :param user_msg: str, 사용자가 입력한 문장
        '''

        self._log.debug('user_msg = %s',user_msg)

        _results = self._config.get_vector_store().similarity_search_with_relevance_scores (
            query=user_msg,
            k=1
        )

        # self._log.debug('_results = %s',_results)
        
        if _results is not None and len(_results[0]) > 0:
            self._log.debug('================')
            self._log.debug('len = %s',len(_results[0]))
            self._log.debug('%s',_results[0])
            self._log.debug('%s',_results[0][0].id)
            self._log.debug('================')
            if _results[0][1] >= 0.85:
                command_id =_results[0][0].id.split("_")[0]
            else:
                command_id = 'unknown'
            self._log.debug('[get_command] command_id = %s',command_id)
            if not command_id.startswith('T1') and command_id not in ('yes','no') and command_id.startswith('T'):
                self._log.debug('[get_command] command_id = %s',command_id)
                return command_id, ''
            
            if command_id.startswith('T1'):
                user_msg = self._T1X[command_id]

        # Vector DB로 검색되지 않는 명령어를 찾는다.
        self._log.debug('===== Command is None in VectoreStore. =====')
        command_id, output = self._ai.get_command(user_msg, chat_list)

        return command_id, output

