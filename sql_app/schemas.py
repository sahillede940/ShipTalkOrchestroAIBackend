from pydantic import BaseModel
from datetime import datetime
from typing import List

class CommentBase(BaseModel):
    content: str
    author: str = "Anonymous"

    class Config:
        validate_assignment = True
        json_encoders = {datetime: lambda v: v.isoformat()}


class PostBase(BaseModel):
    title: str
    content: str
    author: str = "Anonymous"
    category: str = "Carrier Comparison"
    comments: List[CommentBase] = []

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class QuestionBase(BaseModel):
    question: str
