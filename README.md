# 강의 요약 및 퀴즈 생성기 – Frontend

> <span style="color:gray"><strong>단국대학교 오픈소스SW기초 6분반 15조</strong><br>
조원: 박수빈, 변윤성, 이지호</span>

<br><br>

## 이곳은 "frontend" branch입니다.

React를 사용하여 사용자 인터페이스를 구현했습니다. 백엔드와 연동하여 오디오 파일 업로드, 텍스트 요약, 퀴즈 생성을 시각적으로 확인할 수 있도록 구성되어 있습니다.

<br><br>

## 디렉토리 구조

```
OS_15
│  README.md
│
└─frontend
    └─src
        ├── components
        │   ├── Sidebar.css        # 사이드바 스타일
        │   └── Sidebar.js         # 사이드바 컴포넌트
        │
        ├── pages
        │   ├── PageStyles.css     # 페이지 공통 스타일
        │   ├── QuizPage.js        # 퀴즈 결과 페이지
        │   ├── SummaryPage.js     # 요약 결과 페이지
        │   ├── TextPage.js        # STT 텍스트 결과 페이지
        │   └── UploadPage.js      # 오디오 파일 업로드 페이지
        │
        ├── App.js                 # 라우팅 및 전체 페이지 구성
        ├── App.css
        ├── index.js               # React 앱 시작점
        ├── index.css
        ├── reportWebVitals.js
        └── setupTests.js

    .gitignore
    package.json
    package-lock.json

```

<br><br>

## 실행 방법

### 1. 프로젝트 설치 및 실행

```bash
git clone https://github.com/iamdbstjd/OS_15
cd OS_15

cd frontend
npm install
npm start
```

### 2. 백엔드와 연동

백엔드 서버(`localhost:8000`)가 실행 중인 상태여야 프론트에서 정상적으로 요청을 보낼 수 있습니다.

<br><br>

## 페이지 구성

| 경로 | 설명 |
|------|------|
| `/` | 파일 업로드 페이지 |
| `/summary` | 요약 결과를 보여주는 페이지 |
| `/quiz` | 자동 생성된 퀴즈 결과 페이지 |
| `/text` | STT로 변환된 전체 텍스트 확인 페이지 |

<br><br>

## 현재 구현된 기능

-  음성 파일 업로드 UI
-  STT 결과 출력 페이지
-  요약 결과 페이지
-  퀴즈 결과 페이지 틀 (연동 대기)
-  사이드바를 통한 페이지 이동

<br><br>
