'''
face_type_service.py

얼굴형 분석
'''
import threading
import logging

# import matplotlib.pyplot as plt
import numpy as np
import cv2
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.applications.vgg16 import preprocess_input
from mtcnn import MTCNN

from halowing.util.properties.application_properties import ApplicationProperties

from exception.exceptions import FaceNotDetectedException
from models.fileuploader_model import StoredFileModel
from services.service_helper import FileServiceHelper as fsh

class FaceAnalyzeService:
    '''
    얼굴형 분석 서비스
    '''

    _instance = None
    _lock = threading.Lock()

    _log = logging.getLogger('FaceTypeService')

    def __new__(cls):
        '''
        instance를 singletone으로 생성한다.
        '''
        if cls._instance is not None:
            return cls._instance
        
        with cls._lock:
            if cls._instance is not None:
                return cls._instance
            cls._instance = super(FaceAnalyzeService, cls).__new__(cls)

            cls._property:ApplicationProperties = ApplicationProperties()

            # 모델 로드
            _model_path = cls._property['app.ml.model.face_shape_classifier'] # './saved_face_models/vgg16.keras'
            # cls._model = tf.keras.models.load_model(_model_path)
            cls._model = load_model(_model_path)

            # MTCNN 얼굴 감지 모델 초기화
            cls.detector = MTCNN()

            return cls._instance

    async def analyze(self, _file:StoredFileModel) -> tuple[str, int]:
        '''
        얼굴형을 분석한다.

        :param _file: 얼굴형 분석할 파일
        '''
        _stored_file_path:str = fsh.get_stored_file_path(_file.path, _file.stored_filename)
        self._log.debug('_stored_file_path = %s',_stored_file_path )

        _face_type, _face_shape_id = self.get_facetype(_stored_file_path)
        self._log.debug('_face_type = %s, _face_shape_id = %s',_face_type, _face_shape_id )

        return _face_type.lower(), _face_shape_id
    
    
        
    def get_facetype(self, _stored_file_path: str) -> tuple[str, int]:
        '''
        얼굴형 분석 
        '''
        # GPU 사용을 비활성화하여 CPU만 사용하도록 설정
        tf.config.set_visible_devices([], 'GPU')

        # 카테고리 및 레이블 맵 정의
        # categories = ['Heart', 'Oblong', 'Oval', 'Round', 'Square']
        label_map = {0: 'Heart', 1: 'Oblong', 2: 'Oval', 3: 'Round', 4: 'Square'}

        # 이미지 로드
        img = fsh.convert_rgba_to_rgb_img(_stored_file_path)
        img_rgb = np.array(img)

        # 얼굴 감지
        faces = self.detector.detect_faces(img_rgb)

        if len(faces) == 0:
            self._log.error("No face detected")
            raise FaceNotDetectedException()
            
        x, y, w, h = faces[0]['box']
        x2, y2 = x + w, y + h
        # face_img = img_rgb[y:y2, x:x2]

        # 얼굴을 비율을 맞춰 리사이즈
        face_resized_with_padding = self.extract_face(img_rgb, target_size=(224, 224))

        self._log.debug('check point 01')
        if face_resized_with_padding is None:
            self._log.error("얼굴 추출 실패")
            raise FaceNotDetectedException()
        
        self._log.debug('check point 02')
        # 이미지를 numpy 배열로 변환하고 VGG16에 맞게 전처리
        img_array = np.expand_dims(face_resized_with_padding, axis=0)
        self._log.debug('check point 02-1: %s', img_array.shape)

        img_array = preprocess_input(img_array)
        self._log.debug('check point 03: %s', img_array.shape)

        # 모델 예측
        predictions = self._model.predict(img_array, verbose=0)
        self._log.debug('check point 03-1')

        predicted_class = np.argmax(predictions, axis=1)
        # confidence = np.max(predictions)

        self._log.debug('check point 04')
        predicted_label = label_map[predicted_class[0]]

        return predicted_label, predicted_class[0]

    # MTCNN 활용 얼굴 탐지 함수 
    def extract_face(self, img, target_size=(224, 224)):
        '''
        MTCNN 활용 얼굴 탐지 함수 
        '''
        self._log.debug('Start detect face')
        results = self.detector.detect_faces(img)
        if results == []:
            new_face = self.crop_and_resize_with_aspect(img, target_w=224, target_h=224)
        else:
            x1, y1, width, height = results[0]['box']
            x2, y2 = x1 + width, y1 + height
            # face = img[y1:y2, x1:x2]

            adj_h = 10
            new_y1 = max(0, y1 - adj_h)
            new_y2 = min(img.shape[0], y1 + height + adj_h)
            new_height = new_y2 - new_y1

            adj_w = int((new_height - width) / 2)
            new_x1 = max(0, x1 - adj_w)
            new_x2 = min(img.shape[1], x2 + adj_w)
            new_face = img[new_y1:new_y2, new_x1:new_x2]

        sqr_img = cv2.resize(new_face, target_size)

        self._log.debug('End detect face')

        return sqr_img

    def crop_and_resize_with_aspect(self, image, target_w=224, target_h=224):
        '''
        이미지 비율 crop & resize 함수
        '''
        img_h, img_w, channels = image.shape  # 이미지 높이, 너비, 채널
        target_aspect_ratio = target_w / target_h
        input_aspect_ratio = img_w / img_h
        #가로가 긴 경우
        if input_aspect_ratio > target_aspect_ratio:
            resize_w = int(input_aspect_ratio * target_h)
            resize_h = target_h
            img_resized = cv2.resize(image, (resize_w, resize_h))
            crop_left = int((resize_w - target_w) / 2)
            crop_right = crop_left + target_w
            new_img = img_resized[:, crop_left:crop_right]
        #세로가 긴 경우
        elif input_aspect_ratio < target_aspect_ratio:
            resize_w = target_w
            resize_h = int(target_w / input_aspect_ratio)
            img_resized = cv2.resize(image, (resize_w, resize_h))
            crop_top = int((resize_h - target_h) / 4)
            crop_bottom = crop_top + target_h
            new_img = img_resized[crop_top:crop_bottom, :]
        else:
            new_img = cv2.resize(image, (target_w, target_h))

        return new_img
    