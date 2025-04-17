'''
fitting_service.py

This module provides functions to handle image processing tasks such as resizing 
and converting images.

author: sgkim
since: 2025-04-01
'''
import logging
import threading
from uuid import uuid4
import cv2
import dlib  # dlib은 얼굴 감지 및 특징점 예측을 위한 라이브러리입니다. cmake 설치 필요 yum install cmake
import numpy as np

from PIL import Image

from halowing.util.properties.message_properties import ResponseMessage
from halowing.util.properties.application_properties import ApplicationProperties


from exception.exceptions import FaceNotDetectedException
from models.chat_models import ChatModel
from models.fileuploader_model import StoredFileModel
from repositories.file_repository import FileRepository
from services.service_helper import FileServiceHelper as fsh
from session.session_models import ChatSessionData

class FittingService:
    '''
    이미지 처리 서비스 클래스입니다.
    이 클래스는 사용자 얼굴 사진과 안경 이미지의 사진 합성을 처리합니다.
    '''
    
    _instance = None
    _lock = threading.Lock()
    _log = logging.getLogger('FittingService')
    
    _task_id = 'T08'

    def __new__(cls):
        if cls._instance is not None:
            return cls._instance
        
        with cls._lock:
            if cls._instance is not None:
                return cls._instance
            cls._instance = super(FittingService, cls).__new__(cls)
            cls._res_msg = ResponseMessage()
            _properties = ApplicationProperties()
            cls._dat_path = _properties['app.ml.model.face_shape_landmarks']
            cls._file_repository = FileRepository()
            return cls._instance
        
    async def fitting(self, session: ChatSessionData, model:ChatModel) -> ChatModel:
        '''
        안경 피팅.
        '''
        if session.face_type is None:
            # 얼굴형이 판독 안된 경우
            model.response_message = self._res_msg['res.' + self._task_id + '-01']
            return model

        if len(session.glassess) == 0:
            # 안경을 선택하지 않은 경우
            model.response_message = self._res_msg['res.' + self._task_id + '-02']
            return model
        
        # 얼굴 이미지 불러오기
        _face_file = session.upload_images[-1]
        _face_image_path = fsh.get_stored_file_path(_face_file.path, _face_file.stored_filename)
        _face_image = self.__read_image_file(_face_image_path)

        # 안경 이미지 불러 오기기
        _glasses_file = session.glassess[-1].images[0]
        _glasses_image_path = fsh.get_stored_file_path(_glasses_file.path, _glasses_file.stored_filename)
        #안경 이미지, alpha가 들어 있어서 PIL 사용 안함.
        # _glasses_image = self.__get_image_file(glasses_image_path)
        _glasses_image = cv2.imread(_glasses_image_path, cv2.IMREAD_UNCHANGED)

        # 출력 파일 경로와 DB 저장 모델 생성.
        _output_file, _output_file_path = self.__get_output_file_model(_face_file.filename)

        # 안경 이미지와 얼굴 이미지 합성
        mixed_image = self.__merge_glasses_and_face(
            face_image = _face_image,
            glasses_image= _glasses_image)

        # 결과 이미지 저장.
        self.__write_image_file( _output_file_path, mixed_image)

        self._log.debug('_face_image_path=%s, _glasses_image_path=%s, _output_file_path = %s',
                         _face_image_path,    _glasses_image_path,    _output_file_path)
        

        # 파일 생성 정보 DB 저장
        async with self._file_repository.in_transaction():
            _output_file = await self._file_repository.create(_output_file)

            # 생성된 파일의 url 값 설정: 
            fsh.set_url(_output_file)

            # 생성된 url을 응답 메시지에 추가
            model.response_message = self._res_msg['res.' + self._task_id ]
            model.response_message += '<br/><img src="' + _output_file.url + '" style="width: 100%; margin-top: 10px; " />'

        return model
    
    def __merge_glasses_and_face(self, face_image, glasses_image):
        """
        사람 얼굴 사진에 안경 사진을 합성합니다.

        Args:
        :param     face_image_path: (str): 얼굴 사진 경로
        :param  glasses_image_path: (str): 안경 사진 경로
        :return : (MatLike) OpenCV Numpy Array
        """

        # 얼굴 감지기 및 얼굴 특징점 예측기 초기화
        detector = dlib.get_frontal_face_detector()
        predictor = dlib.shape_predictor(self._dat_path) # 다운로드 필요

        # 얼굴 감지
        faces = detector(face_image)

        if len(faces) == 0:
            self._log.debug("얼굴이 감지되지 않았습니다.")
            raise FaceNotDetectedException()

        # 첫 번째 얼굴에만 안경 합성
        face = faces[0]
        landmarks = predictor(face_image, face)

        # 랜드마크 표시: 눈 안쪽 과 눈썹 바깥쪽 노란색
        # for i in range(68):
        #     x = landmarks.part(i).x
        #     y = landmarks.part(i).y
        #     if i in [17,26,39,42]:
        #         cv2.circle(face_image, (x, y), 2, (0, 255, 255), -3) # 붉은색 원으로 표시
        #     else:
        #         cv2.circle(face_image, (x, y), 2, (0, 255, 0), -3) # 초록색 원으로 표시

        # 눈과 눈썹 위치를 이용한 계산 용 좌표 조회
        left_eyebrow_points = np.array([(landmarks.part(17).x, landmarks.part(17).y),
                                        # (landmarks.part(21).x, landmarks.part(21).y)])
                                        (landmarks.part(39).x, landmarks.part(39).y)])
        right_eyebrow_points = np.array(
                                    [(landmarks.part(42).x, landmarks.part(42).y),
                                    #  [(landmarks.part(22).x, landmarks.part(22).y),
                                    (landmarks.part(26).x, landmarks.part(26).y)])
        
        self._log.debug('[] left_eyebrow_points: %s, right_eyebrow_points: %s',
                        left_eyebrow_points, right_eyebrow_points)

        # 안경 크기 조정 및 회전
        # 안경 회전 각도 계산
        angle = np.arctan2(right_eyebrow_points[1][1] - left_eyebrow_points[0][1],
                        right_eyebrow_points[1][0] - left_eyebrow_points[0][0]) * 180 / np.pi * -1

        # 안경 회전
        rotation_matrix = cv2.getRotationMatrix2D((glasses_image.shape[1] / 2, glasses_image.shape[0] / 2), angle, 1)
        glasses_rotated = cv2.warpAffine(glasses_image, rotation_matrix, (glasses_image.shape[1], glasses_image.shape[0]))

        # 안경 이미지 크롭
        glasses_rotated = self.__crop_glasses(glasses_rotated)

        # 안경 크기 조정 
        glasses_width = int(np.linalg.norm(left_eyebrow_points[0] - right_eyebrow_points[1]) * 1.2)
        glasses_height = int(glasses_width * glasses_rotated.shape[0] / glasses_rotated.shape[1])
        glasses_rotated = cv2.resize(glasses_rotated, (glasses_width, glasses_height), interpolation=cv2.INTER_AREA)

        # cv2.rectify3Collinear

        # 안경 합성 위치 계산
        top_left = (0,0)

        self._log.debug('angle = %s', angle)

        top_left = (int( (left_eyebrow_points[1][0] + right_eyebrow_points[0][0] - glasses_rotated.shape[1] ) / 2 ),
                    int( (left_eyebrow_points[1][1] + right_eyebrow_points[0][1] - glasses_rotated.shape[0] ) / 2 ))
        
        # 안경 합성
        # for i in range(glasses_rotated.shape[0]):
        #     for j in range(glasses_rotated.shape[1]):
        #         if glasses_rotated[i, j, 3] > 0:  # 투명한 부분 제외
        #             face_image[top_left[1] + i, top_left[0] + j] = glasses_rotated[i, j, :3]
        
        # 전경 이미지에서 알파 채널 분리
        alpha = glasses_rotated[:, :, 3] / 255.0
        alpha = np.expand_dims(alpha, axis=2)

        # 배경 이미지의 해당 영역 추출
        face_image_cropped = face_image[top_left[1]:top_left[1] + glasses_rotated.shape[0],
                                        top_left[0]:top_left[0] + glasses_rotated.shape[1]].astype(float)
        glasses_rgb = glasses_rotated[:, :, :3].astype(float)

        # 알파 블렌딩을 사용하여 합성
        blended = alpha * glasses_rgb + (1 - alpha) * face_image_cropped
        face_image[top_left[1]:top_left[1] + glasses_rotated.shape[0],
                   top_left[0]:top_left[0] + glasses_rotated.shape[1]] = blended.astype(np.uint8)

        return face_image

    def __get_output_file_model(self, _filename:str) -> tuple[StoredFileModel, str] :
        '''
        파일 명으로 output file 정보 만들기.
        :param  _filename:(str) 입력 파일명
        :return          :(tuple[StoredFileModel, str]) DB 저장 객체, 저장 URI
        '''
        _file_id = uuid4()
        _path, _stored_filename, _ext, _stored_file_path = fsh.get_stored_file_path_info(
                                                                file_id=_file_id,
                                                                filename=_filename,
                                                                middle_fix='fit'
                                                            )
        _output_file = StoredFileModel.model_validate({
            'file_id': _file_id,
            'filename': _filename,
            'file_ext': _ext,
            'stored_filename': _stored_filename,
            'path': _path
        })
        return _output_file, _stored_file_path

    def __crop_glasses(self, image):
        """
        안경 이미지에서 불투명한 부분만 crop합니다.

        Args:
            image_path (str): 안경 이미지 경로
            output_path (str): crop된 이미지 저장 경로
        """
        if image is None:
            self._log.error("이미지를 불러올 수 없습니다: ")
            return

        # 알파 채널(투명도) 분리
        alpha_channel = image[:, :, 3]

        # 불투명한 부분의 좌표 찾기
        y_coords, x_coords = np.where(alpha_channel > 0)

        # 불투명한 부분의 경계 계산
        min_x, max_x = np.min(x_coords), np.max(x_coords)
        min_y, max_y = np.min(y_coords), np.max(y_coords)

        # 이미지 crop
        croped_image = image[min_y:max_y + 1, min_x:max_x + 1]

        return croped_image
    
    def __read_image_file(self, _file_path:str):
        '''
        파일명에 한글 있을 때, opencv 에서 에러 발생하는 것 수정
        '''
        img_pil = Image.open(_file_path).copy()
        img_cv2 = np.array(img_pil)

        # PIL은 RGB로 읽기 때문에 OpenCV의 BGR 형식으로 변환 (선택 사항)
        img_cv2 = cv2.cvtColor(img_cv2, cv2.COLOR_RGB2BGR )

        return img_cv2
    
    def __write_image_file(self, _file_path:str, _file) -> None:
        '''
        파일 저장. 한글 파일 깨지는 문제 수정을 위해 
        :param _file_path:(str) 파일 저장 경로
        :param      _file:(MatLike) opencv Image
        '''
        # cv2.imwrite(_file_path, _file)

        # OpenCV 로 작성된 파일을 PIL로 변환
        img_pil = Image.fromarray(cv2.cvtColor(_file, cv2.COLOR_BGR2RGB))

        img_pil.save(_file_path)
        self._log.debug("결과 이미지가 %s에 저장되었습니다.", _file_path)
