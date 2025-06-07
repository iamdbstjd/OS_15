# 강의 요약 및 퀴즈 생성기

> <span style="color:gray"><strong>단국대학교 오픈소스SW기초 6분반 15조</strong><br>
조원: 박수빈, 변윤성, 이지호</span>

<br><br>

## 이곳은 "backend" branch입니다.

<br><br>

## 디렉토리 구조
```bash
OS_15
│  .env
│  requirements.txt
│
└─app
    │  main.py
    │  __init__.py
    │
    ├─preprocess
    │      text_utils.py
    │
    ├─quiz_list
    │      blank_quiz.py
    │      OX_quiz.py
    │
    ├─stt
    │      audio_splitter.py
    │      azure_stt.py
    │
    └─summary
            koBart_summary.py
            textrank_summary.py
```
