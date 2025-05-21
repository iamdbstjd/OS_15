import re

def preprocess_text_for_summary(text: str) -> str:
    if not text:
        return ""

    processed_text = text

    original_fillers = [
        "음 ", "음,",
        "어 ", "어,",
        "그 ", "그,",
        "저기 ", "저기,",
        "이제 좀 ", "일단은 ", "약간 ", "뭐랄까 ", "아무튼 ",
        "글쎄 ", "암튼 ", "뭐냐냐 ",
        "어쨌든 간에 ", "어쨌거나 ", "하여튼 ",
        "다름이 아니라 ",
    ]

    additional_fillers = [
        "네 ", "네,",
        "자 ", "자,",
        "뭐 ", "뭐,",
        "좀 ",
        "막 ",
        "그냥 ",
        "아니 ", "아니,",
        "혹시 ", "혹시,",
        "지금 ", "지금,",
        "일단 ",
        "사실 ", "사실,",
        "대충 ",
        "아마 ",
        "정말 ",
        "진짜 ",
        "완전 ",
        "아주 ",
        "매우 ",
        "엄청 ",
        "되게 ",
        "굉장히 ",
        "이게 ", "이게,",
        "그게 ", "그게,",
        "저게 ", "저게,",
        "이거 ", "이거,",
        "그거 ", "그거,",
        "저거 ", "저거,",
        "그래서 ", "그래서,",
        "근데 ", "근데,",
        "그러니까 ", "그러니까,",
        "그러면 ", "그러면,",
        "게다가 ", "게다가,",
        "이렇게 ", "이렇게,",
        "그렇게 ", "그렇게,",
        "저렇게 ", "저렇게,",
        "어떤 ",
        "이런 거 ", "이런 거,", "이런 건 ", "이런 건,", "이런 게 ", "이런 게,",
        "그런 거 ", "그런 거,", "그런 건 ", "그런 건,", "그런 게 ", "그런 게,",
        "저런 거 ", "저런 거,", "저런 건 ", "저런 건,", "저런 게 ", "저런 게,",
        "예를 들어 ", "예를 들어,",
        "예를 들면 ", "예를 들면,",
        "글쎄요 ", "글쎄요,",
        "바로 ",
    ]

    fillers = original_fillers + additional_fillers

    for filler in fillers:
        processed_text = processed_text.replace(filler, " ")

    processed_text = re.sub(r'\s+', ' ', processed_text).strip()

    if text != processed_text:
        print(f"[Preprocess] 원본 (앞 50자): {text[:50]}...")
        print(f"[Preprocess] 처리 후 (앞 50자): {processed_text[:50]}...")
    else:
        print(f"[Preprocess] 원본과 동일하여 별도 변경 없음 (앞 50자): {text[:50]}...")

    return processed_text