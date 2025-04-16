'''
session_models.py

author: sgkim
since : 2025-03-26
'''
from uuid import UUID
from datetime import datetime
from typing import List
from pydantic import BaseModel

from codes.codes import CameraState
from models.fileuploader_model import StoredFileModel
from models.glasses_models import GlassesSubModel, FaceShapeModel
from models.chat_models import ChatModel

class ChatSessionData(BaseModel):
    ''' ChatSessionData '''
    session_id: UUID
    chat_list: List[ChatModel] = []
    camera_state: CameraState = CameraState.OFF
    upload_images: List[StoredFileModel] = []
    glassess: List[GlassesSubModel] =[]
    face_type: FaceShapeModel = None

    created_datetime: datetime

    def __str__(self):
        return f"session_id: {self.session_id}, chat_list: {self.chat_list},\
                camera_state: {self.camera_state}, upload_images: {self.upload_images},\
                face_type: {self.face_type},\
                created_datetime: {self.created_datetime}"
    
    def __repr__(self):
        return f"ChatSessionData[session_id={self.session_id}, chat_list={self.chat_list},\
                camera_state={self.camera_state}, upload_images={self.upload_images},\
                face_type: {self.face_type},\
                created_datetime={self.created_datetime}]"
