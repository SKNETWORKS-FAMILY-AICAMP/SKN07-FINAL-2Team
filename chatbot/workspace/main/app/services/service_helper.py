'''
service_helper.py

author: sgkim
since : 2025-03-24
'''
import os
import uuid
import logging

from datetime  import datetime
from typing import Tuple

from PIL import Image

from halowing.util.properties.application_properties import ApplicationProperties

from models.fileuploader_model import StoredFileModel

class FileServiceHelper:
    ''' FileServiceHleper.class '''

    _property:ApplicationProperties = ApplicationProperties()
    _log = logging.getLogger('FileServiceHelper')

    _storage_root = _property['app.file.storage.root']

    @classmethod
    def get_stored_file_path_info(cls, file_id:uuid.UUID, filename:str, middle_fix:str = 'org') -> Tuple[str,str,str,str]:
        '''
        get_stored_file_path_info 파일을 저장할 경로를 반환한다.
        형식은 다름과 같다. f"/{_storage_root}/{parent_path}/{file_id}-{middle_fix}-{filename}"

        :param  file_id:(uuid.UUID) DB에 저장된 pk, uuid.uuid(4)
        :param filename:(str) 원본 file 이름
        :param middle_fix:(str) 저장 파일 이름 만들 때 사용될 중간 접속자.
        :return             _path:(str) parent_path
        :return  _stored_filename:(str) 저장된 파일 명
        :return              _ext:(str) 파일 확장자
        :return _stored_file_path:(str) 파일 경로 uri, f"/{_storage_root}/{parent_path}/{file_id}-{middle_fix}-{filename}"
        '''
        _now:datetime = datetime.now()

        _path:str = _now.strftime('%Y%m%d')
        _ext:str = os.path.splitext(filename)[-1][1:]
        _stored_filename = f'-{middle_fix}-'.join((file_id.hex,filename))

        _parent_path:str = os.path.abspath(os.path.join(cls._storage_root, _path))
        if not os.path.exists(_parent_path):
            os.makedirs(_parent_path)

        _stored_file_path:str = os.path.join(_parent_path,_stored_filename)
        
        return _path, _stored_filename, _ext, _stored_file_path

    @classmethod
    def get_stored_file_path(cls, _path:str, _stored_filename:str) -> str:
        '''
        실제 파일 저장 경로 찾기
        out:(str) 저장된 파일 경로 

        :param  _path:(str) 파일이 저장된 uri
        :param  _stored_filename:(str) 저장된 파일 이름
        '''
        _parent_path:str = os.path.abspath(os.path.join(cls._storage_root, _path))
        return os.path.join(_parent_path,_stored_filename)

    @classmethod
    def set_url(cls, data:StoredFileModel) -> None:
        ''' Set file web url '''
        data.url = cls._property['app.file.url'] + data.path + '/' + data.stored_filename

    @classmethod
    def get_url(cls, _path:str, _stored_filename:str) -> str:
        ''' Set file web url '''
        return cls._property['app.file.url'] + _path + '/' + _stored_filename
    
    @classmethod
    def convert_rgba_to_rgb_img(cls, _stored_file_path:str):
        '''
        RGBA -> RGB
        '''
         # 이미지 로드
        img = Image.open(_stored_file_path).copy()
        cls._log.debug('[convert_img] input img.mode = %s', img.mode)
        if img.mode == 'RGBA':
            img_test = Image.new("RGB", img.size)
            alpha = img.split()[3]
            img_test.paste(img, mask=alpha)
            cls._log.debug('[convert_img] input img_test.mode = %s', img_test.mode)
            return img_test
        else:
            return img
