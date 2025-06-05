import re
import random
import nltk
from konlpy.tag import Okt
from collections import Counter

# NLTK 데이터 다운로드 (문장 토큰화에 필요)
try:
    nltk.data.find('tokenizers/punkt')
except Exception:
    nltk.download('punkt', quiet=True)

try:
    nltk.data.find('tokenizers/punkt_tab')
except Exception:
    nltk.download('punkt_tab', quiet=True)

# konlpy Okt 형태소 분석기 초기화
okt = Okt()

def generate_ox_quizzes(text: str, num_quizzes: int = 5, min_word_length: int = 2) -> list[dict]: # 퀴즈 개수 5개로 변경
    if not text or not text.strip():
        return []

    cleaned_text = re.sub(r'[^\w\s가-힣.?!,]', '', text)
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()

    sentences = nltk.sent_tokenize(cleaned_text)
    if not sentences:
        return []

    # 1. 평서문만 퀴즈 후보로 선택
    # 2. 최소 문장 길이 필터 추가 (너무 짧은 문장 제외)
    filtered_sentences_for_ox = []
    min_sentence_char_length = 15 # O/X 퀴즈 문장의 최소 길이

    for s in sentences:
        if '?' in s or '!' in s: # 물음표 또는 느낌표 포함 문장 제외
            print(f"DEBUG: [OX Filter] 물음표/느낌표 포함 문장 제외: {s[:50]}...")
            continue
        
        # 문장 끝이 특정 평서형 어미로 끝나는지 확인 
        if re.search(r'(다|습니다|ㅂ니다|이다)\.?$', s.strip()):
            if len(s.strip()) >= min_sentence_char_length:
                filtered_sentences_for_ox.append(s)
            else:
                print(f"DEBUG: [OX Filter] 너무 짧은 평서문 제외 ({len(s.strip())}자): {s[:50]}...")
        else:
            print(f"DEBUG: [OX Filter] 평서문 어미로 끝나지 않음: {s[:50]}...")

    sentences = filtered_sentences_for_ox

    if not sentences:
        print("[OX_QuizGen] O/X 퀴즈를 만들 적절한 평서문이 없습니다. O/X 퀴즈 생성 불가.")
        return []

    all_nouns_in_text = []
    for sentence in sentences:
        tagged_tokens = okt.pos(sentence, norm=True, stem=True)
        for word, tag in tagged_tokens:
            if tag == 'Noun' and len(word) >= min_word_length and re.fullmatch(r'[가-힣a-zA-Z]+', word):
                all_nouns_in_text.append(word)
    
    if len(all_nouns_in_text) < 2:
        print("[OX_QuizGen] 텍스트 내에 O/X 퀴즈를 만들 충분한 명사 후보가 없습니다.")
        return []

    unique_nouns = list(set(all_nouns_in_text))
    if len(unique_nouns) < 2:
        print("[OX_QuizGen] 텍스트 내에 대체할 고유 명사가 부족합니다.")
        return []

    quizzes_list = []
    processed_sentences = set()

    # O/X 퀴즈 생성에 사용할 불용어 명사 목록 (강화된 목록)
    ox_common_nouns_to_exclude = {
        "것", "수", "때", "점", "분", "이", "그", "저", "말", "부분", "경우", "위", "안", "밖", "내", "중", "등", "번", "가지", "동안", "다시", "하나", "모든", "가장", "다른", "이러한", "이것", "그것", "저것", "여기", "저기", "어디", "무엇", "누구", "언제", "어떻게", "왜", "어떤", "어느",
        "대한", "통해", "위해", "관련", "대해", "따라", "속", "앞", "뒤", "옆", "쪽", "가운데", "사이", "정도", "현재", "미래", "과거", "오늘", "내일", "어제", "이번", "다음", "지난", "매번", "항상", "계속", "점점", "더욱", "아주", "매우", "엄청", "되게", "굉장히", "정말", "진짜", "사실", "아마", "혹시", "지금", "바로", "그냥", "막", "좀", "자", "네", "아니", "음", "어", "그", "저기", "일단", "약간", "뭐랄까", "아무튼", "글쎄", "암튼", "뭐냐", "어쨌든", "하여튼",
        "사람", "언어", "모델", "텍스트", "단어", "함수", "파라미터", "연산", "아키텍처", "메커니즘", "기술", "분야", "혁명", "인공지능", "벡터", "정보", "교환", "과정", "훈련", "예측", "처리", "사용자", "어시스턴트", "데이터", "컴퓨터", "시리즈", "영상", "구독", "회사", "강연", "링크", "대본", "기계", "칩", "알고리즘", "구조", "의미", "맥락", "네트워크", "어텐션", "수학", "확률", "방향", "연구팀", "연구자", "절반", "오류", "내용", "마지막", "억", "년" 
    }

    num_true_quizzes = num_quizzes // 2
    num_false_quizzes = num_quizzes - num_true_quizzes

    true_quiz_candidates_pool = []
    false_quiz_generated = []

    # 참(O) 퀴즈 후보 선정
    for sentence in sentences:
        if sentence not in processed_sentences:
            true_quiz_candidates_pool.append(sentence)

    # 거짓(X) 퀴즈 생성 시도 (명사 대체 방식)
    attempts_false = 0
    max_attempts_false = len(sentences) * 5 
    
    false_sentence_pool = [s for s in sentences if s not in processed_sentences]

    while len(false_quiz_generated) < num_false_quizzes and attempts_false < max_attempts_false and false_sentence_pool:
        attempts_false += 1
        
        candidate_sentence_for_false = random.choice(false_sentence_pool)
        
        tagged_tokens_orig = list(okt.pos(candidate_sentence_for_false, norm=False, stem=False, join=False))
        
        sentence_nouns_for_replacement = []
        for word, tag in tagged_tokens_orig:
            if tag == 'Noun' and len(word) >= min_word_length and re.fullmatch(r'[가-힣a-zA-Z]+', word) and word not in ox_common_nouns_to_exclude:
                sentence_nouns_for_replacement.append(word)
        
        if not sentence_nouns_for_replacement:
            continue

        word_to_replace = random.choice(sentence_nouns_for_replacement)
        
        substitute_nouns_pool = [
            n for n in unique_nouns 
            if n != word_to_replace and n not in ox_common_nouns_to_exclude and n not in candidate_sentence_for_false
        ]
        
        if not substitute_nouns_pool:
            continue

        substitute_word = random.choice(substitute_nouns_pool)
        
        # 원본 문장에서 word_to_replace를 substitute_word로 대체하여 거짓 문장 생성
        false_question_replaced = re.sub(r'\b' + re.escape(word_to_replace) + r'\b', substitute_word, candidate_sentence_for_false, 1)
        
        if false_question_replaced.strip() == candidate_sentence_for_false.strip():
            continue

        false_quiz_generated.append({
            "type": "O/X",
            "question": false_question_replaced.strip(),
            "answer": "X"
        })
        processed_sentences.add(candidate_sentence_for_false)
        if candidate_sentence_for_false in false_sentence_pool:
            false_sentence_pool.remove(candidate_sentence_for_false)


    # 최종 퀴즈 리스트 구성 (참 퀴즈와 거짓 퀴즈를 섞어서)
    random.shuffle(true_quiz_candidates_pool)
    random.shuffle(false_quiz_generated)

    final_quizzes_output = []
    idx_true = 0
    idx_false = 0
    
    while len(final_quizzes_output) < num_quizzes:
        if idx_true < len(true_quiz_candidates_pool) and (len(final_quizzes_output) % 2 == 0 or idx_false >= len(false_quiz_generated)):
            final_quizzes_output.append({
                "type": "O/X",
                "question": true_quiz_candidates_pool[idx_true].strip(),
                "answer": "O"
            })
            idx_true += 1
        elif idx_false < len(false_quiz_generated):
            final_quizzes_output.append(false_quiz_generated[idx_false])
            idx_false += 1
        else:
            break

    if len(final_quizzes_output) < num_quizzes:
        print(f"[OX_QuizGen] 요청한 O/X 퀴즈 수({num_quizzes}개)를 모두 생성하지 못했습니다. (현재 {len(final_quizzes_output)}개)")
        
    return final_quizzes_output
