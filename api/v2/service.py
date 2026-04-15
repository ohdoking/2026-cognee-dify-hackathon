from api.schemas import CogneeFeedbackBatchRequest, CogneeFeedbackRequest
from api.services.cognee import (
    build_feedback_error_response,
    build_feedback_response,
    cognee_dataset_name,
    compact_contexts,
    extract_search_context,
    ingest_transcript_to_cognee,
    is_cognee_configured,
    cognee_search,
)
from api.v2.schemas import V2FeedbackRequest, V2QuizItem, V2SessionPrepareRequest


def build_v2_analysis_query(transcript: str) -> str:
    return (
        "Analyze this meeting transcript for rules, constraints, approvals, silent risks, "
        "and facts that must be remembered later. Transcript: "
        f"{transcript.strip()}"
    )


def build_gemma_quiz_prompt(transcript: str, contexts: list[str]) -> str:
    context_block = "\n".join(f"- {item}" for item in contexts) if contexts else "- No extra Cognee context returned."
    return f"""
You are Gemma 4 running locally on an iPhone. Create exactly 3 multiple-choice quiz questions from the transcript and Cognee context.

Requirements:
- Focus on rules, approvals, memory drift, and misinformation risk.
- Each question must have exactly 2 options: A and B.
- Return valid JSON only.
- JSON shape:
{{
  "quizzes": [
    {{
      "category": "short label",
      "question": "question text",
      "options": {{"A": "option A", "B": "option B"}},
      "correct_answer": "A or B",
      "insight": "why this matters and what to remember"
    }}
  ]
}}

Transcript:
{transcript.strip()}

Cognee context:
{context_block}
""".strip()


def prepare_v2_session(payload: V2SessionPrepareRequest):
    dataset_name = cognee_dataset_name(payload.dataset_name)
    ingest_result = None
    if is_cognee_configured():
        ingest_result = ingest_transcript_to_cognee(payload.transcript, dataset_name)

    search_result = cognee_search(build_v2_analysis_query(payload.transcript), dataset_name, top_k=payload.top_k)
    contexts = compact_contexts(extract_search_context(search_result), limit=payload.top_k)

    return {
        "transcript": payload.transcript,
        "datasetName": dataset_name,
        "cognee": ingest_result,
        "contexts": contexts,
        "analysisQuery": build_v2_analysis_query(payload.transcript),
        "gemmaPrompt": build_gemma_quiz_prompt(payload.transcript, contexts),
    }


def quiz_item_to_feedback_request(quiz: V2QuizItem, user_answer: str, dataset_name: str | None, top_k: int):
    return CogneeFeedbackRequest(
        index=quiz.index,
        question=quiz.question,
        user_answer=user_answer,
        correct_answer=quiz.correct_answer,
        category=quiz.category,
        insight=quiz.insight,
        dataset_name=dataset_name,
        top_k=top_k,
    )


def build_v2_feedback(payload: V2FeedbackRequest):
    dataset_name = cognee_dataset_name(payload.dataset_name)
    items = []

    for index, quiz in enumerate(payload.quizzes):
        answer = payload.user_answers.get(index, "")
        quiz_with_index = quiz.model_copy(update={"index": quiz.index if quiz.index is not None else index})
        try:
            items.append(
                build_feedback_response(
                    quiz_item_to_feedback_request(quiz_with_index, answer, dataset_name, payload.top_k),
                    dataset_name_override=dataset_name,
                    top_k_override=payload.top_k,
                )
            )
        except Exception as exc:
            items.append(build_feedback_error_response(
                quiz_item_to_feedback_request(quiz_with_index, answer, dataset_name, payload.top_k),
                exc,
            ))

    remember = []
    for item in items:
        if item.get("comparison", {}).get("rememberedCorrectly"):
            continue
        contexts = item.get("contexts") or []
        if contexts:
            remember.append(contexts[0])
        elif item.get("query"):
            remember.append(item["query"])

    return {
        "datasetName": dataset_name,
        "items": items,
        "rememberHighlights": remember[:3],
    }
