
import os
import time
import azure.cognitiveservices.speech as speechsdk

AZURE_SPEECH_KEY = "실제 키 값" #카톡으로 보내드리겠습니다
AZURE_SPEECH_REGION = "koreacentral" 

# Speech SDK 설정 객체 초기화
speech_config = None


if AZURE_SPEECH_KEY and AZURE_SPEECH_REGION:
    try:
        speech_config = speechsdk.SpeechConfig(subscription=AZURE_SPEECH_KEY, region=AZURE_SPEECH_REGION)
        speech_config.speech_recognition_language = "ko-KR"  
        print(f"[Azure Speech] SpeechConfig 초기화 완료. 지역: {AZURE_SPEECH_REGION}")
    except Exception as e:
        print(f"[Azure Speech] SpeechConfig 초기화 중 오류 발생: {e}")
        speech_config = None  # 오류 발생 시 None으로 명시적 설정
else:
    print("[Azure Speech] 경고: Azure Speech 구독 키 또는 지역 정보가 설정되지 않았습니다.")
    print("     Main/Azure_STT.py 파일 상단의 AZURE_SPEECH_KEY와 AZURE_SPEECH_REGION에")
    print("     실제 발급받은 정확한 정보를 입력해주세요. API 호출이 실패합니다.")
    speech_config = None # 이 경우에도 None으로 명시


# --- 이하 transcribe_audio_with_azure 함수 및 테스트 코드는 이전과 동일 ---
def transcribe_audio_with_azure(audio_filepath: str) -> str | None:
    global speech_config
    if speech_config is None:
        error_msg = "오류: Azure SpeechConfig가 초기화되지 않았습니다. 파일 상단의 구독 키와 지역 설정을 확인해주세요."
        print(f"[Azure Speech] {error_msg}")
        return error_msg # 오류 메시지 반환 (또는 API 호출 실패를 명시)
    
    # ... (이하 함수 내용은 이전 답변과 동일하게 유지) ...
    if not os.path.exists(audio_filepath):
        error_msg = f"오류: 음성 파일 경로를 찾을 수 없습니다 - {audio_filepath}"
        print(f"[Azure Speech] {error_msg}")
        return error_msg

    print(f"[Azure Speech] 음성 파일 처리 시작: {audio_filepath}")
    
    audio_config = speechsdk.audio.AudioConfig(filename=audio_filepath)
    speech_recognizer = None 
    all_recognized_text_parts = []
    recognition_done = False 

    def recognized_text_handler(evt: speechsdk.SpeechRecognitionEventArgs):
        nonlocal all_recognized_text_parts
        if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
            all_recognized_text_parts.append(evt.result.text)
        elif evt.result.reason == speechsdk.ResultReason.NoMatch:
            print("음성을 인식하지 못했습니다 (NOMATCH).")
        elif evt.result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = evt.result.cancellation_details
            print(f"음성 인식이 취소되었습니다: {cancellation_details.reason}")
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                print(f"취소 오류 상세: {cancellation_details.error_details}")

    def session_stopped_handler(evt: speechsdk.SessionEventArgs):
        nonlocal recognition_done
        print(f"인식 세션 중지됨: {evt}")
        recognition_done = True

    try:
        speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
        speech_recognizer.recognized.connect(recognized_text_handler)
        speech_recognizer.session_stopped.connect(session_stopped_handler)
        speech_recognizer.canceled.connect(recognized_text_handler) 

        speech_recognizer.start_continuous_recognition_async().get() 
        
        print("[Azure Speech] 연속 인식 시작됨. 파일 처리를 기다립니다...")
        timeout_seconds = 300 
        start_time = time.time()
        while not recognition_done:
            if time.time() - start_time > timeout_seconds:
                print("[Azure Speech] 처리 시간 초과!")
                break
            time.sleep(0.5)
        
    except Exception as e:
        print(f"[Azure Speech] 인식 과정 중 예외 발생: {e}")
        return f"Azure Speech API 처리 오류: {e}"
    finally:
        if speech_recognizer and not recognition_done: 
            print("[Azure Speech] 명시적으로 인식 중지 시도...")
            try:
                speech_recognizer.stop_continuous_recognition_async().get()
            except Exception as stop_e:
                print(f"[Azure Speech] 인식 중지 중 오류 발생: {stop_e}")
        elif speech_recognizer and recognition_done: 
            print("[Azure Speech] 인식 세션 정상 종료됨.")


    if not all_recognized_text_parts:
        print("[Azure Speech] 최종적으로 인식된 텍스트가 없습니다.")
        return "오류: 인식된 텍스트가 없음 (NoMatch 또는 빈 오디오 가능성)"

    full_transcribed_text = " ".join(all_recognized_text_parts)
    print("[Azure Speech] 음성 파일 처리 완료.")
    return full_transcribed_text


if __name__ == '__main__':
    if speech_config is None: # speech_config가 None이면 키/지역 정보가 유효하지 않거나 설정되지 않은 것
        print("테스트를 진행할 수 없습니다. 파일 상단의 Azure Speech 키/지역 정보를 정확히 입력했는지 확인해주세요.")
    else:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        test_file_name = "sample.mp3" 
        test_file_relative_path = os.path.join("..", "uploaded_audio_files", test_file_name)
        test_file_abs_path = os.path.normpath(os.path.join(current_dir, test_file_relative_path))

        if os.path.exists(test_file_abs_path):
            print(f"\n--- Azure Speech Service 단독 테스트 시작 (파일: {test_file_abs_path}) ---")
            text_result = transcribe_audio_with_azure(test_file_abs_path)
            
            print("\n[변환된 텍스트 결과]")
            if text_result and not text_result.startswith("오류:"):
                print(text_result)
            else:
                print(f"텍스트 변환 실패 또는 오류: {text_result}")
        else:
            print(f"테스트할 오디오 파일이 없습니다: {test_file_abs_path}")