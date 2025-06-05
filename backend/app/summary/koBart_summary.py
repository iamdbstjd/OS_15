import re
from .textrank_summary import summarize_with_textrank 
from ..preprocess.text_utils import preprocess_text_for_summary 
from transformers import BartForConditionalGeneration, PreTrainedTokenizerFast
import torch

# KoBART 모델 및 토크나이저 초기화
model_name = "hyunwoongko/kobart"
tokenizer = PreTrainedTokenizerFast.from_pretrained(model_name)
model = BartForConditionalGeneration.from_pretrained(model_name)
model.eval()

if torch.cuda.is_available():
    model.to("cuda")
else:
    pass

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

def summarize_text(text: str,
                   max_summary_length: int = 250,
                   min_summary_length: int = 40,
                   num_beams: int = 1,
                   length_penalty: float = 1.5,
                   no_repeat_ngram_size: int = 3,
                   repetition_penalty: float = 3.0,
                   do_sample: bool = True,
                   top_k: int = 50,
                   top_p: float = 0.95) -> str:
    if not text.strip():
        return ""
            
    inputs = tokenizer(text, return_tensors="pt", max_length=1024, truncation=True, padding="max_length")
    
    if torch.cuda.is_available():
        inputs = {k: v.to("cuda") for k, v in inputs.items()}

    try:
        summary_ids = model.generate(
            inputs["input_ids"],
            attention_mask=inputs["attention_mask"],
            max_length=max_summary_length,
            min_length=min_summary_length,
            num_beams=num_beams,
            early_stopping=True,
            no_repeat_ngram_size=no_repeat_ngram_size,
            length_penalty=length_penalty,
            repetition_penalty=repetition_penalty,
            do_sample=do_sample,
            top_k=top_k,
            top_p=top_p
        )
        summary = tokenizer.decode(summary_ids[0].to("cpu"), skip_special_tokens=True)
        return summary.strip()
    except Exception as e:
        return "요약 중 오류 발생: KoBART 모델 처리 실패"


def summarize_long_text(
    text: str,
    textrank_params: dict = None,
    kobart_final_max_length: int = 700,
    kobart_final_min_length: int = 150
    ) -> str:
    # 1. TextRank 요약 시작
    default_textrank_params = {
        "num_sentences_to_select_ratio": 0.25,
        "min_sentences": 5,
        "max_sentences": 15,
        "similarity_graph_threshold": 0.15,
        "lambda_mmr": 0.5,
        "use_mmr": True,
        "filter_endings": True,
        "perform_preprocessing": False
    }
    current_textrank_params = {**default_textrank_params, **(textrank_params or {})}

    # 2. TextRank 요약 실행
    textrank_summary = summarize_with_textrank(
        text,
        num_sentences_to_select_ratio=current_textrank_params["num_sentences_to_select_ratio"],
        min_sentences=current_textrank_params["min_sentences"],
        max_sentences=current_textrank_params["max_sentences"],
        similarity_graph_threshold=current_textrank_params["similarity_graph_threshold"],
        lambda_mmr=current_textrank_params["lambda_mmr"],
        use_mmr=current_textrank_params["use_mmr"],
        filter_endings=current_textrank_params["filter_endings"],
        perform_preprocessing=current_textrank_params["perform_preprocessing"]
    )

    # 3. TextRank 결과 오류 처리 및 반환
    if not textrank_summary.strip() or "오류:" in textrank_summary or "실패" in textrank_summary or "없습니다" in textrank_summary:
        return textrank_summary if textrank_summary.strip() and ("오류:" in textrank_summary or "실패" in textrank_summary or "없습니다" in textrank_summary) else "TextRank 요약 생성 중 문제가 발생했습니다."

    return textrank_summary 