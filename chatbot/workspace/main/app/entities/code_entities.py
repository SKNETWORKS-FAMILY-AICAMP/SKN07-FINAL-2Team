'''
code_entities.py

author: sgkim
since : 2025-03-31
'''
from tortoise import fields, models

class FaceShape(models.Model):
    '''
    얼굴형 정보를 보관한다.
    '''
    face_shape_id           = fields.SmallIntField(
                                primary_key=True, 
                                comment='Primay key. Heart: 1\n, Oblong: 2\n, Oval: 3\n, Round: 4\n, Square: 5\n')
    face_shape_name         = fields.CharField(
                                max_length=16, 
                                comment='It is the name of face shape. : Heart, Oblong, Oval, Round, Square')
    image                   = fields.ForeignKeyField(
                                'models.StoredFileEntity',
                                related_name="face_shape",
                                source_field="file_id",
                                comment='It is a image of glasses. Foreign key, references file_tb.file_id.')
    description             = fields.TextField(
                                null=True, 
                                comment='It is a descripton of face shape.')

    def __str__(self):
        return f'face_shape_id={self.face_shape_id}, face_shape_name={self.face_shape_name},\
            image={self.image}, description={self.description}'
    
    def __repr__(self):
        return f'FaceShape[face_shape_id={self.face_shape_id}, face_shape_name={self.face_shape_name},\
            image={self.image}, description={self.description}]'

    class Meta:
        '''
        metadata
        '''
        table = "face_shape_tb"
        table_description = "얼굴형 정보를 보관한다."
# ------------------------------------------------------

class GlassesTypeCode(models.Model):
    '''
    안경 타입 정보를 보관한다.
    '''
    glasses_type_code       = fields.SmallIntField(
                                primary_key=True, 
                                comment='Primary key. It is a code of glasses type.'
                            )
    glasses_type            = fields.CharField(
                                max_length=64,
                                comment='It is a type of glasses. ex) 일반, 선글라스, 스포츠'
                            )
    face_shapes             = fields.ManyToManyField(
                                'models.FaceShape',
                                related_name='glasses_type',
                                backward_key='glasses_type_code',
                                forward_key='face_shape_id',
                                through='face_shape_glasses_map_tb',
                                through_fields=['face_shape_id', 'glasses_type_code'],
                                comment='It is a map table.')

    def __str__(self):
        return f'glasses_type_code={self.glasses_type_code}, glasses_type={self.glasses_type},\
            face_shapes={self.face_shapes}'

    def __repr__(self):
        return f'GlassesTypeCode[glasses_type_code={self.glasses_type_code},\
              glasses_type={self.glasses_type}, face_shapes={self.face_shapes}]'

    class Meta:
        '''
        metadata
        '''
        table = "glasses_type_code_tb"
        table_description = "안경 타입 정보를 보관한다."
# ------------------------------------------------------

class ColorCode(models.Model):
    '''
    안경 색상 정보를 보관한다.
    '''
    color_code              = fields.SmallIntField(primary_key=True, comment='Primary key. It is a color code of glasses. ')
    color_name              = fields.CharField(max_length=64, comment='It is the name of color. ex) red, green, blue')

    def __str__(self):
        return f'color_code={self.color_code}, color_name={self.color_name}'
    
    def __repr__(self):
        return f'ColorCode[color_code={self.color_code}, color_name={self.color_name}]'

    class Meta:
        '''
        metadata
        '''
        table = "color_code_tb"
        table_description = "안경 색상 정보를 보관한다."
# ------------------------------------------------------

class MaterialCode(models.Model):
    '''
    안경 재질 정보를 보관한다.
    '''
    material_code           = fields.SmallIntField(primary_key=True, comment='Primary key. It is a material code of glasses.')
    material_name           = fields.CharField(max_length=64, comment='It is the name of material. ex) 뿔테, 금테, 티타늄')

    def __str__(self):
        return f'material_code={self.material_code}, material_name={self.material_name}'
    
    def __repr__(self):
        return f'MaterialCode[material_code={self.material_code}, material_name={self.material_name}]'
    
    class Meta:
        '''
        metadata
        '''
        table = "material_code_tb"
        table_description = "안경 재질 정보를 보관한다."
# ------------------------------------------------------
