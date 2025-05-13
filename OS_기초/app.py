import os
import shutil
from fastapi import FastAPI, File, UploadFile, Request # HTML 템플릿 사용 시 Request 필요
from fastapi.responses import HTMLResponse # 결과를 HTML 페이지로 보여줄 때 사용
from fastapi.templating import Jinja2Templates
from fastapi.concurrency import run_in_threadpool # 동기 함수를 비동기로 안전하게 실행
from werkzeug.utils import secure_filename # 안전한 파일명 처리 (선택적이지만 권장)

# Main 패키지에서 Azure STT 함수 가져오기
from Main.Azure_STT import transcribe_audio_with_azure # Azure Speech Service 사용하는 함수

# --- FastAPI 앱 및 기본 설정 ---
app = FastAPI(title="강의 음성 STT 서비스 (Azure)")

# --- 폴더 설정 ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # app.py가 있는 현재 폴더
UPLOAD_AUDIO_DIR = os.path.join(BASE_DIR, "uploaded_audio_files") # 오디오 파일 저장 경로
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates") # HTML 템플릿 경로

os.makedirs(UPLOAD_AUDIO_DIR, exist_ok=True) # 폴더 없으면 생성
templates = Jinja2Templates(directory=TEMPLATES_DIR) # 템플릿 폴더 지정

# --- (선택적) 앱 시작 시 이벤트 핸들러 ---
# Azure SDK는 speech_config 객체로 관리되므로,
# Main/whisper.py 내부에서 초기화됩니다. app.py에서 특별히 할 일은 없을 수 있습니다.
@app.on_event("startup")
async def startup_event():
    print("애플리케이션 시작... Azure Speech SDK 설정 확인 (whisper.py 내에서 수행)")
    # 필요하다면 Main.whisper 모듈의 speech_config가 None이 아닌지 여기서 확인 가능
    pass


# --- API 엔드포인트 정의 ---
@app.get("/", response_class=HTMLResponse)
async def get_upload_form_page(request: Request):
    """메인 페이지: 파일 업로드 폼을 포함한 HTML을 렌더링합니다."""
    # 초기에는 아무 결과도 없으므로 None 또는 빈 값으로 전달
    return templates.TemplateResponse("index.html", {
        "request": request,
        "filename": None,
        "transcription": None,
        "summary": None, # 나중에 추가될 요약 결과
        "quizzes": None, # 나중에 추가될 퀴즈 결과
        "error_message": None
    })

@app.post("/process-lecture/", response_class=HTMLResponse) # HTML 폼의 action 경로와 일치
async def process_lecture_audio(
    request: Request, # HTML 템플릿에 request 객체 전달용
    audio_file: UploadFile = File(...) # FastAPI가 업로드된 파일을 받는 방식
):
    """오디오 파일을 업로드 받아 STT 처리하고 결과를 HTML 페이지에 표시합니다."""

    if not audio_file.filename:
        return templates.TemplateResponse("index.html", {"request": request, "error_message": "파일이 선택되지 않았습니다."})

    filename = secure_filename(audio_file.filename)
    saved_filepath = os.path.join(UPLOAD_AUDIO_DIR, filename)

    transcribed_text = None
    summary_text = None # 나중에 구현될 요약 결과 (틀만 잡음)
    quizzes_list = None # 나중에 구현될 퀴즈 결과 (틀만 잡음)
    error_msg = None

    try:
        # 1. 파일 저장
        with open(saved_filepath, "wb") as buffer:
            shutil.copyfileobj(audio_file.file, buffer)
        print(f"파일 저장 완료: {saved_filepath}")

        # 2. Azure Speech STT 실행 (Main/whisper.py의 함수 호출)
        print("[API] Azure Speech Service 처리 시작...")
        transcribed_text = await run_in_threadpool(
            transcribe_audio_with_azure, # 호출할 함수
            saved_filepath               # 함수에 전달할 인자
        )
        print("[API] Azure Speech Service 처리 완료.")

        if transcribed_text is None or "오류:" in transcribed_text: # whisper.py에서 오류 메시지를 반환하는 경우
            error_msg = transcribed_text if transcribed_text else "STT 처리 중 알 수 없는 오류 발생"
            transcribed_text = None # 오류가 있다면 텍스트 결과는 없음으로 처리
        else:
            # --- 3. BART로로 요약 (나중에 구현할 부분 - 현재는 틀만 잡음) ---
            print("[API] BART 요약 처리 시작 예정 (현재는 자리만 마련)...")
            # from Main.bart import summarize_text_with_bart # 나중에 import
            # summary_text = await run_in_threadpool(summarize_text_with_bart, transcribed_text)
            summary_text = "요약 기능은 여기에 표시됩니다. (아직 구현되지 않음)"
            print("[API] BART 요약 처리 건너뜀 (자리만 마련).")

            # --- 4. 퀴즈 생성 (나중에 구현할 부분 - 현재는 틀만 잡음) ---
            print("[API] 퀴즈 생성 시작 예정 (현재는 자리만 마련)...")
            # from Main.quiz_generator import MyQuizGenerator # 나중에 import
            # quiz_generator = MyQuizGenerator() # 필요시 인스턴스화
            # quizzes_list = await run_in_threadpool(quiz_generator.generate_quizzes, summary_text) # 또는 transcribed_text
            quizzes_list = [
                {"type": "O/X", "question": "이곳에 O/X 문제가 표시됩니다. (아직 구현되지 않음) (O/X)", "answer": "미정"},
                {"type": "빈칸", "question": "이곳에 _______ 문제가 표시됩니다. (아직 구현되지 않음)", "answer": "미정"}
            ]
            print("[API] 퀴즈 생성 건너뜀 (자리만 마련).")


    except Exception as e:
        print(f"파일 처리 또는 STT 중 API 레벨 오류: {e}")
        error_msg = f"처리 중 심각한 오류 발생: {str(e)}"
    finally:
        await audio_file.close() # 파일 핸들 항상 닫기

    # 처리 결과를 다시 HTML 템플릿에 담아 사용자에게 보여주기
    return templates.TemplateResponse("index.html", {
        "request": request,
        "filename": filename if not error_msg and transcribed_text else None, # 성공 시에만 파일명 전달
        "transcription": transcribed_text,
        "summary": summary_text,
        "quizzes": quizzes_list,
        "error_message": error_msg
    })

# --- 앱 실행 (터미널에서 'uvicorn app:app --reload' 사용) ---
# if __name__ == "__main__":
#     import uvicorn
#     # 개발 시에는 --reload 옵션을 사용하는 것이 편리합니다.
#     uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)