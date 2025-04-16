'''
base_tasks.py

author: sgkim
since: 2023-03-31
'''
from logging import getLogger
from abc import ABC, abstractmethod

from openai import OpenAI

from pydantic import BaseModel

from halowing.util.properties.application_properties import ApplicationProperties
from halowing.util.properties.message_properties import ResponseMessage

from codes.codes import CameraState
from models.chat_models import ChatModel
from services.glasses_read_service import GlassesReadService
from services.face_read_service import FaceReadService
from services.fitting_service import FittingService
from session.session_models import ChatSessionData

class AbstractTask(ABC):
    """
    Abstract base class for all tasks.
    """
    TALK_ID = 'T99'

    def __init__(self, task_id: str, task_name: str) -> None:
        self.task_id = task_id
        self.task_name = task_name
        self._property:ApplicationProperties = ApplicationProperties()
        self._res_msg = ResponseMessage()
        self._log = getLogger(self.__class__.__name__)

    @abstractmethod
    async def run(self, session: ChatSessionData, model:ChatModel) -> ChatModel:
        """
        Run the task with the given arguments.
        """
        # pass

    def get_id(self):
        '''
        task_id 
        '''
        return self.task_id

class CommandAnalysisTask(AbstractTask):
    """
    Analyze command.
    """
    # def __init__(self, task_id:str, task_name:str) -> None:
    #     super(CommandAnalysisTask,self).__init__(task_id, task_name)

    async def run(self, session: ChatSessionData, model:ChatModel):
        """
        Run a task.   "
        """
        if model.task_id != self.task_id:
            return None

        model.response_message = self._res_msg['res.' + self.task_id]
        self._log.debug('response = %s',model)

        return model

class CommandAnalysisTask2(AbstractTask):
    """
    Analyze command.

    응답의 task_id가 특별히 action을 하는 것이 아니고, 메시지만이 의미가 있을 때 사용.
    """
    # def __init__(self, task_id:str, task_name:str) -> None:
    #     super(CommandAnalysisTask,self).__init__(task_id, task_name)

    async def run(self, session: ChatSessionData, model:ChatModel):
        """
        Run a task.   "
        """
        if model.task_id != self.task_id:
            return None

        model.response_message = self._res_msg['res.' + self.task_id]
        self._log.debug('response = %s',model)

        if len(model.task_id.split('-')) > 0:
            model.task_id = self.TALK_ID

        return model

class SelectCameraTask(AbstractTask):
    """
    Select camera.
    """
    def __init__(self) -> None:
        super(SelectCameraTask,self).__init__('T01', 'camera select')
        self._property:ApplicationProperties = ApplicationProperties()
        self._res_msg = ResponseMessage()

    async def run(self, session: ChatSessionData, model:ChatModel):
        """
        Run a task.   
        """
        if model.task_id != self.task_id:
            return None
        if session.camera_state is None or session.camera_state == CameraState.OFF:
            model.response_message = self._res_msg['res.' + self.task_id + '-00']
            model.task_id = 'T09'
        else:
            model.response_message = self._res_msg['res.' + self.task_id]
        self._log.debug('response = %s',model)

        return model

class FaceListTask(AbstractTask):
    """
    Listing glasseses.
    """
    def __init__(self) -> None:
        super(FaceListTask,self).__init__('T03', 'all face type list')
        self._service = FaceReadService()

    async def run(self, session: ChatSessionData, model:ChatModel):
        """
        Run a task.   "
        """
        if model.task_id != self.task_id:
            return None

        model.response_message = self._res_msg['res.' + self.task_id]
        _rs =  await self._service.get_list(offset=0, limit=100, )
        model.data = {'face_type_list': _rs.datas}

        self._log.debug('response = %s',model)

        return model

class GlassesListTask(AbstractTask):
    """
    Listing glasseses.
    """
    _log = getLogger('GlassesListTask')

    def __init__(self) -> None:
        super(GlassesListTask,self).__init__('T06', 'glasses list')
        self._service = GlassesReadService()

    async def run(self, session: ChatSessionData, model:ChatModel):
        """
        Run a task.   "
        """
        if model.task_id != self.task_id:
            return None

        self._log.debug('face_type = %s',session.face_type)
        if session.face_type is None:
            model.response_message = self._res_msg['res.' + self.task_id + '-00']
            model.task_id = self.TALK_ID
            return model

        model.response_message = self._res_msg['res.' + self.task_id]

        _condition = {
            'glasses__glasses_type__face_shapes__face_shape_name': session.face_type.face_shape_name
        }
        
        _rs =  await self._service.get_list(offset=0, limit=100, condition=_condition)
        model.data = {'glasses_list': _rs.datas}

        self._log.debug('response = %s',model)

        return model
    
class ChosenGlasses(BaseModel):
    '''
    선택된 안경 모델.
    '''
    glasses_sub_id: int


class GlassesDetailTask(AbstractTask):
    """
    Listing glasseses.
    """
    _log = getLogger('GlassesDetailTask')
    def __init__(self) -> None:
        super(GlassesDetailTask,self).__init__('T07', 'glasses')
        self._service = GlassesReadService()
        self._client = OpenAI()

    async def run(self, session: ChatSessionData, model:ChatModel):
        """
        Run a task.   "
        """
        if model.task_id != self.task_id:
            return None
        
        if session.face_type is None:
            model.response_message = self._res_msg['res.' + self.task_id + '-03']
            model.task_id = self.TALK_ID
            return model

        _condition = {
            'glasses__glasses_type__face_shapes__face_shape_name': session.face_type.face_shape_name
        }
        
        _rs =  await self._service.get_list(offset=0, limit=100, condition=_condition)

        if len(_rs.datas) == 0:
            model.response_message = self._res_msg['res.' + self.task_id + '-01']
            model.task_id = self.TALK_ID
            return model

        # AI에서 안경 선택 
        _chosen_glasses: ChosenGlasses = await self.get_glasses_by_ai(model.request_message, _rs.datas)
        if _chosen_glasses is None:
            model.response_message = self._res_msg['res.' + self.task_id + '-02']
            model.task_id = self.TALK_ID
            return model

        try:
            _glasses = await self._service.get(_chosen_glasses.glasses_sub_id)
            if _glasses is None:
                model.response_message = self._res_msg['res.' + self.task_id + '-02']
                model.task_id = self.TALK_ID
                return model
            model.response_message = self._res_msg['res.' + self.task_id + '-04']
            model.response_message = model.response_message.replace(
                '#brand_name#', _glasses.brand_name).replace(
                '#product_name#', _glasses.product_name).replace(
                '#color_name#', _glasses.color_code.color_name).replace(
                '#url#', _glasses.url)
            model.task_id = self.TALK_ID
            model.data = {'glasses': _glasses}
        except Exception as ex:
            self._log.error('%s',ex)
            model.response_message = self._res_msg['res.' + self.task_id + '-02']
            model.task_id = self.TALK_ID
            return model

        return model
    
    async def get_glasses_by_ai(self, request_message:str , glasses):
        glasses_info = "\n".join(f"glasses_sub_id: {item.glasses_sub_id}, 제품명: {item.product_name}, 색상: {item.color_code.color_name}, 재질: {item.material_code.material_name}" for item in glasses)
        prompt = f"다음 안경 목록 중에서 회원 요청에 따라 그 중 한 개를 선택하고, 그 안경의 glasses_sub_id 를 JSON 형태로 응답해 주세요:\n 안경목록:{glasses_info}\n 사용자 요청: {request_message}"

        try:
            completion = self._client.chat.completions.create(
                model="gpt-4o-mini-2024-07-18",  # 또는 다른 적절한 모델 선택
                messages=[
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
            )
            response_json = completion.choices[0].message.content

            if response_json:
                return ChosenGlasses.model_validate_json(response_json)
            else:
                self._log.debug("OpenAI API 응답이 비어 있습니다.")
                return None
        except Exception as ex:
            self._log.error('Error: %s',ex)
            return None

class FittingTask(AbstractTask):
    """
    Listing glasseses.
    """
    def __init__(self) -> None:
        super(FittingTask,self).__init__('T08', 'fitting glass')
        self._service = FittingService()

    async def run(self, session: ChatSessionData, model:ChatModel):
        """
        Run a task.   "
        """
        if model.task_id != self.task_id:
            return None
        self._log.debug('start fitting task.')
        _is_camera = False
        for chat in session.chat_list:
            if chat.task_id == 'T01':
                _is_camera = True
            elif chat.task_id == 'T02':
                _is_camera = False
        
        # if _is_camera is True:
        #     model.task_id = self.task_id +'-03'
        #     model.response_message = self._res_msg['res.' + self.task_id ]
        #     return model

        model = await self._service.fitting(session=session, model=model)

        return model
