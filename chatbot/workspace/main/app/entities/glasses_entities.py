'''
This module contains the Glasses class, which represents a pair of glasses.
It includes attributes such as id, name, description, price, and image URL.

author: sgkim
since : 2025-03-31
'''

from tortoise import fields, models

class Glasses(models.Model):
    '''
    안경 정보를 보관한다.
    '''
    glasses_id              = fields.SmallIntField(primary_key=True, comment='Primay key, it is generated automatically.')
    brand_name              = fields.CharField(max_length=128, null=True, default=None, comment='It is the brand name of glasses.')
    model_no                = fields.CharField(max_length=64, null=True, default=None, comment='It is the model no of glasses assigned by brand')
    glasses_type            = fields.ForeignKeyField(
                                "models.GlassesTypeCode",
                                related_name="glasses",
                                null=True,
                                source_field="glasses_type_code",
                                comment='Foreign key. It is a code of glasses type.')

    def __str__(self):
        return f'glasses_id={self.glasses_id}, brand_name={self.brand_name}, model_no={self.model_no}, glasses_type=[{self.glasses_type}]]'
    
    def __repr__(self):
        return f'Glasses[glasses_id={self.glasses_id}, brand_name={self.brand_name}, model_no={self.model_no}, glasses_type=[{self.glasses_type}]]'
    
    class Meta:
        '''
        metadata
        '''
        table = "glasses_tb"
        table_description = "저장된 안경 모델 정보를 보관한다."
# ------------------------------------------------------

class GlassesSub(models.Model):
    '''
    안경 세부 정보를 보관한다.
    '''
    glasses_sub_id          = fields.SmallIntField(primary_key=True, comment='Primary key')
    glasses                 = fields.ForeignKeyField(
                                "models.Glasses",
                                related_name="glasses_sub",
                                source_field="glasses_id",
                                comment='Foreign key, references glasses_tb.glasses_id')
    product_name            = fields.CharField(
                                max_length=256,
                                null=True,
                                default=None,
                                comment='It is the Product Name.')
    color_code              = fields.ForeignKeyField(
                                "models.ColorCode",
                                related_name="glasses_sub",
                                null=True,
                                source_field="color_code",
                                comment='It is the color code of glasses. reference = color_code_tb.color_code')
    url                     = fields.CharField(max_length=256, null=True, default=None, comment='It is web url address of glasses for more information.')
    lens_width              = fields.SmallIntField(null=True, default=None, comment='It is the width of lens. unit: mm')
    lens_height             = fields.SmallIntField(null=True, default=None, comment='It is the height of lens. unit: mm')
    frame_front_length      = fields.SmallIntField(null=True, default=None, comment='It is the width of front frame. unit: mm')
    material_code           = fields.ForeignKeyField(
                                "models.MaterialCode", related_name="glasses_sub", 
                                null=True,
                                source_field="material_code",
                                comment='It is the type of glasses material. material_code_tb.material_code')
    price                   = fields.IntField(null=True, default=None, comment='It is the price of glasses. unit: won')
    images                  = fields.ManyToManyField(
                                'models.StoredFileEntity',
                                related_name='glasses_sub',
                                backward_key='glasses_sub_id',
                                forward_key='file_id',
                                through='glasses_file_map_tb',
                                through_fields=['glasses_sub', 'file'],
                                # source_field='file_id',
                                comment='It is a map table.')
    
    def __str__(self):
        return f'glasses_sub_id={self.glasses_sub_id},\
            glasses=[{self.glasses}],\
            product_name={self.product_name},\
            color_code={self.color_code},\
            url={self.url}, lens_width={self.lens_width}, lens_height={self.lens_height},\
            frame_front_length={self.frame_front_length},\
            material_code=[{self.material_code}],\
            price={self.price},\
            images=[{self.images}]'
    
    def __repr__(self):
        return f'GlassesSub[glasses_sub_id={self.glasses_sub_id},\
            glasses=[{self.glasses}],\
            product_name={self.product_name},\
            color_code={self.color_code},\
            url={self.url}, lens_width={self.lens_width}, lens_height={self.lens_height},\
            frame_front_length={self.frame_front_length},\
            material_code=[{self.material_code}],\
            price={self.price},\
            images=[{self.images}]'

    class Meta:
        ''''
        metadata
        '''
        table = "glasses_sub_tb"
        table_description = "저장된 안경 모델 별 세부 정보를 보관한다."
# ------------------------------------------------------

class GlassesFileMapTb(models.Model):
    '''
    안경 모델과 파일을 매핑한다.
    '''
    glasses_sub             = fields.ForeignKeyField(
                                "models.GlassesSub",
                                related_name="glasses_file_map",
                                source_field="glasses_sub_id",
                                comment='Foreign key, references glasses_sub_tb.glasses_sub_id')
    file                    = fields.ForeignKeyField(
                                "models.StoredFileEntity",
                                related_name="glasses_file_map",
                                source_field="file_id",
                                comment='Foreign key, references file_tb.file_id.')
    
    def __str__(self):
        return f'glasses_sub=[{self.glasses_sub}], file=[{self.file}]'
    
    def __repr__(self):
        return f'GlassesFileMapTb[glasses_sub=[{self.glasses_sub}], file=[{self.file}]]'

    class Meta:
        '''
        metadata
        '''
        table = "glasses_file_map_tb"
        table_description = "저장된 안경 모델 정보를 보관한다."
# ------------------------------------------------------

class FaceShapeGlassesMap(models.Model):
    '''
    얼굴형과 안경 타입을 매핑한다.
    '''
    face_shape              = fields.ForeignKeyField(
                                "models.FaceShape", 
                                related_name="face_shape_glasses_map",
                                source_field="face_shape_id",
                                comment='Foreign key. references face_shape_tb.face_shape_id')
    glasses_type            = fields.ForeignKeyField(
                                "models.GlassesTypeCode", 
                                related_name="face_shape_glasses_map",
                                source_field="glasses_type_code",
                                comment='Foreign key. references glasses_type_code_tb.glasses_type_code')
    
    def __str__(self):
        return f'face_shape={self.face_shape}, glasses_type={self.glasses_type}'
    
    def __repr__(self):
        return f'FaceShapeGlassesMap[face_shape={self.face_shape}, glasses_type={self.glasses_type}]'
    
    class Meta:
        '''
        metadata
        '''
        table = "face_shape_glasses_map_tb"
        table_description = "저장된 안경 모델 정보를 보관한다."
