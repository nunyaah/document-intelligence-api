import uuid

from pydantic import BaseModel, Field, field_validator


class ConversationTurn(BaseModel):
    role: str = Field(..., description="'user' or 'assistant'")
    content: str = Field(..., max_length=4000)


class AskRequest(BaseModel):
    document_id: str = Field(..., description="UUID of the uploaded document")
    question: str = Field(..., min_length=1, max_length=1000, description="Natural language question")
    top_k: int = Field(default=5, ge=1, le=20, description="Number of chunks to retrieve")
    conversation_history: list[ConversationTurn] = Field(
        default_factory=list,
        max_length=10,
        description="Recent conversation turns for query contextualization",
    )

    @field_validator("document_id")
    @classmethod
    def validate_uuid(cls, v: str) -> str:
        try:
            uuid.UUID(v, version=4)
        except ValueError:
            raise ValueError("document_id must be a valid UUID4")
        return v

    @field_validator("question")
    @classmethod
    def strip_question(cls, v: str) -> str:
        return v.strip()


class EvalItem(BaseModel):
    question: str = Field(..., min_length=1)
    ground_truth: str = Field(..., min_length=1)


class EvalRequest(BaseModel):
    document_id: str = Field(..., description="UUID of the document to evaluate against")
    eval_dataset: list[EvalItem] = Field(..., min_length=1)

    @field_validator("document_id")
    @classmethod
    def validate_uuid(cls, v: str) -> str:
        try:
            uuid.UUID(v, version=4)
        except ValueError:
            raise ValueError("document_id must be a valid UUID4")
        return v
