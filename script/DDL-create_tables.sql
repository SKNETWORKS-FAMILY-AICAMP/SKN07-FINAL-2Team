-- facefit.file_tb definition

ALTER TABLE glasses_tb 
DROP CONSTRAINT glasses_tb_fk_1
;

ALTER TABLE glasses_sub_tb 
DROP CONSTRAINT glasses_sub_tb_fk_1 
;

ALTER TABLE glasses_sub_tb 
DROP CONSTRAINT glasses_sub_tb_fk_2
;

ALTER TABLE glasses_sub_tb 
DROP CONSTRAINT glasses_sub_tb_fk_3 
;


ALTER TABLE glasses_file_map_tb 
DROP CONSTRAINT glasses_file_map_tb_fk_1 
;

ALTER TABLE glasses_file_map_tb 
DROP CONSTRAINT glasses_file_map_tb_fk_2 
;

ALTER TABLE face_shape_tb 
DROP CONSTRAINT face_shape_tb_tb_fk_1 
;

ALTER TABLE face_shape_glasses_map_tb 
DROP CONSTRAINT face_shape_glasses_map_tb_fk1 
;

ALTER TABLE face_shape_glasses_map_tb 
DROP CONSTRAINT face_shape_glasses_map_tb_fk2
;


DROP TABLE IF EXISTS `file_tb` CASCADE;

DROP TABLE IF EXISTS `face_shape_tb` CASCADE;

drop table IF EXISTS `glasses_type_code_tb` CASCADE;

DROP TABLE IF EXISTS `color_code_tb`CASCADE;

DROP TABLE IF EXISTS `material_code_tb` CASCADE;

DROP TABLE IF EXISTS `glasses_tb` CASCADE;

DROP TABLE IF EXISTS `glasses_sub_tb` CASCADE;

DROP TABLE IF EXISTS `glasses_file_map_tb`;

drop table IF EXISTS `face_shape_glasses_map_tb`;

-- ---


CREATE TABLE `file_tb` (
  `file_id` 			char(36) 		NOT NULL									COMMENT 'Primay key, it is generated automatically by python Tortoise.',
  `filename` 			varchar(256) 	NOT NULL									COMMENT 'It is the original filename.',
  `file_size` 			bigint(20) 					DEFAULT NULL					COMMENT 'It is file size in byte unit',
  `file_ext` 			varchar(4) 					DEFAULT NULL					COMMENT 'It is the file extension of stored, png/jpg/img/...',
  `registed_datetime` 	datetime(6) 	NOT NULL 	DEFAULT current_timestamp(6)	COMMENT 'It is the datetime when row is created.',
  `stored_filename` 	varchar(256) 	NOT NULL									COMMENT 'It is a name of file that is saved in file_storage',
  `path` 				varchar(256) 	NOT NULL									COMMENT 'It is a parent path of stored file.',
  `state` 				smallint(6) 	NOT NULL 	DEFAULT 0						COMMENT 'It is the stae of file. READY: 1\nSTORED: 0\nDELETED: -1',
  PRIMARY KEY (`file_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci COMMENT='저장된 파일 정보를 보관한다.';


-- facefit.face_shape_tb definition
CREATE TABLE `face_shape_tb` (
  `face_shape_id` 		smallint(6)		NOT NULL									COMMENT 'Primay key. Heart: 1\n, Oblong: 2\n, Oval: 3\n, Round: 4\n, Square: 5\n',
  `face_shape_name` 	varchar(16) 	NOT NULL									COMMENT 'It is the name of face shape. : Heart, Oblong, Oval, Round, Square',
  `file_id` 			char(36) 		NOT NULL									COMMENT 'It is a image of glasses. Foreign key, references file_tb.file_id.',
  `description`         text			NULL	                    				COMMENT 'It is a descripton of face shape.',
  PRIMARY KEY (`face_shape_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci COMMENT='저장된 얼굴형 정보를 보관한다.';

-- facefit.material_code_tb definition
CREATE TABLE `glasses_type_code_tb` (
  `glasses_type_code`   smallint(4)		NOT NULL                    				COMMENT 'Primary key. It is a code of glasses type.',
  `glasses_type`        varchar(64)		NOT	NULL		   							COMMENT 'It is a type of glasses. ex) 일반, 선글라스, 스포츠',
  PRIMARY KEY (`glasses_type_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci COMMENT='저장된 안경 형태 code를 보관한다.';


-- facefit.color_code_tb definition
CREATE TABLE `color_code_tb` (
  `color_code`         	smallint(4)		NOT NULL                    				COMMENT 'Primary key. It is a color code of glasses. ',
  `color_name` 			varchar(64) 	NOT NULL									COMMENT 'It is the name of color. ex) red, green, blue',
  PRIMARY KEY (`color_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci COMMENT='저장된 color code를 보관한다.';

-- facefit.material_code_tb definition
CREATE TABLE `material_code_tb` (
  `material_code`      	smallint(4)		NOT NULL                    				COMMENT 'Primary key. It is a material code of glasses.',
  `material_name` 		varchar(64) 	NOT NULL									COMMENT 'It is the name of material. ex) 뿔테, 금테, 티타늄',
  PRIMARY KEY (`material_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci COMMENT='저장된 material code를 보관한다.';


-- facefit.glasses_tb definition
CREATE TABLE `glasses_tb` (
  `glasses_id` 			smallint(6)		NOT NULL									COMMENT 'Primay key, it is generated automatically.',
  `brand_name`			varchar(128)		NULL		DEFAULT NULL				COMMENT 'It is the brand name of glasses.',
  `model_no`			varchar(64)			NULL		DEFAULT NULL				COMMENT 'It is the model no of glasses assigned by brand',
  `glasses_type_code`   smallint(4)		    NULL                    				COMMENT 'Foreign key. It is a code of glasses type.',
  PRIMARY KEY (`glasses_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci COMMENT='저장된 안경 모델 정보를 보관한다.';



-- facefit.glasses_tb definition
CREATE TABLE `glasses_sub_tb` (
  `glasses_sub_id` 		smallint(6)		NOT NULL									COMMENT 'Primary key',
  `glasses_id` 			smallint(6)		NOT NULL									COMMENT 'Foreign key, references glasses_tb.glasses_id',
  `product_name` 		varchar(256) 	    NULL		DEFAULT NULL				COMMENT 'It is the Product Name.',
  `color_code` 			smallint(4)		    NULL									COMMENT 'It is the color code of glasses. reference = color_code_tb.color_code',
  `url`					varchar(256)		NULL		DEFAULT NULL				COMMENT 'It is web url address of glasses for more information.',
  `lens_width` 			smallint(3) 		NULL		DEFAULT NULL				COMMENT 'It is the width of lens. unit: mm',
  `lens_height` 		smallint(3) 		NULL		DEFAULT NULL				COMMENT 'It is the height of lens. unit: mm',
  `frame_front_length` 	smallint(3) 	 	NULL		DEFAULT NULL				COMMENT 'It is the width of front frame. unit: mm',
  `material_code`      	smallint(4) 		NULL		DEFAULT NULL				COMMENT 'It is the type of glasses material. material_code_tb.material_code',
  `price` 				int 	            NULL        DEFAULT NULL				COMMENT 'It is the price of glasses. unit: won',
   PRIMARY KEY (`glasses_sub_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci COMMENT='저장된 안경 모델 별 세부 정보를 보관한다.';

-- facefit.glasses_file_map_tb definition
CREATE TABLE `glasses_file_map_tb` (
  `glasses_sub_id` 		smallint(6)		NOT NULL									COMMENT 'Foreign key, references glasses_sub_tb.glasses_sub_id',
  `file_id` 			char(36) 		NOT NULL									COMMENT 'Foreign key, references file_tb.file_id.'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci COMMENT='저장된 안경 모델 정보를 보관한다.';



CREATE TABLE `face_shape_glasses_map_tb` (
	`face_shape_id` 	  smallint(6)		NOT NULL									COMMENT 'Foreign key. references face_shape_tb.face_shape_id',
	`glasses_type_code`   smallint(4)		NOT NULL                    				COMMENT 'Foreign key. references glasses_type_code_tb.glasses_type_code'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci COMMENT='얼굴형 별 안경 모델 정보를 보관한다.';
;


ALTER TABLE `glasses_tb`
ADD CONSTRAINT  glasses_tb_fk_1
FOREIGN KEY (glasses_type_code) REFERENCES glasses_type_code_tb(glasses_type_code)
ON DELETE CASCADE
;


ALTER TABLE glasses_sub_tb 
ADD CONSTRAINT glasses_sub_tb_fk_1 
Foreign key (glasses_id) references glasses_tb(glasses_id)
ON DELETE CASCADE
;

ALTER TABLE glasses_sub_tb 
ADD CONSTRAINT glasses_sub_tb_fk_2
Foreign key (material_code) references material_code_tb(material_code)
ON DELETE CASCADE
;

ALTER TABLE glasses_sub_tb 
ADD CONSTRAINT glasses_sub_tb_fk_3 
Foreign key (color_code) references color_code_tb(color_code)
ON DELETE CASCADE
;


ALTER TABLE glasses_file_map_tb 
ADD CONSTRAINT glasses_file_map_tb_fk_1 
Foreign key (glasses_sub_id) references glasses_sub_tb(glasses_sub_id)
ON DELETE CASCADE
;

ALTER TABLE glasses_file_map_tb 
ADD CONSTRAINT glasses_file_map_tb_fk_2 
Foreign key (file_id) references file_tb(file_id)
ON DELETE CASCADE
;

ALTER TABLE face_shape_tb 
ADD CONSTRAINT face_shape_tb_tb_fk_1 
Foreign key (file_id) references file_tb(file_id)
ON DELETE CASCADE
;

ALTER TABLE face_shape_glasses_map_tb 
ADD CONSTRAINT face_shape_glasses_map_tb_fk1 
Foreign key (face_shape_id) references face_shape_tb(face_shape_id)
ON DELETE CASCADE
;

ALTER TABLE face_shape_glasses_map_tb 
ADD CONSTRAINT face_shape_glasses_map_tb_fk2 
Foreign key (glasses_type_code) references glasses_type_code_tb(glasses_type_code)
ON DELETE CASCADE
;
