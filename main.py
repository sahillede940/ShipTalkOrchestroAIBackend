import json
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sql_app.models import Post, Comment
from sql_app.schemas import CommentBase, PostBase, QuestionBase
from sql_app.database import engine, get_db, Base
from sqlalchemy.orm import Session
from chatbot import LLM


Base.metadata.create_all(bind=engine)


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/healthcheck")
def healthcheck(request: Request):
    return {
        "message": "Server is Running",
        "domain": request.url.hostname,
        "ip": request.client.host,
    }


@app.get("/get_posts/")
def get_posts(db=Depends(get_db)):
    posts = db.query(Post).order_by(Post.created_at.desc()).all()
    return posts


@app.post("/upload_post/")
def upload_post(post: PostBase, db=Depends(get_db)):
    post_data = post.model_dump()
    db_post = Post(**post_data)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post


@app.get("/get_post/{post_id}")
def get_post(post_id: str, db=Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if post:
        return post
    raise HTTPException(status_code=404, detail="Post not found")


@app.get("/like_post/{post_id}")
def like_post(post_id: str, db=Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if post:
        post.upvotes += 1
        db.commit()
        db.refresh(post)
        return post
    raise HTTPException(status_code=404, detail="Post not found")


@app.get("/delete_post/{post_id}")
def delete_post(post_id: str, db=Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if post:
        db.delete(post)
        db.commit()
        return {"message": "Post deleted successfully"}
    raise HTTPException(status_code=404, detail="Post not found")


@app.post("/upload_comment/{post_id}")
def upload_comment(post_id: str, comment: CommentBase, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    comment_data = comment.dict()
    db_comment = Comment(**comment_data)
    post.comments.append(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment


@app.get("/like_comment/{post_id}/{comment_id}")
def like_comment(post_id: str, comment_id: str, db=Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    comment.upvotes += 1
    db.commit()
    db.refresh(comment)
    return comment


@app.get("/delete_comment/{post_id}/{comment_id}")
def delete_comment(post_id: str, comment_id: str, db=Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    db.delete(comment)
    db.commit()
    return {"message": "Comment deleted successfully"}


@app.post("/AI_bot/")
def AI_bot(question: QuestionBase, request: Request, db: Session = Depends(get_db)):
    response = LLM(question.question, db)
    try:
        if response.get("related_posts", None):
            for post in response.get("related_posts", []):
                PORT = request.url.port
                if PORT:
                    post["url"] = (
                        f"{request.url.scheme}://{request.url.hostname}:{PORT}/get_post/{post['id']}"
                    )
                else:
                    post["url"] = (
                        f"{request.url.scheme}://{request.url.hostname}/get_post/{post['id']}"
                    )
        return response
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=500, detail=f"Invalid JSON response from LLM: {str(e)}"
        )
