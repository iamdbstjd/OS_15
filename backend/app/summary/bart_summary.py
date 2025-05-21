from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

model = None
tokenizer = None
model_name = "gogamza/kobart-summarization"

def summarize_text(text: str, max_summary_length=300, min_summary_length=30) -> str:
    global model, tokenizer

    if not text.strip():
        return "요약할 텍스트가 비어 있습니다."

    try:
        if model is None or tokenizer is None:
            print(f"[Summarizer] 모델 및 토크나이저 로딩 시작: {model_name}")
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
            print("[Summarizer] 모델 및 토크나이저 로딩 완료.")
        
        print(f"[Summarizer] 토큰화 시작. 입력 텍스트 길이: {len(text)}")
        inputs = tokenizer(
            [text],
            max_length=1024,
            return_tensors='pt',
            truncation=True,
            padding="longest"
        )
        print("[Summarizer] 토큰화 완료. 요약 생성 시작...")

        summary_ids = model.generate(
                inputs['input_ids'],
                num_beams=4, 
                max_length=max_summary_length,
                min_length=min_summary_length,
                repetition_penalty=1.5,  
                no_repeat_ngram_size=3, 
                early_stopping=True     
    		
	)

        print(f"[Summarizer] 생성된 summary_ids: {summary_ids}")
        print("[Summarizer] 요약 생성 완료. 디코딩 시작...")
        
        summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        print("[Summarizer] 디코딩 완료.")
        return summary

    except Exception as e:
        print(f"[Summarizer] 요약 중 오류 발생: {e}")
        return f"요약 중 오류 발생: {str(e)}"
