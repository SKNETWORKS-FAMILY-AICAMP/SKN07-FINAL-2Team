'''
분석되지 않은 명령에 대한 처리
'''
from langchain_core.messages import HumanMessage, AIMessage
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder
)
from langchain_openai import ChatOpenAI

from config.command_vectordb_configuration import CommandVectorDBConfiguration
from models.chat_models import ChatModel
from services.tasks.base_tasks import AbstractTask
from session.session_models import ChatSessionData

class UnknownTask(AbstractTask):
    '''
    파악되지 않은 문구에 대한 대화
    '''

    CONTEXTUALIZE_Q_SYSTEM_PROMPT = """
    주어진 chat_history 를 바탕으로 사용자의 최신 질문을 이해하고, chat_history 없이 질문을 이해할 수 있도록 새로운 질문을 작성하라. 절대 질문에 답변을 하지 말고 질문을 재 작성하라. 만약 필요하다면 질문을 그대로 반환하라. 
    """

    QA_SYSTEM_TEMPLATE = """
    당신은 AI 맞춤 안경 서비스인 FaceFit 서비스의 AI 어시스턴트입니다. 사용자의 질문에 대해 답변 규칙에 따라 컨텍스트를 바탕으로 명확하고 자세한 답변을 제공하세요. 

    ### [답변 규칙]
    - 질문에 대해 단답형 답변은 지양하고 완전한 문장으로 답변합니다.
    - 답변은 300자 이상을 넘지 않습니다.
    - 사용자가 명확한 답변을 얻을 수 있도록 논리적으로 답변합니다.
    - 대화는 안경에 관한 내용과 일반적인 인사말만 허용합니다. 
    - 컨텍스트가 비어 있고, 질문자의 질문 내용이 인사말인 경우 간단히 대답합니다.
    - 컨텍스트가 비어 있고, 질문자의 질문 내용이 안경과 관련된 내용이면 답변을 하고 끝에 '저는 이렇게 알고 있습니다.'라는 문장을 붙입니다.
    - 컨텍스트가 비어 있고, 질문자의 질문 내용이 안경에 관한 내용이 아니고, 날씨에 대한 이야기나 인사말도 아닌 경우 '저는 안경 Fitting을 도와 주는 AI라서  많은 것에 대답할 수 없습니다. 얼굴 사진을 찍어서 어울리는 안경을 추천 받아 보시는 건 어떨까요?.' 라고 대화를 회피합니다.
    - 컨텍스트가 비어 있고, 이전 대화 내역이 안경에 관한 내용이 아니라면 '얼굴 사진을 찍어서 얼굴에 어울리는 안경을 추천 받아 보시는 것이 어떻습니까'라고 답변한다.

    ### [컨텍스트]
    {context}
    """

    def __init__(self,
                 chat_model:str="gpt-4o-mini-2024-07-18"
                 ) -> None:
        super(UnknownTask,self).__init__('unknown', 'random chat')

        _llm:ChatOpenAI = ChatOpenAI(
            model = chat_model,
            temperature=0.7
        )
        _contextualize_q_prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(self.CONTEXTUALIZE_Q_SYSTEM_PROMPT),
            MessagesPlaceholder('chat_history'),
            HumanMessagePromptTemplate.from_template(template="{input}")
        ])
        
        _context_retriever = CommandVectorDBConfiguration().get_vector_store().as_retriever()
        _history_aware_retriever = create_history_aware_retriever(
            llm= _llm,
            retriever= _context_retriever,
            prompt= _contextualize_q_prompt
        )

        _question_answer_prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(self.QA_SYSTEM_TEMPLATE),
            MessagesPlaceholder('chat_history'),
            HumanMessagePromptTemplate.from_template(template="{input}")
        ])

        _question_answer_chain = create_stuff_documents_chain(
            llm= _llm,
            prompt=_question_answer_prompt,
        )
        self._chain = create_retrieval_chain(_history_aware_retriever, _question_answer_chain)

    async def run(self, session: ChatSessionData, model:ChatModel):
        '''
        run unknown task.
        '''
        if model.task_id != self.task_id:
            return None
        
        _user_msg = model.request_message
        chat_history = []
        for _chat in session.chat_list[-5:]:
            h_msg = _chat.request_message  if _chat.request_message is not None else ''
            ai_msg = _chat.response_message  if _chat.response_message is not None else ''
            chat_history.extend([
                HumanMessage(content= h_msg),
                AIMessage(content= ai_msg)
            ])

        _result = self._chain.invoke( {"input": _user_msg, 
                                    #   "context": None,
                                      "chat_history": chat_history,
                                      })
        _response_message = _result['answer']

        self._log.debug('_response_message = %s',_response_message)

        model.response_message = _response_message
        model.task_id = self.TALK_ID
        self._log.debug('response = %s',model)

        return model
