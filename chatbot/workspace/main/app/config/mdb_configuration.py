'''
db_configuration.py

author: sgkim
since : 2025-03-18
'''
import os
import logging
import threading
from typing import AsyncGenerator

from dotenv import load_dotenv

from tortoise import Tortoise
from tortoise.contrib.fastapi import register_tortoise
from tortoise.transactions import in_transaction
from tortoise.connection import connections

load_dotenv()

class MDBConfiguration:
    '''
    DB 연결에 관한 기능
    '''
    _instance = None
    _lock = threading.Lock()
    _log = logging.getLogger('MDBConfiguration')

    DEFAULT_CONNECTION_NAME = 'default'

    def __new__(cls):
        '''
        create instance
        '''
        if cls._instance is not None:
            return cls._instance
        
        with cls._lock:
            if cls._instance is not None:
                return cls._instance
            cls._instance = super(MDBConfiguration,cls).__new__(cls)

            cls.db_url = os.environ.get('db_url')
            cls._log.debug(f'db_url: {cls.db_url}')
            cls.modules = {
                'models': [
                    'entities.glasses_entities',
                    'entities.file_entities',
                    'entities.code_entities',
                ]
            }

            return cls._instance

    async def init_connection(self) -> None:
        '''
        initiate DB Connection. but, it is not connected.
        전체 application life cycle 중에 한 번만 호출 할 것
        '''
        await Tortoise.init(
            db_url=self.db_url,
            modules=self.modules,
            timezone='Asia/Seoul',
        )

    async def create_schemas(self) -> None:
        '''
        schema 를 생성한다. 한 번만 생성해야함.
        Application 이 실행 되기전에 미리 작동 시킬 것 
        '''
        await Tortoise.generate_schemas(safe=True)

    async def close_connection(self):
        '''
        DB Connection을 닫는다.
        전체 application life cycle 중에 한 번만 호출 할 것.
        Application이 종료 되기 직전에 수행되어야 한다.
        '''
        # await Tortoise.close_connections()
        await connections.close_all()

    def register_tortoise(self, app):
        '''
        Registers Tortoise-ORM with set-up at the beginning of FastAPI application's lifespan
        (which allow user to read/write data from/to db inside the lifespan function),
        and tear-down at the end of that lifespan.
        '''
        register_tortoise(
            app,
            db_url=self.db_url,
            modules=self.modules,
            generate_schemas=True,
            add_exception_handlers=False
        )

    def get_connection(self):
        '''
        각 요청마다 Tortoise의 현재 연결을 제공하는 의존성 함수입니다.
        '''
        return connections.get(self.DEFAULT_CONNECTION_NAME)
    
    def in_transaction(self, _conn = None):
        '''
        in_transaction: Transaction 구간 선언

        :usage: 
        config = mdb_configuration()

        config.init_connection()  # 전체 application life cycle 중에 한 번만 할 것

        async with config.in_transaction():
            do_transaction_function()
        config.close_connection()  # 전체 application life cycle 중에 한 번만 할 것

        :param connection_name: if you have multi connection. then you should choice connection with connection_name.
        '''
        return in_transaction(connection_name=_conn if _conn is not None else self.DEFAULT_CONNECTION_NAME)

    
