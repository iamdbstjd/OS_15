import re
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import networkx as nx
from sentence_transformers import SentenceTransformer

try:
    from ..preprocess.text_utils import preprocess_text_for_summary
except ImportError:
    print("Warning: Could not import 'preprocess_text_for_summary' from ..preprocess.text_utils.")
    print("Using a dummy preprocess_text_for_summary for now if this script is run standalone.")
    def preprocess_text_for_summary(text: str) -> str:
        return re.sub(r'\s+', ' ', text).strip()

SENTENCE_MODEL_NAME = 'jhgan/ko-sroberta-multitask'
FALLBACK_SENTENCE_MODEL_NAME = 'sentence-transformers/xlm-r-100langs-bert-base-nli-stsb-mean-tokens'
sentence_model = None
try:
    sentence_model = SentenceTransformer(SENTENCE_MODEL_NAME)
except Exception:
    try:
        sentence_model = SentenceTransformer(FALLBACK_SENTENCE_MODEL_NAME)
    except Exception:
        pass

def split_sentences_texrank(text: str) -> list[str]:
    if not text or not text.strip():
        return []
    sentences = re.split(r'(?<=[.?!])\s+(?=[A-Z가-힣])', text.strip())
    sentences = [s.strip() for s in sentences if s.strip()]
    return sentences

def embed_sentences_textrank(sentences: list[str]) -> np.ndarray | None:
    if not sentence_model:
        return None
    if not sentences:
        return np.array([])
    try:
        embeddings = sentence_model.encode(sentences)
        return embeddings
    except Exception:
        return None

def build_similarity_matrix_textrank(sentence_embeddings: np.ndarray) -> np.ndarray | None:
    if sentence_embeddings is None or sentence_embeddings.size == 0:
        return np.array([])
    if sentence_embeddings.ndim == 1:
        return np.array([[1.0]]) if sentence_embeddings.size > 0 else np.array([])
    if sentence_embeddings.shape[0] < 1:
        return np.array([])
    if sentence_embeddings.shape[0] == 1:
        return np.array([[1.0]])
    try:
        sim_matrix = cosine_similarity(sentence_embeddings, sentence_embeddings)
        return sim_matrix
    except Exception:
        return None

def apply_textrank_algorithm(similarity_matrix: np.ndarray, similarity_threshold: float = 0.1) -> list[tuple[int, float]]:
    if similarity_matrix is None or similarity_matrix.size == 0 or similarity_matrix.shape[0] == 0:
        return []
    processed_matrix = np.where(similarity_matrix < similarity_threshold, 0, similarity_matrix)
    try:
        nx_graph = nx.from_numpy_array(processed_matrix)
        if not nx_graph.nodes() or not nx_graph.edges():
            if nx_graph.nodes():
                num_nodes = len(nx_graph.nodes())
                return sorted(((i, 1.0/num_nodes if num_nodes > 0 else 0) for i in nx_graph.nodes()), key=lambda x: x[1], reverse=True)
            return []
        scores = nx.pagerank(nx_graph, alpha=0.85, max_iter=500, tol=1.0e-6)
    except Exception:
        try:
            nx_graph = nx.from_numpy_array(processed_matrix)
            if not nx_graph.nodes() or not nx_graph.edges():
                if nx_graph.nodes():
                    num_nodes = len(nx_graph.nodes())
                    return sorted(((i, 1.0/num_nodes if num_nodes > 0 else 0) for i in nx_graph.nodes()), key=lambda x: x[1], reverse=True)
                return []
            scores = nx.pagerank_numpy(nx_graph, alpha=0.85)
        except Exception:
            return []
            
    return sorted(((i, score) for i, score in scores.items()), key=lambda x: x[1], reverse=True)

def apply_mmr_to_ranked_sentences(
    ranked_sentences_with_scores: list[tuple[int, float]],
    sentence_embeddings: np.ndarray,
    num_to_select: int,
    lambda_val: float = 0.5
) -> list[int]:
    if not ranked_sentences_with_scores or num_to_select == 0 or sentence_embeddings.size == 0:
        return []

    max_score = 0.0
    if ranked_sentences_with_scores:
        non_zero_scores = [s for _, s in ranked_sentences_with_scores if s > 0]
        if non_zero_scores:
            max_score = max(non_zero_scores)
        elif ranked_sentences_with_scores:
             max_score = 1.0 if ranked_sentences_with_scores[0][1] == 0 and len(ranked_sentences_with_scores) > 0 else max_score


    normalized_scores = {idx: score / max_score if max_score > 0 else 0
                         for idx, score in ranked_sentences_with_scores}

    selected_indices = []
    candidate_indices_pool = [idx for idx, score in ranked_sentences_with_scores]

    if not candidate_indices_pool:
        return []
        
    first_sentence_index = ranked_sentences_with_scores[0][0]
    selected_indices.append(first_sentence_index)

    while len(selected_indices) < num_to_select:
        remaining_candidate_indices = [idx for idx in candidate_indices_pool if idx not in selected_indices]
        if not remaining_candidate_indices:
            break

        mmr_scores = []
        current_selected_embeddings = sentence_embeddings[selected_indices]
        
        if current_selected_embeddings.ndim == 1:
            current_selected_embeddings_reshaped = current_selected_embeddings.reshape(1, -1)
        else:
            current_selected_embeddings_reshaped = current_selected_embeddings

        for cand_idx in remaining_candidate_indices:
            original_score = normalized_scores.get(cand_idx, 0)
            cand_embedding = sentence_embeddings[cand_idx].reshape(1, -1)
            
            similarities = cosine_similarity(cand_embedding, current_selected_embeddings_reshaped)
            max_similarity_to_selected = np.max(similarities) if similarities.size > 0 else 0
            
            mmr_score = lambda_val * original_score - (1 - lambda_val) * max_similarity_to_selected
            mmr_scores.append((cand_idx, mmr_score))
        
        if not mmr_scores:
            break

        mmr_scores.sort(key=lambda x: x[1], reverse=True)
        next_best_idx = mmr_scores[0][0]
        
        selected_indices.append(next_best_idx)

    return selected_indices


def summarize_with_textrank(text: str, 
                            num_sentences_to_select_ratio: float = 0.2, 
                            min_sentences: int = 5,
                            max_sentences: int = 15,
                            similarity_graph_threshold: float = 0.15,
                            lambda_mmr: float = 0.5,
                            use_mmr: bool = True,
                            filter_endings: bool = True,
                            preprocess_function_to_use=preprocess_text_for_summary,
                            perform_preprocessing: bool = True) -> str:
    # 1. 오류 처리 및 전처리
    if not sentence_model:
        return "오류: 문장 임베딩 모델이 로드되지 않았습니다. TextRank 요약을 진행할 수 없습니다."
    if not text or not text.strip():
        return "입력 텍스트가 비어있거나 공백만 포함하고 있습니다."

    processed_text = text
    if perform_preprocessing:
        processed_text = preprocess_function_to_use(text)
        
    if not processed_text or not processed_text.strip():
        return "전처리 후 또는 입력된 텍스트가 비어있습니다."

    # 2. 문장 분리
    sentences = split_sentences_texrank(processed_text)
    if not sentences:
        return "텍스트에서 문장을 분리할 수 없습니다."

    target_num_sentences = int(len(sentences) * num_sentences_to_select_ratio)
    num_sentences_to_select_final = max(min_sentences, min(target_num_sentences, max_sentences))
    num_sentences_to_select_final = min(num_sentences_to_select_final, len(sentences))
    
    if not sentences or num_sentences_to_select_final == 0:
        return "텍스트에서 문장을 분리할 수 없거나 요약할 문장이 없습니다."

    # 3. 문장 임베딩
    sentence_embeddings = embed_sentences_textrank(sentences)
    if sentence_embeddings is None or sentence_embeddings.size == 0:
        return "문장 벡터화(임베딩)에 실패했습니다."

    # 4. 유사도 행렬 생성
    similarity_matrix = build_similarity_matrix_textrank(sentence_embeddings)
    if similarity_matrix is None or similarity_matrix.size == 0:
        return "유사도 행렬 생성에 실패했습니다."

    # 5. TextRank 알고리즘 적용
    ranked_sentence_indices_with_scores = apply_textrank_algorithm(similarity_matrix, similarity_threshold=similarity_graph_threshold)
    
    if not ranked_sentence_indices_with_scores:
        if len(sentences) == 1: return sentences[0]
        return "TextRank 점수 계산에 실패했거나 유의미한 핵심 문장을 찾지 못했습니다."

    # 6. 핵심 문장 선택 (MMR 적용 여부)
    selected_indices_unfiltered: list[int]
    if use_mmr:
        selected_indices_unfiltered = apply_mmr_to_ranked_sentences(
            ranked_sentence_indices_with_scores,
            sentence_embeddings,
            num_sentences_to_select_final,
            lambda_mmr
        )
    else: 
        actual_num_to_select = min(num_sentences_to_select_final, len(ranked_sentence_indices_with_scores))
        top_sentence_tuples = ranked_sentence_indices_with_scores[:actual_num_to_select]
        selected_indices_unfiltered = [idx for idx, score in top_sentence_tuples]
    
    if not selected_indices_unfiltered:
        return "핵심 문장을 선택하지 못했습니다."

    # 7. 마무리 인사 필터링
    final_selected_indices = []
    if filter_endings:
        closing_patterns = [
            r"다음 영상에서 뵐게요", r"구독과 좋아요", r"감사합니다", r"고생하셨습니다",
            r"문의사항은.*남겨주세요", r"시청해 주세요", r"궁금한 점 있으시면", r"좋아요와 구독",
            r"더 자세히 알고 싶으시다면", r"링크를 남겨 둘 테니", r"다음 영상에서 만나요",
            r"저는 맨날 씁니다",
            r"시청해 주세요"
        ]
        
        for idx in selected_indices_unfiltered:
            sentence_text = sentences[idx]
            is_closing = False
            for pattern in closing_patterns:
                if re.search(pattern, sentence_text, re.IGNORECASE):
                    is_closing = True
                    break
            if not is_closing:
                final_selected_indices.append(idx)
        
        if not final_selected_indices and selected_indices_unfiltered:
            final_selected_indices = selected_indices_unfiltered
    else:
        final_selected_indices = selected_indices_unfiltered
            
    if not final_selected_indices:
        return "필터링 후 또는 문장 선택 과정에서 최종적으로 선택된 문장이 없습니다."

    # 8. 최종 요약 문장 생성 및 후처리
    final_selected_indices.sort() 
    summary_sentences = [sentences[i] for i in final_selected_indices]

    cleaned_summary_sentences = []
    noise_patterns_per_sentence = [
        r'[\s\W_]+$',
        r'^[\s\W_]+',
        r'(\s*아\s*){2,}',
        r'(\s*음\s*){2,}',
        r'(\s*어\s*){2,}',
        r'\s*xxx\s*',
        r'(\s*([.?!,;:])){2,}',
        r'\s*-\s*',
        r'^\s*[\W_]+',
        r'[\W_]+\s*$',
        r'\s{2,}',
    ]

    for sentence in summary_sentences:
        cleaned_sentence = sentence.strip()
        for pattern in noise_patterns_per_sentence:
            cleaned_sentence = re.sub(pattern, ' ', cleaned_sentence).strip()
        
        if cleaned_sentence and not re.search(r'[.?!]$', cleaned_sentence):
            cleaned_sentence += '.'

        if cleaned_sentence:
            cleaned_summary_sentences.append(cleaned_sentence)

    final_summary = "\n".join(cleaned_summary_sentences)
    return final_summary