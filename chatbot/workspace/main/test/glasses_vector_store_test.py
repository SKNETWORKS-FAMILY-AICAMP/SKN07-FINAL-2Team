'''
Glasses Repository Test
'''
import logging

from config.glasses_vectordb_configuration import GlassesVectorDBConfiguration
import config.logging_configuration

_log = logging.getLogger('GlassesVectorDBConfigurationTest')
_config = GlassesVectorDBConfiguration()

def query_test():

    _user_msg = "projektprodukt 에서 만든 안경. "
    _results = _config.get_vector_store().similarity_search_with_relevance_scores (
            query= _user_msg,
            k=5
        )
    
    for _doc, _no in _results:
        _log.debug('================')
        _log.debug('doc = %s, num = %s', _doc.page_content, _no)
        _log.debug('================')

        

if "__main__" == __name__:
    _log.info('################ start test ################')
    query_test()
    _log.info('################ end test   ################')
