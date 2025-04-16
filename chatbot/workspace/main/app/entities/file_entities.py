'''
file_entities.py

author: sgkim
since : 2025-03-18
'''
from tortoise import fields, models

from halowing.web.codes import FileState

class StoredFileEntity(models.Model):
    '''
    저장된 파일 정보를 보관한다.
    '''
    file_id             = fields.UUIDField(primary_key=True)
    filename            = fields.CharField(max_length=256)
    file_size           = fields.BigIntField(null=True)
    file_ext            = fields.CharField(max_length=4, null=True)
    registed_datetime   = fields.DatetimeField(auto_now_add=True)
    stored_filename     = fields.CharField(max_length=256)
    path                = fields.CharField(max_length=256)
    state               = fields.IntEnumField(enum_type=FileState)

    def __str__(self):
        return f'file_id = {self.file_id}, filename = {self.filename},\
              file_size = {self.file_size}, file_ext = {self.file_ext},\
                  registed_datetime = {self.registed_datetime},\
                      stored_filename = {self.stored_filename}, path = {self.path},\
                          state = {self.state}'
    
    def __repr__(self):
        return f'StoredFileEntity[file_id={self.file_id}, filename={self.filename},\
              file_size={self.file_size}, file_ext={self.file_ext},\
                  registed_datetime={self.registed_datetime},\
                      stored_filename={self.stored_filename}, path={self.path},\
                          state={self.state}]'

    class Meta:
        '''
        metadata
        '''
        table = 'file_tb'
        table_description = '파일 저장소'
#----------------------------

# class File(models.Model):
#     ''''
#     파일 정보를 보관한다.
#     '''
#     file_id                 = fields.UUIDField(primary_key=True)
#     filename                = fields.CharField(max_length=256, comment='It is the original filename.')
#     file_size               = fields.BigIntField(null=True, comment='It is file size in byte unit')
#     file_ext                = fields.CharField(max_length=4, null=True, comment='It is the file extension of stored, png/jpg/img/...')
#     registed_datetime       = fields.DatetimeField(auto_now_add=True, comment='It is the datetime when row is created.')
#     stored_filename         = fields.CharField(max_length=256, comment='It is a name of file that is saved in file_storage')
#     path                    = fields.CharField(max_length=256, comment='It is a parent path of stored file.')
#     state                   = fields.IntEnumField(enum_type=FileState)

#     def __str__(self):
#         return f'file_id={self.file_id}, filename={self.filename}, file_size={self.file_size},\
#               file_ext={self.file_ext}, stored_filename={self.stored_filename}, path={self.path}'
#     def __repr__(self):
#         return f'Fiel[file_id={self.file_id}, filename={self.filename}, file_size={self.file_size},\
#               file_ext={self.file_ext}, stored_filename={self.stored_filename}, path={self.path}]'
    
#     class Meta:
#         '''
#         metadata
#         '''
#         table = "file_tb"
#         table_description = "파일 정보를 보관한다."
# ------------------------------------------------------