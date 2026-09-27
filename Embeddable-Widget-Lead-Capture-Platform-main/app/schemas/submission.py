from pydantic import BaseModel, Field
class SubmissionRequest(BaseModel):
    widget_id: str = Field(min_length=10, max_length=50)
    data: dict[str, str] = Field(default_factory=dict)
    honeypot: str = Field(default="", max_length=200)
class SubmissionResponse(BaseModel):
    id: str
    status: str
    message: str
    duplicate: bool = False
