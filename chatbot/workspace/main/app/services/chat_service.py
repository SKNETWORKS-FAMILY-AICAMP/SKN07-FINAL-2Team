'''
chat_service.py

---
result_type:
  0 : welcome
100 : None
---
author: sgkim
since : 2025-03-26
'''
import threading
from datetime import datetime
import logging

from halowing.util.properties.application_properties   import ApplicationProperties
from halowing.util.properties.message_properties import ResponseMessage
from models.chat_models import ChatModel, RequestChatModel
from session.session_models import ChatSessionData
from repositories.command_repository import CommandRepository
from services.tasks.task_manager import ChatTaskManager


class ChatService:
    ''' Chating Service '''

    _instance = None
    _lock = threading.Lock()
    _log = logging.getLogger('ChatService')

    def __new__(cls):
        '''
        instance를 singletone으로 생성한다.
        '''
        if cls._instance is not None:
            return cls._instance
        
        with cls._lock:
            if cls._instance is not None:
                return cls._instance
            cls._instance = super(ChatService, cls).__new__(cls)

            cls._property:ApplicationProperties = ApplicationProperties()
            cls._res_msg = ResponseMessage()
            cls._command_repository = CommandRepository()
            cls._tmanager = ChatTaskManager()

            return cls._instance

    async def welcome(self) -> ChatModel:
        ''' 첫 대화 '''
        _chat_data = ChatModel(
            msg_no=0,
            request_message='',
            request_datatime= datetime.today(),
            task_id='T00',
            response_message=self._res_msg['res.T00']
        )
        return _chat_data

    async def good_bye(self) -> ChatModel:
        '''
        good_bye
        '''
        _chat_data = ChatModel(
            msg_no=9999,
            request_message='good-bye',
            request_datatime= datetime.today(),
            task_id='good-bye',
            response_message=self._res_msg['res.good-bye']
        )
        return _chat_data

    async def ready_to_file_upload(self) ->ChatModel:
        ''' 파일 사용 준비 완료 '''
        _chat_data = ChatModel(
            msg_no=9999,
            request_message='사진을 전송할 준비가 완료 되었습니다.',
            request_datatime= datetime.today(),
            task_id='T20',
            response_message=self._res_msg['res.T20']
        )
        return _chat_data

    async def process(
            self,
            request_chat_data: RequestChatModel,
            session_data: ChatSessionData
        ) -> ChatModel:
        '''
        사용자가 전송한 문장을 분석하여 어떤 명령을 요청 했는지 구분한다.
        '''
        chat_data = ChatModel.model_validate(request_chat_data)
        chat_data.request_datatime = datetime.today()
        _task_id, _output = self._command_repository.get_command(
            request_chat_data.request_message,
            session_data.chat_list
        )
        
        self._log.debug('[process] task_id = %s, output = %s', _task_id, _output)

        if _task_id == 'ai':
            chat_data.task_id = 'T99'
            chat_data.response_message = _output
            return chat_data
        
        chat_data.task_id = _task_id
        chat_data = await self._tmanager.run_task(
            _task_id,
            session=session_data,
            model = chat_data
        )


        return chat_data

    
