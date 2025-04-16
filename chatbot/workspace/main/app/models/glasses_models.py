'''
glasses_models.py

author: sgkim
since : 2025-03-31
'''
from typing import Optional, List
from pydantic import BaseModel, ConfigDict , model_validator, Field
from models.fileuploader_model import StoredFileModel
from services.service_helper import FileServiceHelper as fsh

class MaterialCodeModel(BaseModel):
    ''' 
    MaterialCodeModel 
    '''
    material_code: int
    material_name: str

    model_config = ConfigDict(from_attributes=True)

    def __str__(self):
        return f'material_code={self.material_code}, material_name={self.material_name}'
    
    def __repr__(self):
        return f'MaterialCodeModel(material_code={self.material_code}, material_name={self.material_name})' 

class FaceShapeModel(BaseModel):
    ''' 
    FaceShapeModel 
    '''
    face_shape_id: int
    face_shape_name: str
    image_url: Optional[str] = None
    image: Optional[StoredFileModel] = Field(exclude=True)
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode='before')
    def sync_glassess_fields(self):
        ''' image 정보를 밖으로 뽑아낸다. '''
        if self.image is None:
            return self
        fsh.set_url(self.image)
        self.image_url=self.image.url
        return self

    def __str__(self):
        return f'face_shape_id={self.face_shape_id}, face_shape_name={self.face_shape_name},\
              image={self.image}, description={self.description}'
    
    def __repr__(self):
        return f'FaceShapeModel(face_shape_id={self.face_shape_id}, \
            face_shape_name={self.face_shape_name},\
            image={self.image}, description={self.description}'

class ColorCodeModel(BaseModel):
    '''
    ColorCodeModel
    '''
    color_code: int
    color_name: str

    model_config = ConfigDict(from_attributes=True)

    def __str__(self):
        return f'color_code={self.color_code}, color_name={self.color_name}'

    def __repr__(self):
        return f'ColorCodeModel(color_code={self.color_code}, color_name={self.color_name})'

class GlassesTypeCodeModel(BaseModel):
    '''
    안경 타입 정보
    '''
    glasses_type_code: int
    glasses_type: str
    face_shapes: List[FaceShapeModel] = []

    model_config = ConfigDict(from_attributes=True)

    def __str__(self):
        return f'glasses_type_code={self.glasses_type_code}, glasses_type={self.glasses_type}'
    
    def __repr__(self):
        return f'GlassesTypeCode[glasses_type_code={self.glasses_type_code},\
              glasses_type={self.glasses_type}]'


class GlassesModel(BaseModel):
    ''' 
    GlassesModel 
    '''
    glasses_id: int
    brand_name: Optional[str] = None
    model_no: Optional[str] = None
    glasses_type:Optional[GlassesTypeCodeModel] = None

    model_config = ConfigDict(from_attributes=True)

    def __str__(self):
        return f'glasses_id={self.glasses_id}, brand_name={self.brand_name},\
                model_no={self.model_no}, glasses_type=[{self.glasses_type}]\
                    '
    
    def __repr__(self):
        return f'GlassesModel[glasses_id={self.glasses_id}, brand_name={self.brand_name},\
                model_no={self.model_no}, glasses_type=[{self.glasses_type}]\
        ]'

class GlassesSubModel(GlassesModel):
    ''' 
    GlassesSubModel 
    '''
    glasses_sub_id: int
    glasses: GlassesModel = Field(exclude=True)
    product_name: str
    color_code: ColorCodeModel
    url: Optional[str] = None
    lens_width: Optional[int] = None
    lens_height: Optional[int] = None
    frame_front_length: Optional[int] = None
    material_code: Optional[MaterialCodeModel] = None
    price: Optional[int] = None
    image_urls: List[str] = []
    images: List[StoredFileModel] = Field(exclude=True)

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode='after')
    def sync_glassess_fields(self):
        ''' glasess 정보를 밖으로 뽑아낸다. '''
        self.brand_name=self.glasses.brand_name
        self.model_no=self.glasses.model_no
        self.glasses_type = self.glasses.glasses_type
        for img in self.images:
            if img.url is None:
                fsh.set_url(img)
                self.image_urls.append(img.url)
        return self
    
    def __str__(self):
        return f'glasses_sub_id={self.glasses_sub_id}, super=[{super().__str__()}], product_name={self.product_name},\
            color_code={self.color_code}, url={self.url}, lens_width={self.lens_width},\
                  lens_height={self.lens_height}, frame_front_length={self.frame_front_length},\
                      material_code={self.material_code}, price={self.price}, images={self.images}'
    
    def __repr__(self):
        return f'GlassesSubModel(glasses_sub_id={self.glasses_sub_id}, super=[{super()}], \
             product_name={self.product_name}, color_code={self.color_code}, url={self.url},\
                  lens_width={self.lens_width},lens_height={self.lens_height},\
                      frame_front_length={self.frame_front_length},\
                      material_code={self.material_code}, price={self.price}), images={self.images}'
