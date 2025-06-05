import os
import shutil
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import run_in_threadpool
from werkzeug.utils import secure_filename
from pydub import AudioSegment

from .stt.azure_stt import transcribe_multiple_files
from .stt.audio_splitter import split_audio 
from .summary.koBart_summary import summarize_long_text
from .preprocess.text_utils import preprocess_text_for_summary
from .quiz_list.blank_quiz import generate_blank_quizzes
from .quiz_list.OX_quiz import generate_ox_quizzes


app = FastAPI(title="강의 음성 STT 서비스 (Azure)")

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_AUDIO_DIR = os.path.join(BASE_DIR, "uploaded_audio_files")
os.makedirs(UPLOAD_AUDIO_DIR, exist_ok=True)

def convert_audio_to_wav(source_path: str, target_dir: str) -> str | None:
    filename_without_ext, original_ext = os.path.splitext(os.path.basename(source_path))
    wav_filename = f"{filename_without_ext}_converted.wav"
    wav_filepath = os.path.join(target_dir, wav_filename)
    try:
        print(f"[CONVERT] 오디오 파일 변환 시도: {source_path} -> {wav_filepath}")
        audio_format = original_ext.replace('.', '')
        if not audio_format:
            audio = AudioSegment.from_file(source_path)
        else:
            audio = AudioSegment.from_file(source_path, format=audio_format)
        audio.export(wav_filepath, format="wav")
        print(f"[CONVERT] 오디오 파일 변환 성공: {wav_filepath}")
        return wav_filepath
    except Exception as e:
        print(f"[CONVERT ERROR] {source_path} -> WAV 변환 중 오류 발생: {e}")
        return None

@app.get("/")
async def root():
    return {"message": "강의 음성 STT 서비스 API입니다. POST /process-lecture/ 로 오디오 파일을 업로드하세요."}

@app.post("/process-lecture/")
async def process_lecture_audio(audio_file: UploadFile = File(...)):
    if not audio_file.filename:
        raise HTTPException(status_code=400, detail="파일이 선택되지 않았습니다.")

    original_filename = secure_filename(audio_file.filename)
    original_saved_filepath = os.path.join(UPLOAD_AUDIO_DIR, original_filename)
    
    filepath_for_stt = original_saved_filepath
    converted_temp_file_path = None

    try:
        # 1. 오디오 파일 저장
        with open(original_saved_filepath, "wb") as buffer:
            shutil.copyfileobj(audio_file.file, buffer)

        # 2. mp3 → wav 변환
        file_extension = os.path.splitext(original_filename)[1].lower()
        if file_extension == ".mp3":
            print(f"[PROCESS] MP3 파일 감지: {original_filename}. WAV로 변환합니다...")
            converted_temp_file_path = await run_in_threadpool(
                convert_audio_to_wav, original_saved_filepath, UPLOAD_AUDIO_DIR
            )
            if not converted_temp_file_path:
                raise HTTPException(status_code=500, detail="MP3를 WAV로 변환하는 데 실패했습니다.")
            filepath_for_stt = converted_temp_file_path

        # 3. 오디오 분할
        audio_chunks = await run_in_threadpool(split_audio, filepath_for_stt, UPLOAD_AUDIO_DIR)
        if not audio_chunks:
            raise HTTPException(status_code=500, detail="오디오 분할에 실패했습니다.")

        # 4. 조각별 STT 수행
        transcribed_text = await run_in_threadpool(transcribe_multiple_files, audio_chunks)
        if not transcribed_text or ("오류:" in str(transcribed_text)):
            error_detail = transcribed_text if transcribed_text else "STT 처리 중 알 수 없는 오류 발생 또는 빈 결과"
            raise HTTPException(status_code=500, detail=f"STT 처리 실패: {error_detail}")

        # 5. 전처리
        print("[Main] STT 완료. 텍스트 전처리 시작...")
        preprocessed_text = await run_in_threadpool(preprocess_text_for_summary, transcribed_text)
        print("[Main] 텍스트 전처리 완료.")

        # 6. 요약
        summary_text = await run_in_threadpool(summarize_long_text, preprocessed_text)
        if "요약 중 오류 발생:" in str(summary_text):
            raise HTTPException(status_code=500, detail=f"요약 처리 실패: {summary_text}")

        # 7. 퀴즈 생성
        print("[Main] 퀴즈 생성 시작...")
        
        # 빈칸 퀴즈 생성 
        blank_quizzes = await run_in_threadpool(generate_blank_quizzes, preprocessed_text, num_quizzes=5)
        print(f"[Main] 빈칸 퀴즈 생성 완료. 생성된 퀴즈 개수: {len(blank_quizzes)}")

        # O/X 퀴즈 생성 
        ox_quizzes = await run_in_threadpool(generate_ox_quizzes, preprocessed_text, num_quizzes=5) # <-- 이 부분을 num_quizzes=5로 변경
        print(f"[Main] O/X 퀴즈 생성 완료. 생성된 퀴즈 개수: {len(ox_quizzes)}")

        # 모든 퀴즈를 합치기
        quizzes_list = blank_quizzes + ox_quizzes
        
        if not quizzes_list:
            print("[Main] 퀴즈 생성 실패 또는 생성된 퀴즈 없음. 기본 퀴즈 리스트를 사용합니다.")
            quizzes_list = [
                {"type": "O/X", "question": "이곳에 O/X 문제가 표시됩니다. (아직 구현되지 않음)", "answer": "미정"},
                {"type": "빈칸", "question": "이곳에 _______ 문제가 표시됩니다. (아직 구현되지 않음)", "answer": "미정"},
            ]


        return {
            "filename": original_filename,
            "transcription": transcribed_text,
            "summary": summary_text,
            "quizzes": quizzes_list,
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"[Main App Error] /process-lecture/ endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"서버 내부 처리 중 예기치 않은 오류 발생: {str(e)}")
    finally:
        await audio_file.close()
        if converted_temp_file_path and os.path.exists(converted_temp_file_path):
            try:
                os.remove(converted_temp_file_path)
                print(f"[CLEANUP] 임시 변환 파일 삭제: {converted_temp_file_path}")
            except OSError as e:
                print(f"[CLEANUP ERROR] 임시 파일 삭제 실패: {converted_temp_file_path}, 오류: {e}")
