'''
image_mix_test.py
'''
import logging
from services.fitting_service import FittingService
import config.logging_configuration


_log = logging.getLogger('image_mix_test')

def test():
    '''
    image 합성 테스트
    '''
        # 사용 예시
    face_image_path = "./main/test/tmp/face.jpg"  # 얼굴 사진 경로
    glasses_image_path = "./main/test/tmp/glasses.png"  # 안경 사진 경로 (투명 배경 권장)
    output_image_path = "./main/test/tmp/face_with_glasses.jpg" # 결과 사진 저장 경로

    image_service = FittingService()
    # image_service.resize_image("input.jpg", "output.jpg", 800, 600)  # 이미지 크기 조정 예시
    _img_cv = image_service.fitting(face_image_path, glasses_image_path) # 안경 합성 예시
    
if __name__ == '__main__':
    _log.info('################## START TEST #################')
    test()
    _log.info('################### END TEST  #################')



