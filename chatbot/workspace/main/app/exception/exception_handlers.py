'''
exception_handlers.py

author: sgkim
since: 2025-03-24
'''
import threading
import logging

from fastapi import Request, FastAPI
from fastapi.responses import JSONResponse

from halowing.util.properties.message_properties import ResponseMessage

from tortoise.exceptions import (
    OperationalError,
    DoesNotExist,
    ConfigurationError,
    # FieldError,
    # IntegrityError,
    MultipleObjectsReturned,
    # ParamsError,
)

from halowing.exception.exceptions import (
    NotFoundException
)

from exception.exceptions import (
    FaceNotDetectedException
)

class ExceptionHandlerContext:
    '''
    Exception Handler Context
    '''
    _instance = None
    _lock = threading.Lock()
    _log = logging.getLogger('ExceptionHandlerContext')

    def __new__(cls, *args, **kwargs):
        '''
        instance 생성.
        Singletone pattern
        '''
        if cls._instance is not None:
            return cls._instance
        
        with cls._lock:
            if cls._instance is not None:
                return cls._instance
            cls._instance = super(ExceptionHandlerContext,cls).__new__(cls)

            cls._err_msg = ResponseMessage()
            
            return cls._instance
        
    def __init__(self, app:FastAPI):
        app.add_exception_handler(FaceNotDetectedException, self.face_not_detected_exception_handler)
        app.add_exception_handler(OperationalError, self.tortoise_operational_error_handler)
        app.add_exception_handler(DoesNotExist, self.tortois_does_not_exist_exception_handler)
        app.add_exception_handler(NotFoundException, self.not_found_exception_handler)
        app.add_exception_handler(ConfigurationError, self.tortoise_configuration_error_handler)
        app.add_exception_handler(MultipleObjectsReturned, self.tortoise_multiple_object_returned_error_handler)
        app.add_exception_handler(Exception, self.etc_error_handler)

    async def not_found_exception_handler(self, request: Request, exc: NotFoundException):
        '''
        Custom NotFoundException Handler 
        '''
        return JSONResponse(
            status_code=404,
            content={"message" : f"Requested resource is not founded. request data = {exc.request_data}"},
        )

    async def tortois_does_not_exist_exception_handler(self, request: Request, exc: DoesNotExist):
        '''
        DoesNotExist Handler 
        '''
        return JSONResponse(
            status_code=404,
            content={"message" : f"Requested resource is not founded. request data: {request.path_params}"},
        )

    async def tortoise_operational_error_handler(self, request: Request, exc: OperationalError):
        '''
        OperationalError Handler
        '''
        return JSONResponse(
            status_code=500,
            content={"message" : f'{exc}'},
        )
    
    async def tortoise_configuration_error_handler(self, request: Request, exc: ConfigurationError):
        '''
        ConfigurationError Handler
        '''
        return JSONResponse(
            status_code=500,
            content={"message" : f'{exc}'},
        )
    
    async def tortoise_multiple_object_returned_error_handler(self, request: Request, exc: MultipleObjectsReturned):
        '''
        MultipleObjectsReturned Handler
        '''
        return JSONResponse(
            status_code=500,
            content={"message" : f'{exc}'},
        )

    async def face_not_detected_exception_handler(self, request: Request, exc: FaceNotDetectedException):
        '''
        FaceNotDetectedException Handler 
        '''
        return JSONResponse(
            status_code=500,
            content={"message" : self._err_msg[exc.err_code]},
        )

    async def face_not_detected_exception_handler(self, request: Request, exc: FaceNotDetectedException):
        '''
        FaceNotDetectedException Handler 
        '''
        return JSONResponse(
            status_code=500,
            content={"message" : self._err_msg[exc.err_code]},
        )
    
    async def etc_error_handler(self, request: Request, exc: Exception):
        '''
        기타 Exception Handler 
        '''
        return JSONResponse(
            status_code=500,
            content={"message" : f'{exc}'},
        )
        
