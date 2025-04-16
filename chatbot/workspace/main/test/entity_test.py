'''
entity_test.py

author: sgkim
since: 2023-03-31
'''
import os
from  dotenv import load_dotenv
import logging

from tortoise import run_async

import config.logging_configuration

from config.mdb_configuration import MDBConfiguration
from entities.glasses_entities import Glasses, GlassesSub
from entities.code_entities import FaceShape, GlassesTypeCode
    
_log = logging.getLogger('test')
_db = MDBConfiguration()

async def run():

    await _db.init_connection()
    # _face_shape = await FaceShape.get_or_none(face_shape_name='oblong')
    # _log.debug('_face_shape= %s', _face_shape)


    # _glasess_types = await GlassesTypeCode.filter(face_shapes__face_shape_name = 'oblong').all()
    # for item in _glasess_types:
    #     _log.debug('_glasess_type= %s', item)

    # _glasses = await Glasses.filter(glasses_type__face_shapes__face_shape_name = 'oblong').all()
    # _log.debug('_glasses= %s', _glasses)
    _condition = {
            'glasses__glasses_type__face_shapes__face_shape_name': 'oblong'
        }

    _rs = await GlassesSub.filter(
        # glasses__glasses_type__face_shapes__face_shape_name = 'oblong'
        **_condition
    ).prefetch_related(
        'glasses',
        'color_code', 
        'material_code', 
        'glasses__glasses_type',
        'glasses__glasses_type__face_shapes',
        'glasses__glasses_type__face_shapes__image',
        'images' 
    ).order_by('glasses_sub_id').offset(0).limit(100)
    
    for item in _rs:
        _log.debug('glasses= %s', item)
        break
    
   
    await _db.close_connection()        
run_async(run())
