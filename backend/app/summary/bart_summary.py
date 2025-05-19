from transformers import BartForConditionalGeneration, BartTokenizer

model = None
tokenizer = None

def summarize_text(text: str, max_length=130, min_length=30) -> str:
    global model, tokenizer

    if not text.strip():
        return "요약할 텍스트가 비어 있습니다."

    try:
        if model is None or tokenizer is None:
            model_name = "facebook/bart-large-cnn"
            tokenizer = BartTokenizer.from_pretrained(model_name)
            model = BartForConditionalGeneration.from_pretrained(model_name)

        inputs = tokenizer([text], max_length=1024, return_tensors='pt', truncation=True)
        summary_ids = model.generate(
            inputs['input_ids'],
            num_beams=4,
            max_length=max_length,
            min_length=min_length,
            early_stopping=True
        )
        return tokenizer.decode(summary_ids[0], skip_special_tokens=True)

    except Exception as e:
        return f"요약 중 오류 발생: {str(e)}"