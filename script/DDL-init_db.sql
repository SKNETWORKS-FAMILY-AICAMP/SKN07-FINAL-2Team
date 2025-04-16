use mysql;

show databases;

create user firefly@'%' identified by 'firefly@2025';

select * from user;

grant all privileges on facefit.* to firefly@'%';


flush privileges;

