from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
from typing import List
import json
import uuid
from utils import read_json_file, write_json_file
from chatbot import LLM
import re
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

# OPEN TO ALL ORIGINS

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Comment(BaseModel):
    id: str = str(uuid.uuid4())
    content: str
    upvotes: int = 0
    author: str = "Anonymous"
    created_at: datetime = datetime.now()

    class Config:
        validate_assignment = True
        json_encoders = {datetime: lambda v: v.isoformat()}


class Post(BaseModel):
    id: str = str(uuid.uuid4())
    title: str
    content: str
    upvotes: int = 0
    comments: List[Comment] = []
    author: str = "Anonymous"
    created_at: datetime = datetime.now()

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class Question(BaseModel):
    question: str


@app.get("/healthcheck")
def healthcheck():
    return {"message": "Server is Running"}


@app.get("/get_post/{post_id}")
def get_post(post_id: str):
    posts_data = read_json_file()
    for post in posts_data:
        if post["id"] == post_id:
            return post
    raise HTTPException(status_code=404, detail="Post not found")

@app.delete("/delete_post/{post_id}")
def delete_post(post_id: str):
    posts_data = read_json_file()
    for post in posts_data:
        if post["id"] == post_id:
            posts_data.remove(post)
            write_json_file(posts_data)
            return {"message": "Post deleted successfully"}
    raise HTTPException(status_code=404, detail="Post not found")


@app.post("/upload_post/")
def upload_post(post: Post):
    posts_data = read_json_file()
    post_data = post.model_dump()
    post_id = str(uuid.uuid4())
    post_data["id"] = post_id
    posts_data.append(post_data)
    write_json_file(posts_data)
    return post_data


@app.post("/upload_comment/{post_id}")
def upload_comment(post_id: str, comment: Comment):
    print(post_id)
    posts_data = read_json_file()
    for post in posts_data:
        if post["id"] == post_id:
            post["comments"].append(comment.model_dump())
            write_json_file(posts_data)
            return comment.model_dump()
    raise HTTPException(status_code=404, detail="Post not found")


@app.get("/like_post/{post_id}")
def like_post(post_id: str):
    posts_data = read_json_file()
    for post in posts_data:
        if post["id"] == post_id:
            post["upvotes"] += 1
            write_json_file(posts_data)
            return post
    raise HTTPException(status_code=404, detail="Post not found")


@app.get("/like_comment/{post_id}/{comment_id}")
def like_comment(post_id: str, comment_id: str):
    posts_data = read_json_file()
    for post in posts_data:
        if post["id"] == post_id:
            for comment in post["comments"]:
                if comment["id"] == comment_id:
                    comment["upvotes"] += 1
                    write_json_file(posts_data)
                    return comment
    raise HTTPException(status_code=404, detail="Comment not found")


@app.get("/get_posts/")
def get_posts():
    posts_data = read_json_file()
    return posts_data


def sanitize_json_string(json_string: str) -> str:
    # Remove invalid control characters
    json_string = re.sub(r"[\x00-\x1f\x7f]", "", json_string)
    return json_string


@app.post("/AI_bot/")
def AI_bot(question: Question):
    response = LLM(question.question)
    sanitized_response = sanitize_json_string(response)
    try:
        parsed_response = json.loads(sanitized_response)
        return parsed_response
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=500, detail=f"Invalid JSON response from LLM: {str(e)}"
        )
