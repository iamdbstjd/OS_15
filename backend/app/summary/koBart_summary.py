import re
from preprocess.text_utils import preprocess_text_for_summary
from transformers import BartForConditionalGeneration, PreTrainedTokenizerFast
import torch

# KoBART 모델과 토크나이저 초기화 (전역에서 한 번만)
model_name = "hyunwoongko/kobart"
tokenizer = PreTrainedTokenizerFast.from_pretrained(model_name)
model = BartForConditionalGeneration.from_pretrained(model_name)
model.eval()  # 평가 모드

def split_text_by_length(text, max_length=1000):
    sentences = re.split(r'(?<=[.?!])\s+', text)
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if len(sentence) > max_length:
            if current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = ""
            chunks.append(sentence.strip())
            continue

        if len(current_chunk) + len(sentence) + 1 <= max_length:
            current_chunk += (sentence + " ")
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + " "

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks

def summarize_text(text):
    inputs = tokenizer(text, return_tensors="pt", max_length=1024, truncation=True)
    summary_ids = model.generate(
        inputs["input_ids"],
        max_length=150,
        min_length=50,               # 최소 길이 지정
        num_beams=4,
        early_stopping=True,
        no_repeat_ngram_size=3,
        length_penalty=2.0           # 길이 패널티로 너무 짧은 요약 방지
    )
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return summary

def summarize_long_text(text):
    print("[Main] 원본 텍스트 길이:", len(text))

    # 1) 전처리
    preprocessed_text = preprocess_text_for_summary(text)
    print("[Main] 전처리 후 텍스트 길이:", len(preprocessed_text))

    if len(preprocessed_text) < 100:
        # 짧으면 바로 요약
        return summarize_text(preprocessed_text)

    # 2) 텍스트 분할
    chunks = split_text_by_length(preprocessed_text, max_length=1000)
    print(f"[Main] 분할된 chunk 개수: {len(chunks)}")

    # 3) chunk별 요약
    partial_summaries = []
    for i, chunk in enumerate(chunks):
        print(f"[Main] Chunk {i+1} 요약 중 (길이: {len(chunk)})...")
        summary = summarize_text(chunk)
        print(f"[Main] Chunk {i+1} 요약 결과 일부: {summary[:100]}...")
        partial_summaries.append(summary)

    # 4) 부분 요약들 병합 후 재요약
    combined_summary = " ".join(partial_summaries)
    print("[Main] 부분 요약 결과 병합 완료. 병합된 길이:", len(combined_summary))

    final_summary = summarize_text(combined_summary)
    print("[Main] 최종 요약 결과:", final_summary)

    return final_summary
