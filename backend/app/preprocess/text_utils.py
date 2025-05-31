import re

def preprocess_text_for_summary(text: str) -> str:
    if not text:
        return ""

    filler_patterns = [
        # 너무 많이 제거하지 않고, 필러 단어 앞뒤 쉼표나 공백만 적당히 제거
        r'\b(음|어|그|저기|일단|약간|뭐랄까|아무튼|글쎄|암튼|뭐냐|어쨌든|하여튼)\b[,\s]*',
        r'\b(그게|저게|이거|그거|저거|그래서|근데|그러니까|그러면|게다가|이렇게|그렇게|저렇게)\b[,\s]*',
        r'\b(그런 거|저런 거|예를 들어|바로)\b[,\s]*',
        r'\b(네|자|좀|막|그냥|아니|혹시|지금|사실|아마|정말|진짜|완전|아주|매우|엄청|되게|굉장히)\b[,\s]*',
    ]

    processed_text = text
    for pattern in filler_patterns:
        processed_text = re.sub(pattern, ' ', processed_text)

    # 중복 단어 연속 제거 (너무 강하면 제거)
    processed_text = re.sub(r'\b(\w+)( \1\b)+', r'\1', processed_text)

    # 여러 공백은 하나로
    processed_text = re.sub(r'\s+', ' ', processed_text).strip()

    # 문장 분리 (문장 끝에 마침표, 물음표, 느낌표 뒤 공백 기준)
    sentences = re.split(r'(?<=[.?!])\s+', processed_text)

    # 너무 짧은 문장(15자 미만)만 필터링 (30자 -> 15자로 완화)
    filtered_sentences = [s for s in sentences if len(s) >= 15]

    processed_text = ' '.join(filtered_sentences)

    if text != processed_text:
        print(f"[Preprocess] 원본 (앞 50자): {text[:50]}...")
        print(f"[Preprocess] 처리 후 (앞 50자): {processed_text[:50]}...")
    else:
        print(f"[Preprocess] 원본과 동일하여 별도 변경 없음 (앞 50자): {text[:50]}...")

    return processed_text
