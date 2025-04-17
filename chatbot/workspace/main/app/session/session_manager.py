'''
session_manager.py

author: sgkim
since : 2025-03-26
'''
import sys
import logging
from datetime import datetime
from typing import Optional
import threading
from uuid import UUID, uuid4

from fastapi import HTTPException, Response
from fastapi_sessions.backends.implementations.in_memory_backend import InMemoryBackend
from fastapi_sessions.session_verifier import SessionVerifier
from fastapi_sessions.frontends.implementations import SessionCookie, CookieParameters

from codes.codes import CameraState
from models.chat_models import ChatModel
from models.fileuploader_model import StoredFileModel
from models.glasses_models import GlassesSubModel, FaceShapeModel
from session.session_models import ChatSessionData


class BasicVerifier(SessionVerifier[UUID, ChatSessionData]):
    ''' BasicVerifier '''
    def __init__(
        self,
        *,
        identifier: str,
        auto_error: bool,
        backend: InMemoryBackend[UUID, ChatSessionData],
        auth_http_exception: HTTPException,
    ):
        self._identifier = identifier
        self._auto_error = auto_error
        self._backend = backend
        self._auth_http_exception = auth_http_exception

    @property
    def identifier(self):
        return self._identifier

    @property
    def backend(self):
        return self._backend

    @property
    def auto_error(self):
        return self._auto_error

    @property
    def auth_http_exception(self):
        return self._auth_http_exception

    def verify_session(self, model: ChatSessionData ) -> bool:
        """If the session exists, it is valid"""
        return True


class ChatSessionHelper:
    ''' Session 정보 생성 도구. '''
    _instance = None
    _lock = threading.Lock()

    _log = logging.getLogger('ChatSessionHelper')

    def __new__(cls, cookie_name:str='cookie', identifier:str="general_verifier"):
        '''
        instance를 singletone으로 생성한다.
        '''
        if cls._instance is not None:
            return cls._instance
        
        with cls._lock:
            if cls._instance is not None:
                return cls._instance
            cls._instance = super(ChatSessionHelper, cls).__new__(cls)

            cls._cookie_name = cookie_name
            cls._identifier = identifier
            cls._cookie = cls.__cookie()
            cls._backend =  InMemoryBackend[UUID, ChatSessionData]()
            cls._verifier = cls.__verifier()

            return cls._instance
        
    @classmethod
    def __cookie(cls):
        ''' __cookie '''
        cookie_params = CookieParameters()
        cookie = SessionCookie(
            cookie_name= cls._cookie_name,
            identifier= cls._identifier,
            auto_error=False,
            secret_key="DONOTUSE",
            cookie_params=cookie_params,
        )
        return cookie
    
    @classmethod
    def __verifier(cls):
        ''' __verifier '''
        verifier = BasicVerifier(
            identifier= cls._identifier,
            auto_error=True,
            backend= cls._backend,
            auth_http_exception=HTTPException(status_code=403, detail="invalid session"),
        )
        return verifier

    @property
    def cookie(self):
        ''' cookie '''
        return self._cookie

    @property
    def backend(self):
        ''' backend '''
        return self._backend

    @property
    def verifier(self):
        ''' verifier '''
        return self._verifier
    
    async def create_session(self, _response:Response) -> UUID:
        ''' create_session'''
        _session_id = uuid4()
        _data = ChatSessionData(session_id=_session_id, created_datetime=datetime.today())
        # self._log.debug('[%s] session_id : %s, data : %s', sys._getframe().f_code.co_name, _session_id.hex, _data)
        
        await self._backend.create(_session_id, _data)
        self._cookie.attach_to_response(response=_response, session_id=_session_id)

        return _session_id

    async def get_session_data(self, session_id:UUID) -> Optional[ChatSessionData]:
        ''' get_session_data '''
        session_data: ChatSessionData = await self._backend.read(session_id=session_id)
        if session_data is None:
            raise HTTPException(status_code=403, detail="invalid session")
        # self._log.debug('[%s] session_data : %s', sys._getframe().f_code.co_name, session_data)
        return session_data
    
    async def remove_session(self, response:Response, session_id:UUID):
        ''' remove_session'''
        # self._log.debug('[%s] session_id : %s', sys._getframe().f_code.co_name, session_id.hex)
        try:
            session_data: ChatSessionData = await self._backend.read(session_id=session_id)
            if session_data is None:
                # self._log.debug('[%s] session_data is None, session_id = %s', sys._getframe().f_code.co_name, session_id.hex)
                return None
            await self._backend.delete(session_id)
            self._cookie.delete_from_response(response)
        except Exception as ex:
            self._log.error('[%s] Error: %s', sys._getframe().f_code.co_name,ex)

    async def add_to_chat_list(self, session_id: UUID, data: ChatModel )-> None:
        ''' save_data '''
        # self._log.debug('[%s] session_id : %s, data = %s', sys._getframe().f_code.co_name, session_id.hex, data)
        session_data: ChatSessionData = await self._backend.read(session_id=session_id)
        # self._log.debug('[%s] session_data before : %s', sys._getframe().f_code.co_name, session_data)
        session_data.chat_list.append(data)
        # self._log.debug('[%s] session_data after  : %s', sys._getframe().f_code.co_name, session_data)
        await self._backend.update(session_id=session_id, data=session_data )

    async def set_camera_state(self, session_id: UUID, camera_state: CameraState) -> None:
        ''' 
        카메라 상태 설정

        :param   session_id: 사용자 Session ID, 
        :param camera_state: bool 카메라 상태 값. True: 켜져있음., False: 꺼져있음.
        '''
        session_data: ChatSessionData = await self._backend.read(session_id=session_id)
        
        # if camera_state:
        #     session_data.camera_state = CameraState.ON
        # else:
        #     session_data.camera_state = CameraState.OFF

        session_data.camera_state = camera_state
        # self._log.debug('[%s] session_data : %s', sys._getframe().f_code.co_name, session_data)
        await self._backend.update(session_id=session_id, data=session_data )

    async def add_image(self, session_id: UUID, file_model:StoredFileModel) -> None:
        '''
        사용자 얼굴 사진 목록 저장

        :param   session_id: 사용자 Session ID, 
        :param   file_model: StoredFileModel, 업로드한 이미지의 정보보 
        '''
        session_data: ChatSessionData = await self._backend.read(session_id=session_id)
        session_data.upload_images.append(file_model)
        # self._log.debug('[%s] session_data : %s', sys._getframe().f_code.co_name, session_data)
        await self._backend.update(session_id=session_id, data=session_data )

    async def add_glasses(self, session_id: UUID, glasses: GlassesSubModel) -> None:
        '''
        사용자가 선택한 안경 정보 저장
        '''
        session_data: ChatSessionData = await self._backend.read(session_id=session_id)
        session_data.glassess.append(glasses)
        # self._log.debug('[%s] session_data : %s', sys._getframe().f_code.co_name, session_data)
        await self._backend.update(session_id=session_id, data=session_data )

    async def add_face_type(self, session_id: UUID, face_type: FaceShapeModel) -> None:
        '''
        사용자가 선택한 안경 정보 저장
        '''
        session_data: ChatSessionData = await self._backend.read(session_id=session_id)
        session_data.face_type = face_type
        # self._log.debug('[%s] session_data : %s', sys._getframe().f_code.co_name, session_data)
        await self._backend.update(session_id=session_id, data=session_data )

    async def add_analyze_data(
        self,
        session_id: UUID,
        file_model:StoredFileModel,
        face_type: FaceShapeModel,
        data: ChatModel
    ) -> None:
        '''
        얼굴형 분석 데이터 일괄 저장.
        '''
        session_data: ChatSessionData = await self._backend.read(session_id=session_id)
        session_data.face_type = face_type
        session_data.chat_list.append(data)
        session_data.upload_images.append(file_model)
        # self._log.debug('[%s] session_data : %s', sys._getframe().f_code.co_name, session_data)
        await self._backend.update(session_id=session_id, data=session_data )
