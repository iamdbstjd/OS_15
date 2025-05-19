import os
import shutil
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.concurrency import run_in_threadpool
from werkzeug.utils import secure_filename
from stt.azure_stt import transcribe_audio_with_azure
from summary.bart_summary import summarize_text

app = FastAPI(title="강의 음성 STT 서비스 (Azure)")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_AUDIO_DIR = os.path.join(BASE_DIR, "uploaded_audio_files")
os.makedirs(UPLOAD_AUDIO_DIR, exist_ok=True)


@app.get("/")
async def root():
    return {"message": "강의 음성 STT 서비스 API입니다. POST /process-lecture/ 로 오디오 파일을 업로드하세요."}


@app.post("/process-lecture/")
async def process_lecture_audio(audio_file: UploadFile = File(...)):
    if not audio_file.filename:
        raise HTTPException(status_code=400, detail="파일이 선택되지 않았습니다.")

    filename = secure_filename(audio_file.filename)
    saved_filepath = os.path.join(UPLOAD_AUDIO_DIR, filename)

    try:
        # 1. 파일 저장
        with open(saved_filepath, "wb") as buffer:
            shutil.copyfileobj(audio_file.file, buffer)

        # 2. Azure STT 실행
        transcribed_text = await run_in_threadpool(transcribe_audio_with_azure, saved_filepath)

        if not transcribed_text or "오류:" in transcribed_text:
            error_msg = transcribed_text or "STT 처리 중 알 수 없는 오류 발생"
            return JSONResponse(status_code=500, content={"error": error_msg})

        # 3. 요약 처리
        summary_text = await run_in_threadpool(summarize_text, transcribed_text)

        # 4. 퀴즈 자리 마련 (미구현)
        quizzes_list = [
            {"type": "O/X", "question": "이곳에 O/X 문제가 표시됩니다. (아직 구현되지 않음)", "answer": "미정"},
            {"type": "빈칸", "question": "이곳에 _______ 문제가 표시됩니다. (아직 구현되지 않음)", "answer": "미정"},
        ]

        return {
            "filename": filename,
            "transcription": transcribed_text,
            "summary": summary_text,
            "quizzes": quizzes_list,
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"처리 중 오류 발생: {str(e)}"})
    finally:
        await audio_file.close()
