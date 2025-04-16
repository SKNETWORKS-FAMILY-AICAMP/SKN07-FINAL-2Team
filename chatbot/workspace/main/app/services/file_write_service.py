''' 
file_write_service.py

파일을 저장하는 서비스

since: 2025-03-17
author: seong guen kim
'''
import uuid
import threading
import logging

from fastapi import UploadFile

from halowing.util.properties.application_properties import ApplicationProperties
from halowing.web.codes import FileState

from repositories.file_repository import FileRepository
from models.fileuploader_model import StoredFileModel
from services.service_helper import FileServiceHelper as fsh

class FileWriteService:
    ''' 파일 저장을 담당하는 서비스 '''

    _instance = None
    _lock = threading.Lock()
    _storage_root:str = None
    _buffer_size_:int = 1024 * 1024  # 1MB
    _repository:FileRepository = None

    _log = logging.getLogger('FileWriteService')

    def __new__(cls):
        '''
        instance를 singletone으로 생성한다.
        '''
        if cls._instance is not None:
            return cls._instance
        
        with cls._lock:
            if cls._instance is not None:
                return cls._instance
            
            cls._instance = super(FileWriteService, cls).__new__(cls)

            cls._property:ApplicationProperties = ApplicationProperties()
            cls._repository = FileRepository()

            return cls._instance

    async def create(self, file: UploadFile) -> StoredFileModel:
        '''
        create file to the path where is defined in application.yml

        :param file: UploadFile, posted file
        '''
        # self.logger.debug('create file: name = %s, size = %s', file.filename, file.size)

        file_id = uuid.uuid4()
        _path, _stored_filename, _ext, _stored_file_path = fsh.get_stored_file_path_info(file_id, file.filename)
        # self.logger.debug('_path=%s, _stored_filename=%s, _ext=%s, _stored_file_path=%s', _path, _stored_filename, _ext, _stored_file_path)


        stored_file = StoredFileModel.model_validate({
            'file_id': file_id,
            'filename': file.filename,
            'file_size': file.size,
            'file_ext': _ext,
            'stored_filename': _stored_filename,
            'path': _path
        })

        # self.logger.debug('stored_file=%s', stored_file)
        try:
            async with self._repository.in_transaction():
                # self._log.debug('before input db : stored_file=%s', stored_file)
                stored_file = await self._repository.create(stored_file)
                fsh.set_url(stored_file)
                # self._log.debug('after input db : stored_file=%s', stored_file)
                with open(_stored_file_path, 'wb') as f:
                    while contents := await file.read(self._buffer_size_):
                        # self.logger.debug('read file: %s', contents)
                        f.write(contents)
        except Exception as e:
            self._log.error('create file error: %s', e)
            try:
                await self._repository.delete_one(file_id=stored_file.file_id)
            except Exception as e2:
                self._log.error('rollback error: %s', e2)
                # self._log.debug('error type: %s', type(e2))
                raise e2
            raise e
        return stored_file

    async def complete_uploading(self, file_id:str) -> StoredFileModel:
        ''' Changes a state of file into FILE_STATE.COMPLETED. '''
        _conn = self._repository.get_connection()

        item = await self._repository.update_state(file_id=file_id, state=FileState.COMPLETED,conn=_conn)
        fsh.set_url(item)
        return item

    async def delete(self, file_id:str) -> bool:
        '''
        Deletes a file. However, the deletion is not performed synchronously.
        '''
        _conn = self._repository.get_connection()
        
        await self._repository.update_state(file_id=file_id, state=FileState.DELETED, conn=_conn)

        return True
