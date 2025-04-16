# FastAPI Project Template

# 환경설정
## Windows 환경 설정
### 가상환경 설치
- 위치: {repository_root}/
```
python3 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt 
```

### env 파일 설정
- 위치:  {workspace_root}/.env
```
# windows
PYTHONPATH=./main/app/;./main/resources;./lib;%PYTHONPATH%
db_url=mysql://{id}:{passwd}@{db_server}:3306/{db_schema}
```

## Linux 환경 설정
### 가상환경 설치

- 위치 : {repository_root}/
```
python3 -m venv .venv
source .venv\bin\activate
pip install -r requirements.txt 
```

### env 파일 설정
- 위치:  {workspace_root}/.env
```
# linux
PYTHONPATH=$PYTHONPATH:./main/app/:./main/resources:./lib
db_url=mysql://{id}:{passwd}@{db_server}:3306/{db_schema}
```

### DLIB 설치를 위한 CMAKE 설치
sudo yum install python3.12-devel gcc gcc-c++ cmake 
- dlib 를 user 권한으로 설치하면 컴파일 된 라이브러리 설치시 권한이 없어서 에러 난다.
sudo pip3 install dlib 

### SQLite3.35 이상 버전 설치
- 소스 다운로드
sudo yum install wget
wget https://sqlite.org/2025/sqlite-autoconf-3490100.tar.gz
tar xzf sqlite-autoconf-3490100.tar.gz
- 소스 컴파일
cd sqlite-autoconf-3490100
./configure --enable-fts5
sudo make
sudo make install
- LD_LIBRARY_PATH  설정: ./.bashrc_profile
export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH


### opencv lib 설치
sudo yum install mesa-libGL-devel


### OPENAI_API_KEY 설치: ./.bashrc_profile
export OPENAI_API_KEY='your key'
