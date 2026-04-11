import json
import re
from typing import Any

import requests
from fastapi import HTTPException

from api.config import COGNEE_API_KEY, COGNEE_BASE_URL, COGNEE_DATASET_NAME
from api.schemas import CogneeFeedbackRequest


def is_cognee_configured() -> bool:
    return bool(COGNEE_API_KEY and COGNEE_BASE_URL)


def safe_json(response: requests.Response):
    try:
        return response.json()
    except Exception:
        return {"raw": response.text}


def normalize_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, (int, float, bool)):
        return str(value)
    if isinstance(value, list):
        return " ".join(filter(None, (normalize_text(item) for item in value)))
    if isinstance(value, dict):
        preferred_keys = [
            "content",
            "text",
            "answer",
            "message",
            "summary",
            "question",
            "result",
            "description",
            "label",
            "name",
        ]
        collected = [normalize_text(value.get(key)) for key in preferred_keys if key in value]
        if any(collected):
            return " ".join(filter(None, collected))
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def require_cognee():
    if not is_cognee_configured():
        raise HTTPException(status_code=500, detail="Cognee REST API is not configured.")


def cognee_headers():
    require_cognee()
    return {"X-Api-Key": COGNEE_API_KEY}


def cognee_json_headers():
    headers = cognee_headers()
    headers["Content-Type"] = "application/json"
    return headers


def cognee_url(path: str):
    if not path.startswith("/"):
        path = f"/{path}"
    return f"{COGNEE_BASE_URL}{path}"


def cognee_dataset_name(dataset_name: str | None):
    return dataset_name or COGNEE_DATASET_NAME


def cognee_post_add(transcript: str, dataset_name: str):
    transcript = transcript.strip()
    if not transcript:
        raise HTTPException(status_code=400, detail="Transcript is empty.")

    upload_part = [("data", ("context.txt", transcript.encode("utf-8"), "text/plain"))]
    attempts = [
        {
            "url": cognee_url("/api/add"),
            "kwargs": {
                "headers": cognee_headers(),
                "data": {"datasetName": dataset_name},
                "files": upload_part,
                "timeout": 120,
            },
        },
        {
            "url": cognee_url("/api/v1/add"),
            "kwargs": {
                "headers": cognee_headers(),
                "data": {"datasetName": dataset_name},
                "files": upload_part,
                "timeout": 120,
            },
        },
        {
            "url": cognee_url("/api/add_text"),
            "kwargs": {
                "headers": cognee_json_headers(),
                "json": {"textData": [transcript], "datasetName": dataset_name},
                "timeout": 120,
            },
        },
    ]

    last_error = None
    for attempt in attempts:
        response = requests.post(attempt["url"], **attempt["kwargs"])
        if response.ok:
            return safe_json(response)
        last_error = response

    detail = safe_json(last_error)
    raise HTTPException(status_code=last_error.status_code, detail=detail)


def cognee_post_cognify(dataset_name: str):
    payloads = [
        {"datasets": [dataset_name], "runInBackground": False},
        {"datasets": [dataset_name], "run_in_background": False},
    ]
    paths = ["/api/cognify", "/api/v1/cognify"]

    last_error = None
    for path in paths:
        for payload in payloads:
            response = requests.post(
                cognee_url(path),
                headers=cognee_json_headers(),
                json=payload,
                timeout=180,
            )
            if response.ok:
                return safe_json(response)
            last_error = response

    detail = safe_json(last_error)
    raise HTTPException(status_code=last_error.status_code, detail=detail)


def cognee_search(query: str, dataset_name: str, top_k: int = 5):
    query = query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Search query is required.")

    payloads = [
        {
            "searchType": "GRAPH_COMPLETION",
            "datasets": [dataset_name],
            "query": query,
            "topK": top_k,
            "onlyContext": False,
        },
        {
            "search_type": "GRAPH_COMPLETION",
            "datasets": [dataset_name],
            "query": query,
            "top_k": top_k,
            "only_context": False,
        },
    ]
    paths = ["/api/search", "/api/v1/search"]

    last_error = None
    for path in paths:
        for payload in payloads:
            response = requests.post(
                cognee_url(path),
                headers=cognee_json_headers(),
                json=payload,
                timeout=120,
            )
            if response.ok:
                return safe_json(response)
            last_error = response

    detail = safe_json(last_error)
    raise HTTPException(status_code=last_error.status_code, detail=detail)


def cognee_list_datasets():
    last_error = None
    for path in ("/api/v1/datasets", "/api/datasets"):
        response = requests.get(
            cognee_url(path),
            headers=cognee_json_headers(),
            timeout=60,
        )
        if response.ok:
            return safe_json(response)
        last_error = response

    detail = safe_json(last_error)
    raise HTTPException(status_code=last_error.status_code, detail=detail)


def find_dataset_id(dataset_name: str):
    try:
        dataset_response = cognee_list_datasets()
    except HTTPException:
        return None
    if isinstance(dataset_response, list):
        datasets = dataset_response
    else:
        datasets = (
            dataset_response.get("datasets")
            or dataset_response.get("items")
            or dataset_response.get("data")
            or []
        )

    for dataset in datasets:
        if dataset.get("name") == dataset_name:
            return dataset.get("id")
    return None


def extract_dataset_id_from_search_result(search_result: Any):
    if isinstance(search_result, list):
        for item in search_result:
            dataset_id = extract_dataset_id_from_search_result(item)
            if dataset_id:
                return dataset_id
        return None

    if isinstance(search_result, dict):
        for key in ("dataset_id", "datasetId"):
            value = search_result.get(key)
            if value:
                return str(value)

        for key in ("results", "search_results", "data", "items"):
            container = search_result.get(key)
            dataset_id = extract_dataset_id_from_search_result(container)
            if dataset_id:
                return dataset_id

    return None


def cognee_get_dataset_graph(dataset_id: str):
    if not dataset_id:
        return {
            "nodes": [],
            "edges": [],
            "message": "Graph unavailable because the search response did not include a dataset id.",
        }

    paths = [
        f"/api/v1/datasets/{dataset_id}/graph",
        f"/api/datasets/{dataset_id}/graph",
    ]
    last_error = None
    for path in paths:
        response = requests.get(
            cognee_url(path),
            headers=cognee_json_headers(),
            timeout=60,
        )
        if response.ok:
            return safe_json(response)
        last_error = response

    return {
        "error": safe_json(last_error) if last_error is not None else "Graph fetch failed",
        "message": "Graph visualization is unavailable for this dataset or tenant configuration.",
        "nodes": [],
        "edges": [],
    }


def extract_search_context(search_result: Any):
    if isinstance(search_result, list):
        return [normalize_text(item).strip() for item in search_result if normalize_text(item).strip()]

    if isinstance(search_result, dict):
        containers = [
            search_result.get("results"),
            search_result.get("search_results"),
            search_result.get("data"),
            search_result.get("context"),
            search_result.get("items"),
        ]
        for container in containers:
            if isinstance(container, list):
                texts = [normalize_text(item).strip() for item in container if normalize_text(item).strip()]
                if texts:
                    return texts

        text = normalize_text(search_result).strip()
        return [text] if text else []

    text = normalize_text(search_result).strip()
    return [text] if text else []


def compact_contexts(contexts: list[Any], limit: int = 5):
    cleaned: list[str] = []
    for item in contexts:
        text = normalize_text(item).strip()
        if not text:
            continue
        if text not in cleaned:
            cleaned.append(text)
        if len(cleaned) >= limit:
            break
    return cleaned


def build_feedback_query(payload: CogneeFeedbackRequest):
    parts = [
        payload.category.strip(),
        payload.question.strip(),
        f"Correct answer: {payload.correct_answer.strip()}." if payload.correct_answer.strip() else "",
        f"User answer: {payload.user_answer.strip()}." if payload.user_answer.strip() else "",
        payload.insight.strip(),
    ]
    return " ".join(part for part in parts if part).strip()


def tokenize_feedback(query: str, contexts: list[str]):
    combined = " ".join([query, *contexts]).lower()
    tokens = re.findall(r"[a-z0-9][a-z0-9_.-]{2,}", combined)
    stopwords = {
        "the",
        "and",
        "that",
        "with",
        "from",
        "this",
        "what",
        "when",
        "your",
        "user",
        "answer",
        "correct",
        "question",
        "analysis",
        "should",
        "have",
        "into",
    }
    return {token for token in tokens if token not in stopwords}


def graph_nodes_and_edges(raw_graph: Any):
    if isinstance(raw_graph, dict):
        if isinstance(raw_graph.get("nodes"), list) and isinstance(raw_graph.get("edges"), list):
            return raw_graph["nodes"], raw_graph["edges"]
        data = raw_graph.get("data")
        if isinstance(data, dict):
            return graph_nodes_and_edges(data)
    return [], []


def graph_node_label(node: dict):
    return (
        node.get("label")
        or node.get("name")
        or node.get("title")
        or normalize_text(node.get("properties"))
        or node.get("type")
        or "Node"
    )


def graph_node_text(node: dict):
    return " ".join(
        filter(
            None,
            [
                normalize_text(node.get("label")),
                normalize_text(node.get("name")),
                normalize_text(node.get("title")),
                normalize_text(node.get("type")),
                normalize_text(node.get("properties")),
            ],
        )
    ).lower()


def build_feedback_graph(raw_graph: Any, query: str, contexts: list[str]):
    raw_nodes, raw_edges = graph_nodes_and_edges(raw_graph)
    if not raw_nodes:
        return {"nodes": [], "edges": []}

    tokens = tokenize_feedback(query, contexts)
    prepared_nodes = []
    for node in raw_nodes:
        node_id = str(node.get("id") or node.get("uuid") or node.get("name") or graph_node_label(node))
        text = graph_node_text(node)
        matched = bool(tokens and any(token in text for token in tokens))
        prepared_nodes.append(
            {
                "id": node_id,
                "label": graph_node_label(node),
                "type": node.get("type") or "Entity",
                "matched": matched,
                "properties": node.get("properties") or {},
            }
        )

    matched_ids = {node["id"] for node in prepared_nodes if node["matched"]}
    edge_source_keys = ("source", "from", "start", "source_id")
    edge_target_keys = ("target", "to", "end", "target_id")
    prepared_edges = []
    for edge in raw_edges:
        source = next((edge.get(key) for key in edge_source_keys if edge.get(key) is not None), None)
        target = next((edge.get(key) for key in edge_target_keys if edge.get(key) is not None), None)
        if source is None or target is None:
            continue
        prepared_edges.append(
            {
                "id": str(edge.get("id") or f"{source}-{target}"),
                "source": str(source),
                "target": str(target),
                "label": normalize_text(edge.get("label") or edge.get("type")),
            }
        )

    if matched_ids:
        connected_ids = set(matched_ids)
        for edge in prepared_edges:
            if edge["source"] in matched_ids or edge["target"] in matched_ids:
                connected_ids.add(edge["source"])
                connected_ids.add(edge["target"])
        selected_ids = connected_ids
    else:
        selected_ids = {node["id"] for node in prepared_nodes[:10]}

    nodes = [node for node in prepared_nodes if node["id"] in selected_ids][:18]
    selected_id_set = {node["id"] for node in nodes}
    edges = [
        edge
        for edge in prepared_edges
        if edge["source"] in selected_id_set and edge["target"] in selected_id_set
    ][:24]
    return {"nodes": nodes, "edges": edges}


def truncate_label(text: str, limit: int = 84):
    clean = " ".join(text.split())
    if len(clean) <= limit:
        return clean
    return f"{clean[: limit - 1].rstrip()}…"


def build_feedback_fallback_graph(payload: CogneeFeedbackRequest, query: str, contexts: list[str]):
    question_label = truncate_label(payload.question or query or "Question")
    correct_label = payload.correct_answer.strip().upper() or "?"
    user_label = payload.user_answer.strip().upper() or "No answer"
    category_label = payload.category.strip() or "Quiz"

    nodes = [
        {
            "id": "question",
            "label": question_label,
            "type": category_label,
            "matched": True,
            "properties": {"role": "question"},
        },
        {
            "id": "correct-answer",
            "label": f"Correct: {correct_label}",
            "type": "Correct Answer",
            "matched": True,
            "properties": {"role": "correct_answer"},
        },
        {
            "id": "user-answer",
            "label": f"Your answer: {user_label}",
            "type": "User Answer",
            "matched": user_label == correct_label and user_label != "No answer",
            "properties": {"role": "user_answer"},
        },
    ]

    if payload.insight.strip():
        nodes.append(
            {
                "id": "insight",
                "label": truncate_label(payload.insight.strip()),
                "type": "Insight",
                "matched": True,
                "properties": {"role": "insight"},
            }
        )

    edges = [
        {"id": "question-correct", "source": "question", "target": "correct-answer", "label": "expects"},
        {"id": "question-user", "source": "question", "target": "user-answer", "label": "answered"},
    ]

    if payload.insight.strip():
        edges.append({"id": "correct-insight", "source": "correct-answer", "target": "insight", "label": "explains"})

    for index, context in enumerate(contexts[:4]):
        node_id = f"context-{index + 1}"
        nodes.append(
            {
                "id": node_id,
                "label": truncate_label(context, 110),
                "type": "Evidence",
                "matched": True,
                "properties": {"role": "context"},
            }
        )
        edges.append(
            {
                "id": f"correct-context-{index + 1}",
                "source": "correct-answer",
                "target": node_id,
                "label": "supported by",
            }
        )

    return {"nodes": nodes, "edges": edges}


def ingest_text_to_cognee(text: str, dataset_name: str):
    add_result = cognee_post_add(text, dataset_name)
    cognify_result = cognee_post_cognify(dataset_name)
    dataset_id = find_dataset_id(dataset_name)
    return {
        "ingested": True,
        "datasetName": dataset_name,
        "datasetId": dataset_id,
        "addResult": add_result,
        "cognifyResult": cognify_result,
    }


def ingest_transcript_to_cognee(transcript: str, dataset_name: str):
    return ingest_text_to_cognee(transcript, dataset_name)


def build_feedback_response(
    payload: CogneeFeedbackRequest,
    dataset_name_override: str | None = None,
    top_k_override: int | None = None,
):
    dataset_name = cognee_dataset_name(dataset_name_override or payload.dataset_name)
    query = build_feedback_query(payload)
    search_result = cognee_search(query, dataset_name, top_k=top_k_override or payload.top_k)
    contexts = compact_contexts(extract_search_context(search_result))
    dataset_id = extract_dataset_id_from_search_result(search_result) or find_dataset_id(dataset_name)
    raw_graph = (
        cognee_get_dataset_graph(dataset_id)
        if dataset_id
        else {
            "nodes": [],
            "edges": [],
            "message": "Graph unavailable because the search response did not include a dataset id.",
        }
    )
    graph = build_feedback_graph(raw_graph, query, contexts)
    graph_meta_message = raw_graph.get("message") if isinstance(raw_graph, dict) else None
    graph_is_fallback = False

    if not graph.get("nodes"):
        graph = build_feedback_fallback_graph(payload, query, contexts)
        graph_is_fallback = True
        graph_meta_message = (
            "Rendered from retrieved query and evidence because a native Cognee dataset graph was unavailable."
        )

    remembered_correctly = (
        payload.user_answer.strip().upper() == payload.correct_answer.strip().upper()
        if payload.user_answer.strip() and payload.correct_answer.strip()
        else False
    )

    return {
        "index": payload.index,
        "query": query,
        "datasetName": dataset_name,
        "datasetId": dataset_id,
        "contexts": contexts,
        "comparison": {
            "rememberedCorrectly": remembered_correctly,
            "userAnswer": payload.user_answer,
            "correctAnswer": payload.correct_answer,
        },
        "graph": graph,
        "graphMeta": {
            "datasetIdSource": "search_result" if extract_dataset_id_from_search_result(search_result) else ("dataset_lookup" if dataset_id else "unavailable"),
            "message": graph_meta_message,
            "isFallback": graph_is_fallback,
        },
    }


def build_feedback_error_response(payload: CogneeFeedbackRequest, error: Exception):
    return {
        "index": payload.index,
        "query": build_feedback_query(payload),
        "contexts": [],
        "graph": {"nodes": [], "edges": []},
        "error": str(error),
    }
