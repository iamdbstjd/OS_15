# 강의 요약 및 퀴즈 생성기

> <span style="color:gray"><strong>단국대학교 오픈소스SW기초 6분반 15조</strong><br>
조원: 박수빈, 변윤성, 이지호</span>

<br><br>

## 프로젝트 소개
 이 프로젝트는 사용자가 음성 파일을 업로드하면 이를 텍스트로 변환한 뒤, 그 내용을 기반으로 자동으로 퀴즈를 생성해주는 웹 기반 서비스이다. STT(Speech to text)를 담당하는 오픈소스인 '**Whisper**'와 텍스트를 기반으로 퀴즈를 생성해주는 오픈소스인 '**Text2Question**'를 조합했다. 

<br><br>

## 주요 기능
- 🎙 음성 파일 업로드
- 📝 Whisper를 통한 음성 → 텍스트 자동 변환
- 📚 Text2Question을 통한 퀴즈 자동 생성
- 💡 생성된 퀴즈를 웹에서 바로 확인
- 💾 (예정) 생성된 퀴즈와 텍스트를 과목별 분류

<br><br>

## 설치 및 실행 방법
```bash
git clone https://github.com/iamdbstjd/OS_15
cd main
...
```
