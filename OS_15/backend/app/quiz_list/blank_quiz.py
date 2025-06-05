import re
import random
import nltk
from konlpy.tag import Okt
from collections import Counter

try:
    nltk.data.find('tokenizers/punkt')
except Exception:
    nltk.download('punkt', quiet=True)

try:
    nltk.data.find('tokenizers/punkt_tab')
except Exception:
    nltk.download('punkt_tab', quiet=True)

okt = Okt()

def generate_blank_quizzes(text: str, num_quizzes: int = 3, min_word_length: int = 2) -> list[dict]:
    if not text or not text.strip():
        return []

    cleaned_text = re.sub(r'[^\w\s가-힣.?!,]', '', text)
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()

    sentences = nltk.sent_tokenize(cleaned_text)
    if not sentences:
        return []

    # 물음표가 포함된 문장은 퀴즈 후보에서 제외
    filtered_sentences_no_questions = []
    for s in sentences:
        if '?' in s:
            print(f"[QuizGen Filter] 물음표 포함 문장 제외: {s[:50]}...")
            continue
        filtered_sentences_no_questions.append(s)
    sentences = filtered_sentences_no_questions

    if not sentences: # 필터링 후 문장이 없으면 퀴즈 생성 불가
        print("[QuizGen] 물음표 문장 필터링 후 남은 문장이 없습니다.")
        return []

    all_noun_candidates = []
    for sentence in sentences:
        tagged_tokens = okt.pos(sentence, norm=True, stem=True)
        for word, tag in tagged_tokens:
            if tag == 'Noun' and len(word) >= min_word_length and re.fullmatch(r'[가-힣a-zA-Z]+', word):
                all_noun_candidates.append(word)

    word_frequencies = Counter(all_noun_candidates)

    quiz_candidates_with_scores = []
    processed_quiz_pairs = set()

    # 퀴즈로 출제하기에 적절하지 않은, 너무 흔하거나 의미가 약한 명사들 
    common_nouns_to_exclude = {
        "것", "수", "때", "점", "분", "이", "그", "저", "곳", "말", "부분", "경우", "위", "아래", "안", "밖", "내", "외", "중", "등", "번", "가지", "동안", "다시", "하나", "모든", "가장", "다른", "이러한", "이것", "그것", "저것", "여기", "저기", "어디", "무엇", "누구", "언제", "어떻게", "왜", "어떤", "어느",
        "대한", "통해", "위해", "관련", "대해", "따라", "속", "앞", "뒤", "옆", "쪽", "가운데", "사이", "정도", "현재", "미래", "과거", "오늘", "내일", "어제", "이번", "다음", "지난", "매번", "항상", "계속", "점점", "더욱", "아주", "매우", "엄청", "되게", "굉장히", "정말", "진짜", "사실", "아마", "혹시", "지금", "바로", "그냥", "막", "좀", "자", "네", "아니", "음", "어", "그", "저기", "일단", "약간", "뭐랄까", "아무튼", "글쎄", "암튼", "뭐냐", "어쨌든", "하여튼",
        "대본", "기계", "단어", "함수", "모델", "텍스트", "대화", "확률", "훈련", "파라미터", "연산", "칩", "알고리즘", "구조", "정보", "의미", "맥락", "네트워크", "어텐션", "기술", "분야", "혁명", "인공지능", "학습", "예측", "처리", "사용자", "어시스턴트", "데이터", "컴퓨터", "시리즈", "영상", "구독", "회사", "강연", "링크"
    }

    for sentence in sentences:
        tokens_with_original_pos = list(okt.pos(sentence, norm=False, stem=False, join=False))
        tagged_tokens_stemmed = list(okt.pos(sentence, norm=True, stem=True))
        
        token_char_spans = []
        current_offset = 0
        for token_word, _ in tokens_with_original_pos:
            start_idx = sentence.find(token_word, current_offset)
            if start_idx == -1: 
                start_idx = current_offset 
            end_idx = start_idx + len(token_word)
            token_char_spans.append((start_idx, end_idx))
            current_offset = end_idx 
            temp_offset = end_idx
            while temp_offset < len(sentence) and sentence[temp_offset].isspace():
                temp_offset += 1
            current_offset = temp_offset

        for j, (word_orig, tag_orig) in enumerate(tokens_with_original_pos):
            if j >= len(tagged_tokens_stemmed):
                continue

            word_stemmed, tag_stemmed = tagged_tokens_stemmed[j]

            if tag_stemmed == 'Noun' and len(word_stemmed) >= min_word_length and re.fullmatch(r'[가-힣a-zA-Z]+', word_stemmed):
                if word_stemmed in common_nouns_to_exclude:
                    continue

                is_compound_form = False
                if j + 1 < len(tagged_tokens_stemmed):
                    next_token_stemmed, next_tag_stemmed = tagged_tokens_stemmed[j+1]
                    if next_tag_stemmed in ['Verb', 'Adjective'] or next_token_stemmed in ['하다', '되다', '이다', '시키다', '받다', '주다', '하고', '되어', '되는', '된', '될', '입니다', '있습니다', '있어', '있는']:
                        is_compound_form = True
                
                if is_compound_form:
                    continue

                quiz_pair_key = (sentence, word_stemmed)
                if quiz_pair_key in processed_quiz_pairs:
                    continue
                processed_quiz_pairs.add(quiz_pair_key)

                score = word_frequencies[word_stemmed] * 0.8 + len(word_stemmed) * 1.0
                quiz_candidates_with_scores.append((score, sentence, word_stemmed, j))

    quiz_candidates_with_scores.sort(key=lambda x: x[0], reverse=True)

    quizzes_list = []
    selected_words_for_blank = set()

    for score, original_sentence, word_to_blank_stemmed, blank_token_idx in quiz_candidates_with_scores:
        if len(quizzes_list) >= num_quizzes:
            break
        
        if word_to_blank_stemmed in selected_words_for_blank:
            continue
        
        tokens_with_original_pos = list(okt.pos(original_sentence, norm=False, stem=False, join=False))
        
        token_spans_in_current_sentence = []
        current_offset_in_sentence = 0
        for token_word, _ in tokens_with_original_pos:
            start_idx = original_sentence.find(token_word, current_offset_in_sentence)
            if start_idx == -1:
                start_idx = current_offset_in_sentence
            end_idx = start_idx + len(token_word)
            token_spans_in_current_sentence.append((start_idx, end_idx))
            current_offset_in_sentence = end_idx
            while current_offset_in_sentence < len(original_sentence) and original_sentence[current_offset_in_sentence].isspace():
                current_offset_in_sentence += 1


        blank_start_char_idx = -1
        blank_end_char_idx = -1
        original_josa_text = ""

        if blank_token_idx < len(token_spans_in_current_sentence):
            blank_start_char_idx = token_spans_in_current_sentence[blank_token_idx][0]
            blank_end_char_idx = token_spans_in_current_sentence[blank_token_idx][1]

            for next_k in range(blank_token_idx + 1, len(tokens_with_original_pos)):
                next_token_word, next_token_tag = tokens_with_original_pos[next_k]
                
                if next_token_tag == 'Josa':
                    next_actual_start = token_spans_in_current_sentence[next_k][0]
                    if next_actual_start == blank_end_char_idx:
                        original_josa_text = next_token_word
                        blank_end_char_idx = token_spans_in_current_sentence[next_k][1]
                    else:
                        break
                else:
                    break
        
        if blank_start_char_idx != -1:
            generic_josa_placeholder = ""
            if original_josa_text:
                if original_josa_text in ["을", "를"]:
                    generic_josa_placeholder = "을/를"
                elif original_josa_text in ["이", "가"]:
                    generic_josa_placeholder = "이/가"
                elif original_josa_text in ["은", "는"]:
                    generic_josa_placeholder = "은/는"
                else:
                    generic_josa_placeholder = original_josa_text
            
            question_text = original_sentence[:blank_start_char_idx] + '_______' + generic_josa_placeholder + original_sentence[blank_end_char_idx:]
            
            quizzes_list.append({
                "type": "빈칸",
                "question": question_text.strip(),
                "answer": word_to_blank_stemmed
            })
            selected_words_for_blank.add(word_to_blank_stemmed)
        else:
            if re.search(r'\b' + re.escape(word_to_blank_stemmed) + r'\b', original_sentence):
                question_text = re.sub(r'\b' + re.escape(word_to_blank_stemmed) + r'\b', '_______', original_sentence, 1)
                quizzes_list.append({
                    "type": "빈칸",
                    "question": question_text.strip(),
                    "answer": word_to_blank_stemmed
                })
                selected_words_for_blank.add(word_to_blank_stemmed)
    
    if len(quizzes_list) < num_quizzes:
        print(f"[QuizGen] 퀴즈 후보가 부족합니다. (현재 {len(quizzes_list)}개, 요청 {num_quizzes}개)")
        
    return quizzes_list