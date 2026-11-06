"""Small, transparent TF-IDF-like lexical retriever for the starter corpus."""

from __future__ import annotations

import json
import math
import re
import unicodedata
from collections import Counter
from pathlib import Path

CORPUS_PATH = Path(__file__).with_name("corpus.jsonl")

TOPIC_CUES = {
    "Biến và kiểu dữ liệu": ("bien", "gan", "kieu du lieu", "int", "float", "str", "bool", "type(", "ep kieu", "input", "nhap", "in ra", "dau vao", "phep tinh"),
    "Điều kiện if/else": ("if", "elif", "else", "dieu kien", "so sanh", "and", "or", "toan tu logic", "chan le", "so chan", "so le", "chia het", "lon hon", "nho hon", "kiem tra", "truong hop"),
    "Vòng lặp": ("vong lap", "for", "while", "range", "break", "continue", "lap qua", "tong cac so", "tu 1 den", "lap n lan", "duyet", "giai thua", "fibonacci", "so nguyen to", "in day"),
    "Hàm": ("ham", "def", "return", "tham so", "doi so", "gia tri tra ve"),
    "Lỗi thường gặp": ("loi", "error", "traceback", "syntaxerror", "indentationerror", "nameerror", "typeerror", "valueerror", "debug"),
}

SYNONYMS = {
    "function": "ham", "functions": "ham", "method": "ham", "loop": "vong lap",
    "loops": "vong lap", "variable": "bien", "variables": "bien", "condition": "dieu kien",
    "conditions": "dieu kien", "integer": "int", "string": "str", "boolean": "bool",
    "parameter": "tham so", "parameters": "tham so", "argument": "doi so", "arguments": "doi so",
    "error": "loi", "bug": "loi", "indentation": "thut le", "print": "in ra",
}

CODING_REQUEST_PATTERNS = (
    r"\bgiup\b.{0,60}\b(?:code|lap trinh|viet chuong trinh|giai bai|lam bai)\b",
    r"\b(?:code|viet|giai|lam)\b.{0,45}\b(?:bai toan|bai tap|chuong trinh)\b",
    r"\b(?:solve|write|code)\b.{0,45}\b(?:python problem|exercise|program)\b",
)
PROBLEM_DETAIL_CUES = (
    "de bai", "yeu cau", "nhap", "in ra", "xuat", "tinh", "tim", "kiem tra",
    "tong", "chan le", "so chan", "so le", "chia het", "so nguyen to", "so doi xung", "doi xung", "palindrome",
    "giai thua", "fibonacci", "tu 1 den", "cho n", "input", "output", "vi du",
    "for ", "while ", "if ", "def ", "```",
)
def fold(value: str) -> str:
    value = unicodedata.normalize("NFD", value.lower())
    value = "".join(char for char in value if unicodedata.category(char) != "Mn")
    return value.replace("đ", "d")


def terms(value: str) -> list[str]:
    value = fold(value)
    for original, replacement in SYNONYMS.items():
        value = re.sub(rf"\b{re.escape(original)}\b", replacement, value)
    return re.findall(r"[a-z_][a-z_0-9]*|[0-9]+", value)


def load_corpus() -> list[dict]:
    rows = [json.loads(line) for line in CORPUS_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not rows:
        raise RuntimeError("Knowledge corpus is empty")
    required = {"id", "topic", "title", "source", "url", "section", "text"}
    if any(not required.issubset(row) for row in rows):
        raise RuntimeError("A corpus entry is missing required metadata")
    return rows


CORPUS = load_corpus()
DOC_TERMS = [Counter(terms(f"{row['topic']} {row['title']} {row['section']} {row['text']}")) for row in CORPUS]
AVG_LENGTH = sum(sum(doc.values()) for doc in DOC_TERMS) / len(DOC_TERMS)
DF = Counter(term for doc in DOC_TERMS for term in doc)


def detect_topic(question: str) -> str | None:
    topics = detect_topics(question)
    return topics[0] if len(topics) == 1 else None


def detect_topics(question: str) -> list[str]:
    folded = f" {fold(question)} "
    found = []
    for topic, cues in TOPIC_CUES.items():
        if any(re.search(rf"(?<![a-z0-9_]){re.escape(fold(cue))}(?![a-z0-9_])", folded) if cue.isascii() else cue in question for cue in cues):
            found.append(topic)
    return found


def is_coding_request(question: str) -> bool:
    value = fold(question)
    return any(re.search(pattern, value) for pattern in CODING_REQUEST_PATTERNS)


def has_problem_details(question: str) -> bool:
    value = fold(question)
    has_code = "```" in question or bool(re.search(r"\b(?:def|for|while|if)\s+\w+", value))
    return has_code or any(cue in value for cue in PROBLEM_DETAIL_CUES)


def needs_problem_statement(question: str) -> bool:
    return is_coding_request(question) and not has_problem_details(question)


def retrieve(question: str, limit: int = 3) -> list[dict]:
    value = fold(question)
    expansions = []
    if any(cue in value for cue in ("chan le", "so chan", "so le", "chia het")):
        expansions.append("dieu kien if else toan tu chia lay du modulo so du")
    if any(cue in value for cue in ("tinh tong", "tong cac so", "tu 1 den", "giai thua", "fibonacci", "so nguyen to")):
        expansions.append("vong lap for range while duyet cac so")
    if is_coding_request(question):
        expansions.append("bai tap python thuat toan dau vao dau ra bien dieu kien vong lap")
    query_terms = Counter(terms(" ".join([question, *expansions])))
    if not query_terms:
        return []
    query = set(query_terms)
    ranked = []
    for row, doc in zip(CORPUS, DOC_TERMS):
        length = sum(doc.values())
        score = 0.0
        for term, q_count in query_terms.items():
            frequency = doc.get(term, 0)
            if not frequency:
                continue
            inverse = math.log(1 + (len(CORPUS) - DF[term] + 0.5) / (DF[term] + 0.5))
            saturation = frequency * 2.2 / (frequency + 1.2 * (0.25 + 0.75 * length / AVG_LENGTH))
            score += inverse * saturation * min(q_count, 2)
        if score:
            ranked.append((score, len(query & set(doc)), row))
    ranked.sort(key=lambda item: (-item[0], -item[1], item[2]["id"]))
    return [
        {**row, "score": round(score, 4)}
        for score, overlap, row in ranked[:limit]
        if overlap >= 1
    ]


