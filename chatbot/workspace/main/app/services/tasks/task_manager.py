'''
task_manager.py

author: sgkim
siince: 2023-03-31
'''
import sys
import threading
import logging

from typing import Dict

from models.chat_models import ChatModel
from services.tasks import base_tasks
from services.tasks.unkown_task import UnknownTask
from session.session_models import ChatSessionData

class ChatTaskManager:
    """
    ChatTaskManager is responsible for managing and executing tasks.
    """
    _instance = None
    _lock = threading.Lock()
    _log = logging.getLogger('ChatTaskManager')

    _tasks: Dict[str, base_tasks.AbstractTask] = {}

    def __new__(cls) -> None:
        """
        Create a singleton instance of ChatTaskManager.
        """
        if cls._instance is not None:
            return cls._instance
        
        with cls._lock:
            if cls._instance is not None:
                return cls._instance
            cls._instance = super(ChatTaskManager, cls).__new__(cls)
            return cls._instance

    def register_task(self, task: base_tasks.AbstractTask) -> None:
        """
        Register a task with the specified ID.
        """
        self._tasks[task.get_id()] = task

    def get_task(self, task_id: str) -> base_tasks.AbstractTask:
        """
        Get a task by its ID.
        """
        self._log.debug('[get_task] task_id = %s', task_id)
        try:
            return self._tasks.get(task_id,'unknown')
        except KeyError:
            return self.get_task('unknown')

    async def run_task(
            self,
            task_id: str,
            session: ChatSessionData,
            model:ChatModel
    ) -> ChatModel:
        """
        Run a task with the specified ID and arguments.
        """
        self._log.debug('[run_task] task_id = %s', task_id)
        if task_id is None:
            task_id = 'unknown'

        task =self.get_task(task_id)
        self._log.debug('task = %s', task)
        return await task.run(session=session, model=model)

class ChatTaskManagerContext:
    '''
    ChatTaskManagerContext
    '''

    @classmethod
    def init(cls):
        '''
        TaskManager 초기화
        '''
        cls._tmanager = ChatTaskManager()
        cls._tmanager.register_task(base_tasks.CommandAnalysisTask('T00','welcome'))
        # cls._tmanager.register_task(base_tasks.CommandAnalysisTask('T01','camera'))
        cls._tmanager.register_task(base_tasks.SelectCameraTask())
        cls._tmanager.register_task(base_tasks.CommandAnalysisTask('T02','file'))
        cls._tmanager.register_task(base_tasks.CommandAnalysisTask('T05','introduce'))
        cls._tmanager.register_task(base_tasks.CommandAnalysisTask('T09','camera on'))
        cls._tmanager.register_task(base_tasks.CommandAnalysisTask('T10','camera off'))
        cls._tmanager.register_task(base_tasks.CommandAnalysisTask('T20-01','upload file'))
        cls._tmanager.register_task(base_tasks.CommandAnalysisTask2('T20-02','deny upload file', 'T09'))
        cls._tmanager.register_task(base_tasks.CommandAnalysisTask('T90','init'))
        cls._tmanager.register_task(base_tasks.FaceListTask())
        cls._tmanager.register_task(base_tasks.GlassesListTask())
        cls._tmanager.register_task(base_tasks.GlassesDetailTask())
        cls._tmanager.register_task(base_tasks.FittingTask())
        cls._tmanager.register_task(UnknownTask())
