'''
application_context.py

author: sgkim
since : 2025-03-25
'''
import logging
import threading
from contextlib import asynccontextmanager

from typing import Dict, Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import config.logging_configuration
from config.mdb_configuration import MDBConfiguration
from exception.exception_handlers import ExceptionHandlerContext
from session.session_manager import ChatSessionHelper
from services.tasks.task_manager import ChatTaskManagerContext

class ApplicationContext:
    '''
    FastAPI Application Context
    '''
    _instance = None
    _lock = threading.Lock()

    _application_context: Dict[str,Any] = {}

    def __new__(cls):
        '''
        instance를 singletone으로 생성한다.
        '''
        if cls._instance is not None:
            return cls._instance
        
        with cls._lock:
            if cls._instance is not None:
                return cls._instance
            cls._instance = super(ApplicationContext, cls).__new__(cls)

            # logger 초기화.
            cls._log = logging.getLogger('ApplicationContext')

            # FastAPI 객체 생성
            # FastAPI lifespan을 적용하여 객체를 생성한다.
            cls._app = FastAPI(max_request_size=268_435_456, # 256MB
                    lifespan=lifespan
                    )

            # task manager 객체 생성
            cls._task_context = ChatTaskManagerContext()
            cls._task_context.init()

            cls._session_helper = ChatSessionHelper()
            cls._cookie = cls._session_helper.cookie
            cls._verifier = cls._session_helper.verifier

            # ExceptionHandler 등록
            ExceptionHandlerContext(cls._app)

            cls._application_context['app'] = cls._app
            cls._application_context['session_helper'] = cls._session_helper
            cls._application_context['cookie'] = cls._cookie
            cls._application_context['verifier'] = cls._verifier   

            return cls._instance



    def enable_cors(self) -> None:
        '''
        CORS 설정.
        '''
        self._app.add_middleware(
            CORSMiddleware,
            allow_origins=["http://127.0.0.1:8000","http://localhost:8000","*"], # 모든 출처 허용 (보안에 주의)
            allow_credentials=True,
            allow_methods=["*"], # 모든 HTTP 메서드 허용
            allow_headers=["*"], # 모든 HTTP 헤더 허용
        )

    
    def __getitem__(self, key: str) -> Any:
        '''
        Application Context에서 key에 해당하는 value를 반환한다.
        '''
        self._log.debug('ApplicationContext.__getitem__ key=%s', key)
        return self._application_context.get(key)


# lifespan 생성
@asynccontextmanager
async def lifespan(app: FastAPI):
    '''
    main.py 의 app = FastAPI(lifespan=lifespan) 으로 등록 
    '''
    # Application 시작 시점


    
    # DB 객체 생성
    _db_config = MDBConfiguration() 
    # app을 tortoise에 등록

    #DB connection을 초기화 하고, 종료시 connection을 종료한다.
    await _db_config.init_connection()
    await _db_config.create_schemas()

    _db_config.register_tortoise(app)
    
    yield
    
    # Application 종료 시점
    await _db_config.close_connection()
    