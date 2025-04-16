'''
vectordb_configuration.py

author: sgkim
since : 2025-04-01
'''

import threading
from logging import getLogger

from langchain_openai import OpenAIEmbeddings  #← OpenAIEmbeddings를 가져오기
from langchain_chroma import Chroma

from halowing.util.properties.application_properties import ApplicationProperties

class CommandVectorDBConfiguration:
    '''
    VectorDB Configuration

    # pip install fastapi uvicorn opencv-python sentence-transformers chromadb
    '''
    _instance = None
    _lock = threading.Lock()
    _log = getLogger('CommandVectorDBConfiguration')
    
    def __new__(cls):
        if cls._instance is not None:
            return cls._instance
        
        with cls._lock:
            if cls._instance is not None:
                return cls._instance
            cls._instance = super(CommandVectorDBConfiguration, cls).__new__(cls)

            cls._property:ApplicationProperties = ApplicationProperties()
            cls._collection_name = cls._property['app.chromadb.collection.name.command']

            cls._embeddings = OpenAIEmbeddings( #← OpenAIEmbeddings를 초기화
                model=cls._property['app.chromadb.embedding.model_name']
            )
            cls._vector_store = Chroma(
                collection_name=cls._collection_name,
                persist_directory=cls._property['app.chromadb.path'],
                embedding_function=cls._embeddings,
            )
            
            return cls._instance

    def get_collection_name(self) -> str:
        '''
        collection_name 반환
        '''
        return self._collection_name
    
    def get_vector_store(self):
        '''
        vectorstore
        '''
        return self._vector_store
