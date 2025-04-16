'''
logging_configuration.py

author: sgkim
since : 2025-03-27
'''
import os
import logging
import dotenv
from halowing.util.properties.application_properties import ApplicationProperties

def init_logger():
    ''' logger 를 초기화 한다. '''
    dotenv.find_dotenv()

    _properties = ApplicationProperties()
    _file_path = _properties['logging.file_path']
    _log_level = _properties['logging.log_level']
    if _log_level is not None and _log_level.upper() == 'DEBUG':
        _log_level = logging.DEBUG
    else:
        _log_level = logging.INFO

    os.makedirs(name=os.path.dirname(_file_path),exist_ok=True)
    _handlers = [logging.FileHandler(_file_path, mode='a')]
    _profile = os.environ.get('profile')
    if _profile == 'dev':
        _handlers.append(logging.StreamHandler())
    logging.basicConfig(
        level=_log_level,
        format = '%(asctime)s - %(levelname)s - %(name)s - %(message)s', # format 지정
        handlers= _handlers
    )
    

init_logger()

