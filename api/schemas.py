from pydantic import BaseModel


class AuditRequest(BaseModel):
    transcript: str
    dataset_name: str | None = None


class CogneeIngestRequest(BaseModel):
    transcript: str
    dataset_name: str | None = None


class CogneeFeedbackRequest(BaseModel):
    index: int | None = None
    question: str
    user_answer: str = ""
    correct_answer: str = ""
    category: str = ""
    insight: str = ""
    dataset_name: str | None = None
    top_k: int = 5


class CogneeFeedbackBatchRequest(BaseModel):
    items: list[CogneeFeedbackRequest]
    dataset_name: str | None = None
    top_k: int = 5
