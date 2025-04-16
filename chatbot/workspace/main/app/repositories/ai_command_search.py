'''
chat_ai.py
'''
from typing import List, Dict
import logging

from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain.agents.agent import  AgentExecutor
from langchain.agents.openai_functions_agent.base import create_openai_functions_agent
from langchain.tools import Tool
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from models.chat_models import ChatModel

class AiCommanderSearch:
    '''
    기타 알수 없는 명령.
    '''
    _log = logging.getLogger('AiCommanderSearch')


    def __init__(self,
                 chat_model:str="gpt-4o-mini-2024-07-18") -> None:
        
        self._llm:ChatOpenAI = ChatOpenAI(
            model = chat_model,
            temperature=0
        )

        self._prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessage(
                    content='당신은 사용자의 요청을 분석하여 어떤 TOOL을 실행해야 하는지 파악하는 분석가입니다. 만약 사용 가능한 TOOL이 없으면 "unknown"으로 답변하세요.'
                ),
                MessagesPlaceholder(variable_name="chat_history"),
                MessagesPlaceholder(variable_name="input"),
                MessagesPlaceholder(variable_name="agent_scratchpad")
            ],
        )

        def return_function_name(tool_name:str) -> str:
            self._log.debug('input param is %s',tool_name)
            return tool_name

        # tool 등록
        self._tools = [
            # Tool(
            #     name="T01",
            #     func= lambda command :  'T01',
            #     description="안녕하세요. FaceFit 서비스에 오신 것을 환영합니다. 얼굴형에 어울리는 안경을 추천 받기 원하시면 다음과 같은 방법 중 하나를 선택해 주세요.\n 1. 웹캠을 이용하여 사진을 촬영합니다. 2. 얼굴 사진을 전송합니다. 라는 질문중 첫 번째 응답인 1. 얼굴형을 분석하기 위하여 웹캠을 이용하여 사진을 촬영합니다. 를 선택 했을 때 동작합니다. "
            # ),
            # Tool(
            #     name="T02",
            #     func= lambda command:  'T02',
            #     description="안녕하세요. FaceFit 서비스에 오신 것을 환영합니다. 얼굴형에 어울리는 안경을 추천 받기 원하시면 다음과 같은 방법 중 하나를 선택해 주세요.\n 1. 웹캠을 이용하여 사진을 촬영합니다. 2. 얼굴 사진을 전송합니다. 라는 질문중 두 번째 응답인 2. 얼굴형을 분석하기 위하여 얼굴 사진을 전송합니다. 를 선택 했을 때 동작합니다."
            # ),
            Tool(
                name="T01",
                func= return_function_name,
                description="얼굴형을 분석하려면 다음과 같은 방법 중 하나를 선택해 주세요.\n 1. 웹캠을 이용하여 사진을 촬영합니다.\n 2. 얼굴 사진을 전송합니다. 라는 문장이 들어간 질문중, 첫 번째 응답인 1. 얼굴형을 분석하기 위하여 웹캠을 이용하여 사진을 찍는 것을 요청합니다. 를 선택 했을 때 동작합니다."
            ),
            Tool(
                name="T02",
                func= return_function_name,
                description="얼굴형을 분석하려면 다음과 같은 방법 중 하나를 선택해 주세요.\n 1. 웹캠을 이용하여 사진을 촬영합니다.\n 2. 얼굴 사진을 전송합니다. 라는 문장이 들어간 질문중, 두 번째 응답인 2. 얼굴형을 분석하기 위하여 얼굴 사진을 전송합니다. 를 선택 했을 때 동작합니다."
            ),
            Tool(
                name="T03",
                func= return_function_name,
                description="얼굴형에는 어떤 것들이 있나요"
            ),
            Tool(
                name="T05",
                func= return_function_name,
                description="요청한 얼굴 형태의 분석 결과를 알려주세요."
            ),
            Tool(
                name="T06",
                func= return_function_name,
                description="안경 목록을 보여 드릴까요. 분석된 얼굴형에 어울리는 안경들의 목록을 보여 드립니다."
            ),
            Tool(
                name="T07",
                func= return_function_name,
                description="상세 정보를 보여 드립니다. 선택한 안경, 상품 또는 제품의 상세한 정보를 보여 드립니다. "
            ),
            Tool(
                name="T08",
                func= return_function_name,
                description="선택한 안경과 등록된 얼굴 사진을 이용하여 안경을 쓰고 있는 합성 사진을 만듭니다."
            ),
            Tool(
                name="T20-01",
                func= return_function_name,
                description="사진이 준비 되었습니다. 사진을 전송하시겠습니까?<br/> 1.예, 2.아니오. 라는 질문의 응답으로 1.예 또는 긍정의 응답에 대하여 동작합니다."
            ),
            Tool(
                name="T20-02",
                func= return_function_name,
                description="사진이 준비 되었습니다. 사진을 전송하시겠습니까?<br/> 1.예, 2.아니오. 라는 질문의 응답으로 2.아니오 또는 부정의 응답에 대하여 동작합니다."
            ),
            
        ]
        self._agent = create_openai_functions_agent(
            llm=self._llm,
            tools=self._tools,
            prompt=self._prompt
            )
        self._agent_executor = AgentExecutor(
            agent=self._agent,
            tools=self._tools,
            handle_parsing_errors=True,
            return_intermediate_steps=True
        )

    def get_command(
            self,
            user_msg: str,
            chat_list :List[ChatModel]
        ) -> str:
        """
        AI를 통한 명령을 찾는다.
        """
        self._log.debug('#################################################')
        self._log.debug('user_msg : %s', user_msg)
        self._log.debug('#################################################')
        chat_history = []
        for item in chat_list:
            if item.request_message is not None:
                chat_history.append(HumanMessage(content=item.request_message))
            if item.response_message is not None:
                chat_history.append(AIMessage(content=item.response_message))

        try:
            _result = self._agent_executor.invoke(
                {
                    "input": [HumanMessage(content=user_msg)],
                    "chat_history": chat_history
                },
                config={"return_intermediate_steps": True}
            )
        except Exception as ex:
            self._log.error('Error: %s',ex)
            return 'unknown'

        return self.__parse_result(_result)

    def __parse_result(self, results:Dict) -> tuple[str, str]:
        '''
        result를 분석하여 어떤 답을 내었는지 확인한다.
        '''
        if len(results["intermediate_steps"]) ==0 :
            self._log.debug('result : %s', results)
        else:
            self._log.debug('results["intermediate_steps"] : %s', results["intermediate_steps"])
        # self._log.debug('len(results["intermediate_steps"]) : %s', len(results["intermediate_steps"]))
        _output = results['output']
        if len(results["intermediate_steps"]) != 0:
            last_step = results["intermediate_steps"][-1]  # tool 의 return 값
            self._log.debug('last_step*********************** : %s', last_step)
            
            tool_result = last_step[-1]
            _tool_name = last_step[0].tool
            self._log.debug('tool_result*********************** : %s', tool_result)
            self._log.debug('_tool_name*********************** : %s', _tool_name)

            _task_id = _tool_name
        elif _output == 'unknown':
            _task_id = 'unknown'
        else:
            _task_id = 'ai'

        return _task_id, _output
