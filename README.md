# SKN07-FINAL-2Team
# FINAL 프로젝트

## 1. 팀 소개
-
  <table>
  <tr>

    <th>김서진</th>
    <th>김성근</th>
    <th>김태희</th>
    <th>유수현</th>
    <th>정승연</th>
   
  </tr>

  <tr>
    <td><img src="https://github.com/user-attachments/assets/c53b820e-548d-48ec-bcaf-c35a0194ebf5" width="175" height="175"></td>
    <td><img src= "https://github.com/user-attachments/assets/0d1d8199-6d3b-4a1f-bdcc-2cd503ae7792" width="175" height="175"></td>
    <td><img src="https://github.com/user-attachments/assets/da1ae31d-546f-4717-9960-71434d07b5de" width="175" height="175"></td>
    <td><img src="https://github.com/user-attachments/assets/b935e946-dc89-40e6-998e-07d784d949c7" width="175" height="175"></td>
     <td><img src="https://github.com/user-attachments/assets/b935e946-dc89-40e6-998e-07d784d949c7" width="175" height="175"></td>
  </tr>
  <tr></tr>

    <th>PM</th>
    <th>Backend</th>
    <th>Data Modeling</th>
    <th>Frontend</th>
    <th>Data Modeling</th>
    
  </tr>
  </table>

---
## 2. 기술스택
## 🛠️ 기술 스택

<div align="center">

### Backend
<img src="https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white"/>
<img src="https://img.shields.io/badge/FastAPI-0.110.0-green?logo=fastapi&logoColor=white"/>
<img src="https://img.shields.io/badge/Uvicorn-ASGI-lightgrey?logo=python&logoColor=white"/>
<img src="https://img.shields.io/badge/Tortoise--ORM-ORM-blueviolet"/>

### Frontend
<img src="https://img.shields.io/badge/HTML5-E34F26?logo=html5&logoColor=white"/>
<img src="https://img.shields.io/badge/CSS3-1572B6?logo=css3&logoColor=white"/>
<img src="https://img.shields.io/badge/JavaScript-F7DF1E?logo=javascript&logoColor=black"/>
<img src="https://img.shields.io/badge/jQuery-0769AD?logo=jquery&logoColor=white"/>
<img src="https://img.shields.io/badge/Nginx-009639?logo=nginx&logoColor=white"/>

### Data Modeling
<img src="https://img.shields.io/badge/TensorFlow-FF6F00?logo=tensorflow&logoColor=white"/>
<img src="https://img.shields.io/badge/OpenCV-5C3EE8?logo=opencv&logoColor=white"/>
<img src="https://img.shields.io/badge/DeepLearning-mtcnn"/>

### Database
<img src="https://img.shields.io/badge/Chroma-VectorDB-purple"/>
<img src="https://img.shields.io/badge/MariaDB-003545?logo=mariadb&logoColor=white"/>

### AI Core
<img src="https://img.shields.io/badge/OpenAI-GPT3.5-10a37f?logo=openai&logoColor=white"/>
<img src="https://img.shields.io/badge/LangChain-Framework-379683"/>

### 협업 및 배포
<img src="https://img.shields.io/badge/AWS-232F3E?logo=amazonaws&logoColor=white"/>
<img src="https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white"/>
<img src="https://img.shields.io/badge/GitHub-181717?logo=github&logoColor=white"/>
<img src="https://img.shields.io/badge/Discord-5865F2?logo=discord&logoColor=white"/>

</div>

---
## 3. 프로젝트 개요

### 3.1 프로젝트 명

> **🔎facefit👓**  
- 얼굴형 분석 및 안경 추천, 가상 피팅 서비스

### 3.2 프로젝트 소개
**facefit**은 사용자의 얼굴을 웹캠으로 촬영 후 5가지(Round, Oval, Oblong, Heart, Square)의 얼굴형으로 분석하여 어울리는 안경테을 추천하고 안경을 가상으로 착용해볼 수 있는 서비스를 제공
MTCNN을 통한 얼굴 감지, VGG16 기반 얼굴형 분류, 챗봇과의 자연스러운 대화를 통해 맞춤형 안경 추천까지 경험 가능
![image](https://github.com/user-attachments/assets/183a9795-8487-4646-bbb3-24623a1225ee)

### 3.3 프로젝트 필요성 및 배경
- 원하는 안경을 찾기 위해 여러 차례 매장을 방문해야 하는 비효율성이 존재
- 온라인 쇼핑이 증가함에 따라 안경 구매 시 직접 착용해보지 못하는 불편함
- 얼굴형에 따라 어울리는 안경 스타일이 달라지기 때문에 객관적인 얼굴형 분석을 기반으로 개인 맞춤형 안경 추천
- 최근 AI 기술을 활용한 가상 피팅 서비스에 대한 수요가 높아지고 있으며, 이를 통해 사용자 만족도를 높임

### 3.4 프로젝트 목표
- **얼굴형 분석 모델**을 통한 정확한 얼굴형 분류 (정확도 목표 85% 이상)
- **개인 맞춤형 안경 추천 시스템** 구현 
- **웹 기반 가상 피팅 서비스** 구현 (실시간 웹캠 지원)
- **AI 챗봇 연동**으로 사용자 친화적인 안경 추천 경험 제공
- AWS를 통한 **안정적인 배포 및 운영** 실현

---
## 4. 수행 과정

### ✔️데이터 수집 및 전처리
  - 10가지 종류의 안경테 이미지 수집 및 수작업으로 마스크 처리
  - 다양한 얼굴형(둥근형, 타원형, 긴형, 하트형, 각진형) 이미지 데이터 확보
  - MTCNN을 활용한 얼굴 검출 및 정제된 데이터셋 구축

### ✔️모델 개발 및 성능 향상
  - CNN 모델을 통한 1차 얼굴형 분류 (Baseline)
  - VGG16 전이학습을 통해 최종 모델 정확도 89% 달성

### ✔️웹 서비스 구현
  - FastAPI 기반 백엔드 서버 구축
  - MariaDB와 ChromaDB를 통한 데이터 관리
  - 웹캠 연동 기능 개발 (실시간 얼굴 캡처 및 분석)
  - Nginx를 통한 웹서버 설정 및 HTTPS 적용

### ✔️AI 챗봇 연동
  - OpenAI GPT-3.5 Turbo와 LangChain을 이용해 챗봇 구축
  - 얼굴형별 맞춤형 안경 스타일 추천 대화 시나리오 설계

### ✔️배포 및 테스트
  - AWS EC2, RDS를 이용한 서버 구축 및 배포
  - Docker를 활용한 서버 환경 관리 및 배포 자동화
  - 전체 시스템 통합 테스트 및 최적화

### ✔️시스템 아키텍처
![image](https://github.com/user-attachments/assets/55dc292f-15e7-4dcd-ba15-82b31d1cc000)

---
## 5. 수행 결과
![image](https://github.com/user-attachments/assets/f107388b-a185-4e52-85e4-190b1ea7da88)
<p align="center">
  <img src="https://github.com/user-attachments/assets/96c8ee9e-d81d-4714-ab20-fde0a62382cb" width="400"/>
  <img src="https://github.com/user-attachments/assets/b35ce6c0-f63f-48fc-8add-abe6b6130cd6" width="400"/>
</p>

<p align="center">
  <img src="https://github.com/user-attachments/assets/2a4b0647-f839-4f38-aadd-56c11bced024" width="400"/>
  <img src="https://github.com/user-attachments/assets/f21b1fcf-ddea-4ccb-9450-1b63abf4c84d" width="400"/>
</p>

<p align="center">
  <img src="https://github.com/user-attachments/assets/ed8ccc5c-a82d-498c-8986-e77c3c268d42" width="400"/>
  <img src="https://github.com/user-attachments/assets/2b8c6565-1489-4ac5-bb91-c96aef530626" width="400"/>
</p>

--- 
## 6. 한 줄 회고
- 김서진:
- 김성근:
- 김태희:
- 유수현:
- 정승연:
