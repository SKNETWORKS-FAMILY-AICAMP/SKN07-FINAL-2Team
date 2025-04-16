'''
Command Repository Test
'''
import logging
from config.command_vectordb_configuration import CommandVectorDBConfiguration
from repositories.command_repository import CommandRepository
import config.logging_configuration
from models.chat_models import ChatModel
from halowing.util.properties.message_properties import ResponseMessage

_log = logging.getLogger('CommandRepositoryTest')

_config = CommandVectorDBConfiguration()
_repository = CommandRepository()
_msg_property = ResponseMessage()

def add():
    commands = {
        "T05": [
            "내 얼굴은 네모 형이야. 네모형 얼굴에 어울리는 안경은 무엇이지.",
        ],
    }
    for command, synonyms in commands.items():
        _repository.add_command(command, synonyms)

def query_test():
    # _user_msg = "내 얼굴은 네모 형이야. 네모형 얼굴에 어울리는 안경은 무엇이지."
    _user_msg ='안녕하세요.'
    _lst = []
    _chat  = ChatModel.model_validate({
        # 'request_message': "처음부터 다시 시작하자.",
        'request_message': "",
        'response_message': "안녕하세요. FaceFit 서비스에 오신 것을 환영합니다. 얼굴형에 어울리는 안경을 추천 받기 원하시면 1. 웹캠을 이용하여 사진을 촬영하거나 2. 얼굴 사진 파일을 대화창에 첨부해 주세요."
    })
    _lst.append(_chat)
    _command = _repository.get_command(_user_msg,chat_list=_lst)
    _log.info('result = %s, msg= %s', _command, _msg_property['res.' + _command])


print(__name__)
if "__main__" == __name__:
    _log.info('################ start test ################')
    # add()
    query_test()
    _log.info('################ end test   ################')
