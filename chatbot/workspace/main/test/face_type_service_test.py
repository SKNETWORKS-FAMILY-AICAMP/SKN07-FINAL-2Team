'''
face_type_service_test.py
'''
import logging
import asyncio
from services.face_analyze_service import FaceAnalyzeService
import config.logging_configuration

_log = logging.getLogger('face_type_service_test')
_service = FaceAnalyzeService()

def test():
    # 함수 호출 
    face_image_path = "./main/test/tmp/test_img.png"  # 얼굴 사진 경로
    _label = _service.get_facetype(face_image_path)
    _log.info(f'face type : {_label}')


if __name__ == '__main__':
    _log.info('################## START TEST #################')
    test()
    _log.info('################### END TEST  #################')