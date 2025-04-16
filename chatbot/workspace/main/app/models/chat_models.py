'''
chat_models.py

author: sgkim
since : 2025-03-26
'''
from typing import Optional, Dict, Any
from datetime import datetime

from pydantic import BaseModel, ConfigDict

class RequestChatModel(BaseModel):
    ''' 
    RequestChatModel 
    
    :property msg_no: int: client 에서 요청한 message 의 순번.
    :property request_message: str: client에서 요청한 message.
    :property request_datatime: datetime: 메시지 요청 시간
    '''
    msg_no:Optional[int] = None
    request_message:str
    request_datatime: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True, )

class ChatModel(RequestChatModel):
    ''' 
    ChatModel 
    
    :property msg_no: int: client 에서 요청한 message 의 순번.
    :property request_message: str: client에서 요청한 message.
    :property response_message: str: client의 요청에 대한 응답. None 가능
    :property task_id: str: 작업 ID. None 가능  
    :property data: dict: 추가 결과 데이터. None 가능
    '''
    task_id:Optional[str]           = None
    response_message:Optional[str]  = None
    data:Optional[Dict[str, Any]]   = None

    model_config = ConfigDict(from_attributes=True, )
