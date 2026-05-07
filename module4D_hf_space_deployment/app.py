from __future__ import annotations

import difflib
import json
import os
import re
from pathlib import Path
from typing import Any

import gradio as gr
import pandas as pd

try:
    from openai import OpenAI
except Exception:  # pragma: no cover - import availability depends on runtime
    OpenAI = None


APP_ROOT = Path(__file__).resolve().parent
MODULE2_DIR = APP_ROOT / "module2_outputs"
MODULE3_DIR = APP_ROOT / "module3_outputs"
MODULE4_DIR = APP_ROOT / "module4_outputs"

OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_TEMPERATURE = 0.2
OPENAI_MAX_TOKENS = 500
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY and OpenAI is not None else None
LAST_API_ERROR_MESSAGE = ""


def load_json(path: Path) -> dict:
    """Load a JSON object safely, returning an empty dictionary on failure."""
    if not path.exists():
        return {}
    try:
        with path.open("r", encoding="utf-8") as file:
            obj = json.load(file)
        return obj if isinstance(obj, dict) else {"records": obj}
    except Exception:
        return {}


def load_csv_if_exists(path: Path) -> pd.DataFrame | None:
    """Load a CSV file if present, returning None when unavailable."""
    if not path.exists():
        return None
    try:
        return pd.read_csv(path)
    except Exception:
        return None


def table_records(table: pd.DataFrame | None) -> list[dict[str, Any]]:
    """Convert a pandas table to row dictionaries."""
    if table is None:
        return []
    return table.to_dict(orient="records")


def _safe_items(value: Any) -> list[dict]:
    """Return list-like evidence records safely."""
    return value if isinstance(value, list) else []


def _select_fields(row: dict, fields: list[str]) -> dict:
    """Select available non-empty fields from a row."""
    return {field: row.get(field) for field in fields if field in row and row.get(field) not in (None, "")}


def build_evidence_index(
    pattern_table: pd.DataFrame | None,
    classifier_summary: pd.DataFrame | None,
    evidence_pack: dict,
    grounding_summary: dict,
    llm_analysis: dict,
    llm_ready_patterns: dict,
    module4_quality_summary: dict,
) -> dict:
    """Build compact evidence categories for the deployment chatbot."""
    pattern_fields = [
        "classifier",
        "normalization",
        "error_50",
        "error_70",
        "error_80",
        "error_90",
        "error_100",
        "delta_100_50",
        "relative_increase_pct",
        "trend_label",
        "robustness_flag",
        "spike_type",
        "curve_shape",
        "pattern_strength",
        "degradation_type",
        "pattern_sentence",
    ]
    pattern_records = [_select_fields(row, pattern_fields) for row in table_records(pattern_table)]
    classifier_records = table_records(classifier_summary)
    sensitive = _safe_items(evidence_pack.get("most_sensitive_combinations")) or sorted(
        pattern_records, key=lambda row: float(row.get("delta_100_50", 0) or 0), reverse=True
    )[:5]
    stable = _safe_items(evidence_pack.get("most_stable_combinations")) or sorted(
        pattern_records, key=lambda row: float(row.get("delta_100_50", 999) or 999)
    )[:5]
    classifier_evidence = _safe_items(evidence_pack.get("classifier_level_evidence")) or classifier_records
    normalization_evidence = _safe_items(evidence_pack.get("normalization_level_evidence"))
    if not normalization_evidence and pattern_records:
        normalization_evidence = summarize_mean_delta(pattern_records, "normalization")

    return {
        "classifier_sensitivity": classifier_evidence,
        "normalization_stability": normalization_evidence,
        "split_trend": evidence_pack.get("scenario_overview") or average_split_errors(pattern_records),
        "most_sensitive_combinations": sensitive[:5],
        "most_stable_combinations": stable[:5],
        "llm_grounding_quality": {
            "grounding_summary": grounding_summary,
            "module4_quality_summary": module4_quality_summary,
        },
        "limitations": extract_limitations(llm_analysis),
        "overall_summary": {
            "project": "Cross-batch robustness in ML classification experiments.",
            "scenario_overview": evidence_pack.get("scenario_overview", {}),
            "project_scope": evidence_pack.get("project_scope", {}),
            "llm_ready_patterns_available": bool(llm_ready_patterns),
            "top_sensitive_examples": sensitive[:3],
            "top_stable_examples": stable[:3],
            "quality_status": module4_quality_summary.get("overall_module4_quality_status"),
        },
    }


def summarize_mean_delta(rows: list[dict[str, Any]], key: str) -> list[dict[str, Any]]:
    """Summarize mean delta_100_50 by a categorical key."""
    grouped: dict[str, list[float]] = {}
    for row in rows:
        group = row.get(key)
        try:
            value = float(row.get("delta_100_50"))
        except Exception:
            continue
        if group:
            grouped.setdefault(str(group), []).append(value)
    summaries = [
        {key: group, "mean_delta_100_50": round(sum(values) / len(values), 3), "n_records": len(values)}
        for group, values in grouped.items()
    ]
    return sorted(summaries, key=lambda item: item["mean_delta_100_50"])


def average_split_errors(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Compute average classification error by split when split columns exist."""
    output = []
    for split in [50, 70, 80, 90, 100]:
        values = []
        for row in rows:
            try:
                values.append(float(row.get(f"error_{split}")))
            except Exception:
                pass
        if values:
            output.append({"split": split, "mean_classification_error": round(sum(values) / len(values), 3)})
    return output


def extract_limitations(llm_analysis: dict) -> list[str]:
    """Return limitation evidence with default project caveats."""
    text = json.dumps(llm_analysis, ensure_ascii=False)
    limitations = []
    if "Limitations" in text or "limitations" in text:
        limitations.append("Module 3 LLM analysis includes limitation-related content.")
    limitations.extend(
        [
            "Sample size may be limited.",
            "Pattern extraction is rule-based.",
            "Causality is not established by the saved evidence.",
            "Results depend on available classifiers, normalizations, splits, and configurations.",
        ]
    )
    return limitations


PROJECT_SYNONYM_GROUPS = [
    {"classifier", "model", "algorithm", "method", "分类器", "模型", "算法"},
    {"sensitive", "vulnerable", "unstable", "affected", "batch-sensitive", "batch", "robustness", "robust", "敏感", "受影响", "不稳定", "鲁棒"},
    {"stable", "reliable", "consistent", "稳", "稳定", "鲁棒", "一致"},
    {"normalization", "normalize", "normalisation", "qn", "mn", "vsn", "non", "标准化", "归一化"},
    {"split", "train-test", "batch split", "cross-batch", "split50", "split100", "50", "100", "切分", "分割", "跨batch", "跨批次"},
    {"error", "classification error", "performance", "accuracy", "错误率", "准确率", "表现"},
    {"delta", "increase", "degradation", "gap", "change", "worse", "变化", "增加", "退化", "差距", "变差"},
    {"grounding", "consistency", "hallucination", "evidence", "quality", "trust", "证据", "一致性", "幻觉", "质量", "可信"},
    {"limitation", "caveat", "weakness", "risk", "局限", "限制", "风险", "弱点"},
    {"summary", "conclusion", "main finding", "overall", "总结", "结论", "主要发现", "说明"},
]

SYNONYM_LOOKUP: dict[str, set[str]] = {}
for group in PROJECT_SYNONYM_GROUPS:
    normalized_group = {re.sub(r"\s+", " ", term.lower()).strip() for term in group}
    for term in normalized_group:
        SYNONYM_LOOKUP.setdefault(term, set()).update(normalized_group)


def normalize_query(text: str) -> str:
    """Normalize a user query for deterministic matching."""
    text = (text or "").lower()
    text = text.replace("batch-separated", "batch separated").replace("cross-batch", "cross batch")
    text = re.sub(r"split\s*=\s*(50|100)", r"split \1", text)
    text = re.sub(r"[^\w\s\u4e00-\u9fff]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def tokenize_query(text: str) -> list[str]:
    """Tokenize normalized English/Chinese query text."""
    normalized = normalize_query(text)
    tokens = normalized.split()
    for phrase in ["classification error", "batch split", "cross batch", "main finding", "split 50", "split 100", "受影响", "主要发现", "错误率", "准确率", "跨批次", "跨batch"]:
        if phrase in normalized and phrase not in tokens:
            tokens.append(phrase)
    for chinese_term in ["分类器", "模型", "算法", "敏感", "稳定", "不稳定", "鲁棒", "标准化", "归一化", "切分", "分割", "错误率", "准确率", "证据", "一致性", "幻觉", "质量", "局限", "限制", "风险", "总结", "结论", "说明", "可信"]:
        if chinese_term in normalized and chinese_term not in tokens:
            tokens.append(chinese_term)
    return tokens


def expand_query_terms(tokens: list[str]) -> set[str]:
    """Expand query tokens with project-specific synonyms."""
    expanded = set(tokens)
    joined = " ".join(tokens)
    for term, synonyms in SYNONYM_LOOKUP.items():
        if term in expanded or (" " in term and term in joined):
            expanded.update(synonyms)
    return {term for term in expanded if term}


def scoped_demo_response() -> str:
    """Return the standard response for clearly out-of-scope questions."""
    return (
        "This demo is scoped to the project’s ML experiment results and LLM grounding analysis. "
        "I can answer questions about classifier robustness, normalization stability, split trends, "
        "batch sensitivity, and output quality."
    )


def is_out_of_scope_question(question: str) -> bool:
    """Detect clearly unrelated questions that should not use project evidence."""
    q = normalize_query(question)
    out_terms = [
        "weather",
        "temperature today",
        "forecast",
        "transformer architecture",
        "sort",
        "sorting",
        "python code",
        "write code",
        "medical advice",
        "diagnosis",
        "treatment",
        "recipe",
        "movie",
        "stock price",
        "天气",
        "排序",
        "写代码",
        "医疗建议",
        "诊断",
    ]
    project_terms = [
        "classifier",
        "model",
        "normalization",
        "split",
        "batch",
        "error",
        "delta",
        "grounding",
        "llm",
        "demo",
        "robust",
        "stable",
        "分类器",
        "模型",
        "标准化",
        "归一化",
        "切分",
        "批次",
        "错误率",
        "证据",
        "幻觉",
        "局限",
    ]
    return any(term in q for term in out_terms) and not any(term in q for term in project_terms)


def compact_snippet_text(value: Any, max_chars: int = 900) -> str:
    """Convert one evidence object into compact searchable text."""
    if isinstance(value, dict):
        text = "; ".join(f"{key}: {compact_snippet_text(val, max_chars=160)}" for key, val in list(value.items())[:20])
    elif isinstance(value, list):
        text = " | ".join(compact_snippet_text(item, max_chars=180) for item in value[:8])
    else:
        text = str(value)
    return re.sub(r"\s+", " ", text).strip()[:max_chars]


def build_searchable_evidence_corpus(evidence_index: dict) -> list[dict]:
    """Flatten evidence index categories into searchable snippets."""
    corpus: list[dict] = []
    for category, category_value in evidence_index.items():
        items = category_value if isinstance(category_value, list) else [category_value]
        for idx, item in enumerate(items):
            if item in (None, {}, []):
                continue
            corpus.append(
                {
                    "evidence_id": f"{category}_{idx + 1}",
                    "category": category,
                    "text": compact_snippet_text(item),
                    "source": category,
                    "raw_item": item,
                }
            )
    return corpus


def detect_question_type(question: str) -> str:
    """Classify a natural-language question into a supported demo category."""
    q = normalize_query(question)
    tokens = set(tokenize_query(question))
    expanded = expand_query_terms(list(tokens))

    def direct_has(terms: list[str]) -> bool:
        return any(term in q for term in terms)

    def expanded_has(terms: list[str]) -> bool:
        return any(term in q or term in tokens or term in expanded for term in terms)

    if direct_has(["grounding", "llm output", "llm generated", "llm interpretation", "llm analysis", "hallucination", "trust the llm", "llm回答", "llm分析", "幻觉", "可信"]):
        return "llm_grounding_quality"
    if direct_has(["limitation", "weakness", "caveat", "局限", "限制", "弱点", "老师问", "怎么回答"]):
        return "limitations"
    if direct_has(["largest delta", "highest delta", "changes the most", "riskiest", "worst case", "setting looks the riskiest", "受影响最大", "影响最大", "最不稳定", "最差", "风险最大", "变差"]):
        return "most_sensitive_combinations"
    if direct_has(["normalization", "normalize", "normalisation", "qn", "mn", "vsn", "non", "标准化", "归一化"]):
        if direct_has(["combination", "pair", "setting", "classifier normalization", "classifier-normalization"]):
            return "most_stable_combinations" if direct_has(["stable", "robust", "best", "最稳", "最稳定", "最鲁棒"]) else "most_sensitive_combinations"
        return "normalization_stability"
    if direct_has(["most robust", "most stable combination", "most stable setting", "best combination", "stays stable", "最鲁棒", "最稳", "最稳定"]):
        return "most_stable_combinations"
    if direct_has(["classifier", "model", "algorithm", "which method", "哪个分类器", "哪个模型", "算法"]):
        return "classifier_sensitivity"
    if direct_has(["split", "split 50", "split 100", "50", "100", "increase", "cross batch", "batch separated", "generalization", "切分", "分割", "跨batch", "跨批次", "变大", "区别"]):
        return "split_trend"
    if direct_has(["consistent with", "consistency", "quality", "evidence", "reliable", "is this reliable", "可信吗", "一致性", "证据", "质量"]):
        return "llm_grounding_quality"
    if direct_has(["summary", "main finding", "overall", "conclusion", "what does this tell", "说明", "总结", "结论", "主要发现"]):
        return "overall_summary"
    if expanded_has(["limitation", "caveat", "weakness", "risk"]):
        return "limitations"
    if expanded_has(["grounding", "hallucination", "evidence", "quality", "trust"]):
        return "llm_grounding_quality"
    if expanded_has(["split", "cross-batch", "batch split", "classification error", "delta", "increase"]):
        return "split_trend"
    if expanded_has(["normalization", "normalize", "qn", "mn", "vsn", "non"]):
        return "normalization_stability"
    if expanded_has(["classifier", "model", "algorithm", "method"]):
        return "classifier_sensitivity"
    if expanded_has(["summary", "conclusion", "overall"]):
        return "overall_summary"
    return "unknown"


def rewrite_question_for_project_context(question: str, question_type: str) -> str:
    """Rewrite custom wording into a project-aware question using deterministic rules."""
    q = normalize_query(question)
    if question_type == "most_sensitive_combinations" or any(term in q for term in ["worst", "riskiest", "最不稳定", "受影响最大"]):
        return "Which classifier-normalization combination shows the largest increase in classification error from split 50 to split 100?"
    if question_type == "classifier_sensitivity":
        return "Which classifier appears most unstable or batch-sensitive based on the extracted error-curve evidence?"
    if question_type == "normalization_stability":
        return "Which normalization method appears most stable across classifier error curves?"
    if question_type == "most_stable_combinations":
        return "Which classifier-normalization combinations look most robust based on smaller classification error changes across splits?"
    if question_type == "split_trend":
        return "What do split 50 and split 100 show about cross-batch classification error patterns?"
    if question_type == "llm_grounding_quality":
        return "Is the LLM-generated interpretation grounded in the observed project evidence?"
    if question_type == "limitations":
        return "What limitations should be stated for this demo and analysis?"
    return "What do the extracted classifier-normalization error patterns suggest about cross-batch robustness?"


def score_evidence_snippet(question: str, snippet: dict) -> float:
    """Score one evidence snippet for a question using lightweight hybrid matching."""
    query_tokens = set(tokenize_query(question))
    expanded_query = expand_query_terms(list(query_tokens))
    snippet_tokens = set(tokenize_query(snippet.get("text", "")))
    expanded_snippet = expand_query_terms(list(snippet_tokens))
    if not expanded_query or not expanded_snippet:
        return 0.0
    token_overlap = len(query_tokens & snippet_tokens) / max(len(query_tokens), 1)
    synonym_overlap = len(expanded_query & expanded_snippet) / max(len(expanded_query), 1)
    fuzzy_score = difflib.SequenceMatcher(None, normalize_query(question), normalize_query(snippet.get("text", "")[:500])).ratio()
    detected = detect_question_type(question)
    category_bonus = 0.2 if detected != "unknown" and detected == snippet.get("category") else 0.0
    return (0.35 * token_overlap) + (0.35 * synonym_overlap) + (0.15 * fuzzy_score) + category_bonus


def search_evidence(question: str, evidence_corpus: list[dict], top_k: int = 6, min_score: float = 0.05) -> list[dict]:
    """Search evidence snippets with hybrid scoring."""
    scored = []
    for snippet in evidence_corpus:
        score = score_evidence_snippet(question, snippet)
        if score >= min_score:
            result = dict(snippet)
            result["score"] = round(score, 4)
            scored.append(result)
    scored.sort(key=lambda item: item.get("score", 0), reverse=True)
    if scored:
        return scored[:top_k]
    fallback = []
    for snippet in evidence_corpus:
        if snippet.get("category") in {"overall_summary", "limitations", "llm_grounding_quality"}:
            result = dict(snippet)
            result["score"] = 0.0
            fallback.append(result)
    return fallback[:top_k]


def deduplicate_evidence_items(items: list[dict]) -> list[dict]:
    """Deduplicate retrieved evidence snippets by category and text."""
    seen: set[tuple[str, str]] = set()
    output = []
    for item in items:
        key = (str(item.get("category", "")), str(item.get("text", item.get("raw_item", "")))[:240])
        if key not in seen:
            seen.add(key)
            output.append(item)
    return output


def retrieve_relevant_evidence(question: str, evidence_index: dict, max_items: int = 6) -> dict:
    """Retrieve robust custom-question evidence using intent detection and hybrid search."""
    question_type = detect_question_type(question)
    rewritten_query = rewrite_question_for_project_context(question, question_type)
    if is_out_of_scope_question(question):
        return {
            "question_type": "out_of_scope",
            "rewritten_query": rewritten_query,
            "evidence_items": [],
            "evidence_available": False,
            "retrieval_method": "scoped_out_of_project",
            "fallback_message": scoped_demo_response(),
            "top_scores": [],
        }
    searched = search_evidence(question, EVIDENCE_CORPUS, top_k=max_items)
    category_items: list[dict] = []
    if question_type != "unknown" and evidence_index.get(question_type):
        raw_category = evidence_index.get(question_type)
        raw_items = raw_category if isinstance(raw_category, list) else [raw_category]
        for idx, raw_item in enumerate(raw_items[:max_items]):
            category_items.append(
                {
                    "evidence_id": f"category_{question_type}_{idx + 1}",
                    "category": question_type,
                    "text": compact_snippet_text(raw_item),
                    "source": f"category:{question_type}",
                    "raw_item": raw_item,
                    "score": 1.0,
                }
            )
    merged = deduplicate_evidence_items(category_items + searched)[:max_items]
    return {
        "question_type": question_type,
        "rewritten_query": rewritten_query,
        "evidence_items": merged,
        "evidence_available": bool(merged),
        "retrieval_method": "lightweight_hybrid_evidence_search",
        "fallback_message": "" if merged else "No sufficiently relevant project evidence was retrieved.",
        "top_scores": [
            {"evidence_id": item.get("evidence_id"), "category": item.get("category"), "score": item.get("score", 0)}
            for item in merged[:max_items]
        ],
    }


def format_evidence_for_display(evidence_items: Any, max_chars: int = 1200) -> str:
    """Format evidence compactly for internal prompts."""
    text = json.dumps(evidence_items, indent=2, ensure_ascii=False, default=str)
    return text if len(text) <= max_chars else text[:max_chars] + "\n..."


def generate_template_answer(question: str, retrieved: dict) -> str:
    """Generate a deterministic grounded fallback answer from retrieved evidence."""
    qtype = retrieved.get("question_type", "unknown")
    if qtype == "out_of_scope":
        return scoped_demo_response()
    evidence_items = retrieved.get("evidence_items") or []
    rewritten = retrieved.get("rewritten_query") or question
    if not evidence_items:
        return (
            "Direct answer: The loaded project evidence is insufficient for that specific question.\n\n"
            "Evidence used: No relevant evidence snippets were retrieved.\n\n"
            "Interpretation: Try asking about classifier robustness, normalization stability, split trends, batch sensitivity, grounding quality, limitations, or an overall summary.\n\n"
            "Caveat: This chatbot only answers from loaded project evidence."
        )
    raw_items = [item.get("raw_item", item) if isinstance(item, dict) else item for item in evidence_items]
    preview = format_evidence_for_display(raw_items[:3], max_chars=900)
    top = raw_items[0] if raw_items and isinstance(raw_items[0], dict) else {}
    if qtype in {"most_sensitive_combinations", "classifier_sensitivity"}:
        direct = "The retrieved evidence points to batch sensitivity or larger split-related degradation in the highlighted classifier or classifier-normalization records."
    elif qtype in {"most_stable_combinations", "normalization_stability"}:
        direct = "The retrieved evidence points to relatively stable settings by comparing smaller classification error changes across splits."
    elif qtype == "split_trend":
        direct = "The retrieved evidence indicates that split changes, especially split 50 versus split 100, are associated with changes in classification error patterns."
    elif qtype == "llm_grounding_quality":
        direct = "The retrieved grounding evidence summarizes whether the LLM interpretation is consistent with observed project evidence."
    elif qtype == "limitations":
        direct = "The retrieved evidence supports a cautious limitations answer focused on scenario scope, rule-based extraction, and non-causal interpretation."
    else:
        direct = "The retrieved evidence provides a project-scoped answer about cross-batch robustness patterns."
    if isinstance(top, dict) and top.get("classifier") and top.get("normalization"):
        direct += f" The top retrieved example is {top.get('classifier')}|{top.get('normalization')}."
    return (
        f"Direct answer: {direct}\n\n"
        f"Evidence used: Rewritten project query: {rewritten}. Retrieved evidence preview: {preview}\n\n"
        "Interpretation: This answer is based on extracted project evidence and maps the user's wording to the closest supported project concept.\n\n"
        "Caveat: The answer should not be interpreted as causal, universal, or based on information outside the saved project outputs."
    )


def build_api_prompt(question: str, retrieved: dict) -> list[dict[str, str]]:
    """Build constrained OpenAI chat messages from retrieved project evidence."""
    system_message = (
        "You are an evidence-grounded ML experiment analysis chatbot. "
        "Handle custom wording by mapping it to the closest supported project concept. "
        "Answer only from the retrieved evidence. If evidence is insufficient, say so explicitly. "
        "Do not invent numbers, do not claim causality, and do not use overconfident wording. "
        "Keep the answer concise and presentation-friendly. "
        "Use exactly these four labeled parts: Direct answer, Evidence used, Interpretation, Caveat."
    )
    user_message = (
        f"Original user question: {question}\n"
        f"Rewritten project-aware question: {retrieved.get('rewritten_query')}\n"
        f"Detected question type: {retrieved.get('question_type')}\n"
        f"Retrieval method: {retrieved.get('retrieval_method')}\n"
        f"Top retrieved evidence snippets:\n{json.dumps(retrieved.get('evidence_items'), ensure_ascii=False, indent=2, default=str)}\n\n"
        "Required response format:\n"
        "Direct answer: ...\n"
        "Evidence used: ...\n"
        "Interpretation: ...\n"
        "Caveat: ..."
    )
    return [{"role": "system", "content": system_message}, {"role": "user", "content": user_message}]


def generate_api_answer(question: str, retrieved: dict) -> tuple[str, str]:
    """Generate an API answer or return deterministic fallback."""
    global LAST_API_ERROR_MESSAGE
    LAST_API_ERROR_MESSAGE = ""
    template_answer = generate_template_answer(question, retrieved)
    if retrieved.get("question_type") == "out_of_scope":
        return template_answer, "template_fallback_out_of_scope"
    if not OPENAI_API_KEY or openai_client is None:
        return template_answer, "template_fallback_missing_key"
    if not retrieved.get("evidence_available"):
        return template_answer, "template_fallback_no_evidence"
    try:
        response = openai_client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=build_api_prompt(question, retrieved),
            temperature=OPENAI_TEMPERATURE,
            max_tokens=OPENAI_MAX_TOKENS,
        )
        answer = response.choices[0].message.content if response.choices else ""
        if not answer or not answer.strip():
            return template_answer, "template_fallback_empty_api_response"
        return answer.strip(), "api"
    except Exception as exc:
        LAST_API_ERROR_MESSAGE = f"{type(exc).__name__}: {str(exc)[:160]}"
        return template_answer, "template_fallback_api_error"


def run_lightweight_quality_check(answer: str, retrieved: dict) -> dict:
    """Run lightweight deterministic answer quality checks."""
    warnings = []
    answer_lower = answer.lower()
    if not answer.strip():
        return {"status": "fail", "warnings": ["empty answer"], "evidence_available": False}
    if not retrieved.get("evidence_available", False) and retrieved.get("question_type") != "out_of_scope":
        warnings.append("no evidence available")
    if not any(term in answer_lower for term in ["suggests", "appears", "consistent", "based on", "evidence", "scoped"]):
        warnings.append("cautious evidence language missing")
    forbidden = [term for term in ["proves", "causes", "guarantees", "definitively", "certainly"] if term in answer_lower]
    if forbidden:
        warnings.append(f"forbidden unsupported terms: {forbidden}")
    status = "fail" if forbidden else ("warning" if warnings else "pass")
    return {"status": status, "warnings": warnings, "evidence_available": retrieved.get("evidence_available", False)}


def generate_grounded_answer(question: str, retrieved: dict) -> tuple[str, str, dict]:
    """Generate API answer with deterministic fallback on error or failed quality."""
    answer, answer_source = generate_api_answer(question, retrieved)
    quality = run_lightweight_quality_check(answer, retrieved)
    if answer_source == "api" and quality.get("status") == "fail":
        answer = generate_template_answer(question, retrieved)
        answer_source = "template_fallback_quality_fail"
        quality = run_lightweight_quality_check(answer, retrieved)
    return answer, answer_source, quality


def format_supporting_evidence(retrieved: dict, max_items: int = 5) -> str:
    """Format retrieved evidence as compact Markdown bullets."""
    evidence_items = retrieved.get("evidence_items")
    if not evidence_items:
        return f"- {retrieved.get('fallback_message', 'No supporting evidence available.')}"
    bullets = []
    for item in evidence_items[:max_items]:
        category = item.get("category", "evidence")
        score = item.get("score", "NA")
        text = item.get("text") or compact_snippet_text(item.get("raw_item"))
        bullets.append(f"- [{category}; score={score}] {text[:320]}")
    return "\n".join(bullets)


def chatbot_response(message: str, history: list | None = None) -> str:
    """Return a Gradio-formatted grounded chatbot response."""
    if not message or not message.strip():
        return "Please enter a question about the project results."
    retrieved = retrieve_relevant_evidence(message, EVIDENCE_INDEX)
    answer, answer_source, quality = generate_grounded_answer(message, retrieved)
    evidence_text = format_supporting_evidence(retrieved)
    evidence_sufficiency = "available" if retrieved.get("evidence_available") else "not available or out of scope"
    notes = "; ".join(quality.get("warnings", [])) if quality.get("warnings") else "None"
    return (
        f"### Answer\n{answer}\n\n"
        f"### Evidence used\n{evidence_text}\n\n"
        f"### Evidence sufficiency\n{evidence_sufficiency}\n\n"
        f"### Quality check\nStatus: {quality.get('status', '').upper()}\n\n"
        f"### Answer source\n{answer_source}\n\n"
        f"Notes: {notes}"
    )


LLM_READY_PATTERNS = load_json(MODULE2_DIR / "module2_llm_ready_patterns.json")
PATTERN_TABLE = load_csv_if_exists(MODULE2_DIR / "module2_pattern_table_with_sentences.csv")
CLASSIFIER_SUMMARY = load_csv_if_exists(MODULE2_DIR / "module2_classifier_summary.csv")
EVIDENCE_PACK = load_json(MODULE3_DIR / "module3B_evidence_pack.json")
LLM_ANALYSIS = load_json(MODULE3_DIR / "module3D_llm_analysis.json")
GROUNDING_SUMMARY = load_json(MODULE3_DIR / "module3E_grounding_summary.json")
MODULE4_QUALITY_SUMMARY = load_json(MODULE4_DIR / "module4_answer_quality_summary.json")

EVIDENCE_INDEX = build_evidence_index(
    pattern_table=PATTERN_TABLE,
    classifier_summary=CLASSIFIER_SUMMARY,
    evidence_pack=EVIDENCE_PACK,
    grounding_summary=GROUNDING_SUMMARY,
    llm_analysis=LLM_ANALYSIS,
    llm_ready_patterns=LLM_READY_PATTERNS,
    module4_quality_summary=MODULE4_QUALITY_SUMMARY,
)
EVIDENCE_CORPUS = build_searchable_evidence_corpus(EVIDENCE_INDEX)

EXAMPLE_QUESTIONS = [
    "Which classifier is most batch-sensitive?",
    "Which normalization method appears most stable?",
    "What happens when split changes from 50 to 100?",
    "What are the most robust classifier-normalization combinations?",
    "What are the most sensitive classifier-normalization combinations?",
    "Is the LLM-generated interpretation consistent with the observed evidence?",
    "What are the main limitations of this experiment?",
    "Summarize the main findings of the project.",
    "哪个分类器受 batch 影响最大？",
    "这个 LLM 分析有没有幻觉风险？",
]

demo = gr.ChatInterface(
    fn=chatbot_response,
    title="LLM-Assisted ML Result Analysis Demo",
    description=(
        "Ask questions about classifier robustness, normalization stability, split trends, "
        "batch sensitivity, LLM output grounding, and limitations. The app answers only from "
        "included project evidence and uses deterministic fallback if the OpenAI API is unavailable."
    ),
    examples=EXAMPLE_QUESTIONS,
)


if __name__ == "__main__":
    demo.launch()
