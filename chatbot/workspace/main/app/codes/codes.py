'''
codes.py

author: sgkim
since: 2025-04-03
'''

from enum import IntEnum, StrEnum, _simple_enum

@_simple_enum(StrEnum)
class CameraState:
    """
    카메라 상태 
    
    CameraState.ON
    CameraState.OFF
    """
    ON               =  "ON"
    OFF              =  "OFF"

@_simple_enum(IntEnum)
class FaceShapeType:
    """
    얼굴형 타입
    
    FaceShapeType.ROUND
    FaceShapeType.SQUARE
    FaceShapeType.OVAL
    FaceShapeType.HEART
    """
    ROUND            =  1
    SQUARE           =  2
    OVAL             =  3
    HEART            =  4
    OBLONG           =  5