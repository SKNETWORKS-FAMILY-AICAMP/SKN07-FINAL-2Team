'''
chat_service_test.py
'''

from datetime import datetime
from uuid import uuid4
import asyncio
import pytest
from models.chat_models import ChatModel, RequestChatModel
from services.chat_service import ChatService
from session.session_models import ChatSessionData
from services.tasks.task_manager import ChatTaskManager, ChatTaskManagerContext
import config.logging_configuration 


async def test():
    _service = ChatService()
    ChatTaskManagerContext.init()
    
    _request = RequestChatModel.model_validate({
        'request_message': '요즘 유행하는 최신 유행의 안경은 무엇이 있지',
        'message_no':1
    })
    _session = ChatSessionData.model_validate({
        'session_id': uuid4(),
        'created_datetime': datetime.today()
    })

    _chat  = ChatModel.model_validate({
            'request_message': "처음부터 다시 시작하자.",
            'response_message': "안녕하세요. FaceFit 서비스에 오신 것을 환영합니다. 얼굴형에 어울리는 안경을 추천 받기 원하시면 1. 웹캠을 이용하여 사진을 촬영하거나 2. 얼굴 사진 파일을 대화창에 첨부해 주세요."
        })
    _session.chat_list.append(_chat)

    await _service.process(request_chat_data=_request, session_data=_session)

if '__main__' == __name__:
    asyncio.run(test())
