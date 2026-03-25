"""Pure-algorithm text quality analysis — no AI required."""

import re
import math
from collections import Counter


def analyze_text(text: str) -> dict:
    """Analyze text quality and return metrics.
    
    Returns dict with:
    - char_count: total characters
    - word_count: Chinese word approximation (Chinese chars + whitespace-separated tokens)
    - sentence_count: number of sentences
    - paragraph_count: number of paragraphs
    - avg_sentence_length: average sentence length in characters
    - unique_word_ratio: ratio of unique words to total (lexical diversity)
    - paragraph_balance: 0-100 score of how balanced paragraph lengths are (100 = perfectly balanced)
    - reading_time_minutes: estimated reading time (Chinese ~400 chars/min)
    - readability_score: composite 0-100 score
    - details: sub-scores breakdown
    """
    if not text or not text.strip():
        return _empty_result()

    text = text.strip()

    # --- Basic counts ---
    # Characters (exclude whitespace)
    chars_only = re.sub(r'\s', '', text)
    char_count = len(chars_only)

    # Chinese characters
    chinese_chars = re.findall(r'[\u4e00-\u9fff]', text)
    chinese_count = len(chinese_chars)

    # Words: Chinese characters as individual words + non-Chinese whitespace-split tokens
    non_chinese = re.sub(r'[\u4e00-\u9fff]', ' ', text)
    non_chinese_words = [w for w in non_chinese.split() if re.search(r'[a-zA-Z]', w)]
    word_count = chinese_count + len(non_chinese_words)

    # Sentences: split by Chinese/English sentence terminators
    sentences = re.split(r'[。！？.!?\n]+', text)
    sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 1]
    sentence_count = max(len(sentences), 1)

    # Paragraphs: split by double newlines or single newlines with content
    paragraphs = re.split(r'\n\s*\n|\n', text)
    paragraphs = [p.strip() for p in paragraphs if p.strip() and len(p.strip()) > 1]
    paragraph_count = max(len(paragraphs), 1)

    # --- Derived metrics ---
    # Average sentence length
    sentence_lengths = [len(re.sub(r'\s', '', s)) for s in sentences]
    avg_sentence_length = round(sum(sentence_lengths) / len(sentence_lengths), 1) if sentence_lengths else 0

    # Unique word ratio (lexical diversity) — for Chinese, use character bigrams
    if chinese_count > 2:
        bigrams = [chinese_chars[i] + chinese_chars[i+1] for i in range(len(chinese_chars) - 1)]
        all_tokens = bigrams + non_chinese_words
    else:
        all_tokens = list(chars_only)
    
    token_counter = Counter(all_tokens)
    unique_count = len(token_counter)
    total_tokens = len(all_tokens) if all_tokens else 1
    unique_word_ratio = round(unique_count / total_tokens, 3)

    # Paragraph balance: how evenly distributed paragraph lengths are
    if paragraph_count > 1:
        para_lens = [len(re.sub(r'\s', '', p)) for p in paragraphs]
        mean_len = sum(para_lens) / len(para_lens)
        if mean_len > 0:
            variance = sum((l - mean_len) ** 2 for l in para_lens) / len(para_lens)
            cv = math.sqrt(variance) / mean_len  # coefficient of variation
            # cv=0 means perfect balance. Convert to 0-100 score.
            paragraph_balance = max(0, round(100 * (1 - min(cv, 1.5) / 1.5)))
        else:
            paragraph_balance = 100
    else:
        paragraph_balance = 100  # single paragraph is "balanced"

    # Reading time: Chinese ~400 chars/min, English ~200 words/min
    reading_time = round((chinese_count / 400 + len(non_chinese_words) / 200), 1)
    reading_time = max(reading_time, 0.1)

    # --- Composite readability score (0-100) ---
    # Factors:
    #   1. Sentence length comfort: ideal 15-30 chars for Chinese. Penalize extremes.
    #   2. Lexical diversity: higher is better (0.3-0.8 is good)
    #   3. Paragraph balance: already 0-100
    #   4. Structure: having multiple paragraphs is better for long text

    # Sentence length score (0-100)
    if avg_sentence_length < 5:
        sent_score = 40
    elif avg_sentence_length < 10:
        sent_score = 60 + (avg_sentence_length - 5) * 4
    elif avg_sentence_length <= 30:
        sent_score = 80 + min((avg_sentence_length - 10), 10) * 2
    elif avg_sentence_length <= 50:
        sent_score = 100 - (avg_sentence_length - 30) * 1.5
    else:
        sent_score = max(30, 70 - (avg_sentence_length - 50))
    sent_score = max(0, min(100, round(sent_score)))

    # Lexical diversity score (0-100)
    if unique_word_ratio < 0.1:
        lex_score = 30
    elif unique_word_ratio < 0.3:
        lex_score = 30 + (unique_word_ratio - 0.1) * 200
    elif unique_word_ratio <= 0.8:
        lex_score = 70 + (unique_word_ratio - 0.3) * 60
    else:
        lex_score = 100
    lex_score = max(0, min(100, round(lex_score)))

    # Structure score (0-100): reward appropriate paragraph count for text length
    if char_count < 100:
        struct_score = 80  # short text doesn't need many paragraphs
    else:
        ideal_para_count = max(2, char_count // 200)
        ratio = paragraph_count / ideal_para_count
        if 0.5 <= ratio <= 2.0:
            struct_score = 90
        elif 0.3 <= ratio <= 3.0:
            struct_score = 70
        else:
            struct_score = 50
    struct_score = max(0, min(100, round(struct_score)))

    # Weighted composite
    readability_score = round(
        sent_score * 0.30 +
        lex_score * 0.25 +
        paragraph_balance * 0.20 +
        struct_score * 0.25
    )
    readability_score = max(0, min(100, readability_score))

    return {
        "char_count": char_count,
        "word_count": word_count,
        "sentence_count": sentence_count,
        "paragraph_count": paragraph_count,
        "avg_sentence_length": avg_sentence_length,
        "unique_word_ratio": unique_word_ratio,
        "paragraph_balance": paragraph_balance,
        "reading_time_minutes": reading_time,
        "readability_score": readability_score,
        "details": {
            "sentence_length_score": sent_score,
            "lexical_diversity_score": lex_score,
            "paragraph_balance_score": paragraph_balance,
            "structure_score": struct_score,
        },
    }


def _empty_result() -> dict:
    return {
        "char_count": 0,
        "word_count": 0,
        "sentence_count": 0,
        "paragraph_count": 0,
        "avg_sentence_length": 0,
        "unique_word_ratio": 0,
        "paragraph_balance": 0,
        "reading_time_minutes": 0,
        "readability_score": 0,
        "details": {
            "sentence_length_score": 0,
            "lexical_diversity_score": 0,
            "paragraph_balance_score": 0,
            "structure_score": 0,
        },
    }
