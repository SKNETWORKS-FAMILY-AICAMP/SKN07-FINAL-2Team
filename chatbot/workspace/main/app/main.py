""" main.py, File Uploader Service main file """
# from typing import List, Optional, Dict
import logging 
from datetime import datetime
from uuid import UUID

# third party library
from fastapi import  Response, Depends, File, UploadFile

from halowing.web.response_model import MessageResponseModel

# Application library
from config.application_context import ApplicationContext
from codes.codes    import CameraState, FaceShapeType
from models.chat_models import ChatModel, RequestChatModel
from models.fileuploader_model import StoredFileModel
from models.glasses_models import GlassesSubModel, FaceShapeModel
from session.session_models import ChatSessionData
from services.chat_service import ChatService
from services.file_write_service import FileWriteService
from services.file_read_service import FileReadService
from services.glasses_read_service import GlassesReadService
from services.face_analyze_service import FaceAnalyzeService
from services.face_read_service import FaceReadService

_log = logging.getLogger('main')

# FastAPI
application_context = ApplicationContext()
app = application_context['app']
_cookie = application_context['cookie']
_verifier = application_context['verifier']
_session_helper = application_context['session_helper']

_log.debug('__cookie__ = %s', _cookie)
_log.debug('__verifier__ = %s', _verifier)  
_log.debug('__session_helper__ = %s', _session_helper)

# Service Instance
chat_service = ChatService()
file_write_service = FileWriteService()
file_read_service  = FileReadService()
glasses_read_service= GlassesReadService()
face_analyze_service = FaceAnalyzeService()
face_read_service = FaceReadService()

@app.get('/welcome/')
async def welcome(response: Response,
                  session_id: UUID = Depends(_cookie)
                  ) -> ChatModel:
    '''
    welcome:
        session을 생성하고 welcome 메세지 보낸다.
        session이 있으면 삭제한다.

    :param response: Response 응답 객체
    :param session_id: UUID session_id 
    '''
    if session_id is not None and isinstance(session_id, UUID) :
        _log.debug('session_id = %s', session_id.hex)
        await _session_helper.remove_session(response, session_id)

    session_id = await _session_helper.create_session(response)
    _chat_data = await chat_service.welcome()
    await _session_helper.add_to_chat_list(session_id, _chat_data)
    return _chat_data

@app.post('/chat/', dependencies=[Depends(_cookie), Depends(_verifier)])
async def chat(
            chat_model:RequestChatModel,
            session_id:UUID  = Depends(_cookie),
            session_data: ChatSessionData = Depends(_verifier)
            ) -> ChatModel:
    '''
    chat : 
        사용자 메시지를 분석하여 적절한 답변 메시지와 result_type을 전송한다.

    :param chat_model: RequestChatModel 사용자 질문이 담긴 객체
    :param session_id: UUID session_id 
    '''
    _log.debug('session_id = %s', session_id.hex)

    _chat_data = await chat_service.process(chat_model, session_data)
    await _session_helper.add_to_chat_list(session_id, _chat_data)
    return _chat_data


@app.delete('/good-bye/', dependencies=[Depends(_cookie), Depends(_verifier)])
async def remove_session(
            response: Response,
            session_id:UUID  = Depends(_cookie)
            ) -> ChatModel:
    ''' session을 삭제한다.'''
    _log.debug('session_id = %s', session_id.hex)

    await _session_helper.remove_session(response, session_id)
    _chat_data = await chat_service.good_bye()
    return _chat_data

@app.get('/file/ready/', dependencies=[Depends(_cookie), Depends(_verifier)])
async def ready_to_upload(
            session_id:UUID  = Depends(_cookie)
            ) -> ChatModel:
    ''' 파일 사용 준비가 끝났습니다. '''
    _log.debug('session_id = %s', session_id.hex)
    _chat_data = await chat_service.ready_to_file_upload()
    await _session_helper.add_to_chat_list(session_id, _chat_data)
    return _chat_data
    

@app.post('/file/', dependencies=[Depends(_cookie), Depends(_verifier)])
async def create_file(
            file: UploadFile = File(...),
            session_id:UUID  = Depends(_cookie),
            ) -> ChatModel:
    ''' create file '''

    # file upload
    _file:StoredFileModel = await file_write_service.create(file)
    _log.debug('StoredFileModel = %s',_file)
    
    # 얼굴형 분석
    try:
        _log.debug('Start Analyzing')
        _face_type, _face_shape_id = await face_analyze_service.analyze(_file)
        _log.debug('_face_type = %s',_face_type)
        _log.debug('End Analyzing')
    except Exception as ex:
        _log.error('Error : %s', ex)
        raise ex

    # 얼굴형 정보 조회
    # _log.debug('Start reading DB')
    _face_shape = await face_read_service.find_one(_face_type)
    # _log.debug('_face_type_model = %s',_face_shape)
    # _log.debug('End reading DB')

    # 응답 데이터 만들기
    _chat = ChatModel.model_validate({
        'msg_no': 9999,
        'request_message': 'file upload',
        'response_message': f'얼굴형 분석을 끝냈습니다. 당신의 얼굴형은 "{_face_type}" 입니다.',
        'task_id': "T05",
        'data': {'file': _file, 'face_type': _face_shape},
        'request_datatime': datetime.today(),
    })
    _log.debug('_chat = %s',_chat)
    
    await _session_helper.add_analyze_data(session_id, _file, _face_shape, _chat)
    return _chat

@app.get('/file/{file_id}/', dependencies=[Depends(_cookie), Depends(_verifier)])
async def get_file(file_id:str) -> StoredFileModel:
    ''' get file '''
    file_info = await file_read_service.get(file_id)
    return file_info

@app.get('/webcam/state/{state}/', dependencies=[Depends(_cookie), Depends(_verifier)])
async def change_webcam_state(
    state: CameraState,
    session_id:UUID  = Depends(_cookie)
    ) -> MessageResponseModel:
    '''
    webcam 상태 설정
    :param session_id: UUID session_id 
    '''
    await _session_helper.set_camera_state(session_id = session_id, camera_state = state)
    _rs = MessageResponseModel()
    _rs.messages.append(f'camera state is {state.value}')
    return _rs

@app.get('/glasses/{glasses_sub_id}/', dependencies=[Depends(_cookie), Depends(_verifier)])
async def get_glasses_info(
    glasses_sub_id:int,
    session_id:UUID  = Depends(_cookie),
    ) -> ChatModel:
    '''
    안경 상세 정보

    :param glasses_id: 안경 ID
    :param session_id: UUID session_id 
    '''
    _log.debug('id = %s', glasses_sub_id)

    _rs = await glasses_read_service.get(glasses_sub_id)
    await _session_helper.add_glasses(session_id=session_id,glasses=_rs)
    _chat_data = ChatModel.model_validate({
        'msg_no': 9999,
        'request_message': 'select a glasses id= ' + str(glasses_sub_id),
        'response_message': f'선택하신 안경은 {_rs.brand_name} 에서 만든 {_rs.product_name} 안경입니다. 색상은 {_rs.color_code.color_name} 입니다. 상세 정보는 <a href="{_rs.url}" target="_blank" style="font-weight: bold;font-color:red;">"여기"</a>에서 확인 가능하십니다.  안경 피팅을 해보시겠습니까?',
        'task_id': "T99",
        'data': {'glasses': _rs},
        'request_datatime': datetime.today(),
    })
    _log.debug('_chat = %s',_chat_data)
    await _session_helper.add_to_chat_list(session_id, _chat_data)
    return _chat_data

