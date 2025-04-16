''''
user_exceptions.py
'''

class FaceNotDetectedException(Exception):
    '''
    얼굴 탐색 실패 에러.
    '''
    def __init__(self):
        self.err_code = 'err.face_not_detected'
