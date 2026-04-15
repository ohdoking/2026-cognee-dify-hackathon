from pydantic import BaseModel, Field


class V2SessionPrepareRequest(BaseModel):
    transcript: str
    dataset_name: str | None = None
    top_k: int = 5


class V2QuizItem(BaseModel):
    index: int | None = None
    category: str = ""
    question: str
    options: dict[str, str] = Field(default_factory=dict)
    correct_answer: str = ""
    insight: str = ""


class V2FeedbackRequest(BaseModel):
    transcript: str = ""
    dataset_name: str | None = None
    quizzes: list[V2QuizItem]
    user_answers: dict[int, str] = Field(default_factory=dict)
    top_k: int = 5
