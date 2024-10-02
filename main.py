import json
from fastapi import FastAPI, Request, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from sql_app.models import Post, Comment
from sql_app.schemas import CommentBase, PostBase, QuestionBase
from sql_app.database import engine, get_db, Base
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from chatbot import LLM
from openai import RateLimitError

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
        "message": " Server is up and running",
        "domain": request.url.hostname,
    }


@app.get("/get_posts/")
def get_posts(
    search: str = "",
    sort_by: str = "created_at",  # Default sorting by created_at
    limit: int = 10,
    offset: int = 0,
    db=Depends(get_db),
):
    # Determine the sorting attribute
    if sort_by not in [
        "created_at",
        "upvotes",
        "title",
        "category",
    ]:
        sort_by = "created_at"

    # get db url

    query = db.query(Post)

    if search:
        query = query.filter(Post.title.ilike(f"%{search}%"))

    if sort_by == "created_at":
        query = query.order_by(Post.created_at.desc())
    elif sort_by == "likes":
        query = query.order_by(Post.upvotes.desc())
    elif sort_by == "title":
        query = query.order_by(Post.title.asc())

    # Pagination
    posts = query.limit(limit).offset(offset).all()

    total_posts = db.query(Post).count()

    return {
        "posts": posts,
        "total_posts": total_posts,
        "limit": limit,
        "offset": offset,
    }


@app.post("/upload_post/", status_code=status.HTTP_201_CREATED)
def upload_post(post: PostBase, db=Depends(get_db)):
    try:
        post_data = post.model_dump()  # Validate the input data
        db_post = Post(**post_data)

        db.add(db_post)
        db.commit()
        db.refresh(db_post)

        return db_post
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred.",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"An error occurred: {str(e)}",
        )


@app.get("/get_post/{post_id}")
def get_post(post_id: str, db=Depends(get_db)):
    try:
        post = db.query(Post).filter(Post.id == post_id).first()
        if post:
            return post
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found."
        )

    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred.",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"An error occurred: {str(e)}",
        )


@app.get("/get_comment/{comment_id}")
def get_post(comment_id: str, db=Depends(get_db)):
    try:
        comment = db.query(Comment).filter(Comment.id == comment_id).first()
        if comment:
            return comment
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found."
        )

    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred.",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"An error occurred: {str(e)}",
        )


@app.get("/like_post/{post_id}")
def like_post(post_id: str, db=Depends(get_db)):
    try:
        post = db.query(Post).filter(Post.id == post_id).first()
        if post:
            post.upvotes += 1
            db.commit()
            db.refresh(post)
            return {
                "message": "Post liked successfully",
                "upvotes": post.upvotes,
            }
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found."
        )

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred.",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"An error occurred: {str(e)}",
        )


@app.delete("/delete_post/{post_id}")
def delete_post(post_id: str, db=Depends(get_db)):
    try:
        post = db.query(Post).filter(Post.id == post_id).first()
        if post:
            db.delete(post)
            db.commit()
            return {"message": "Post deleted successfully"}
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found."
        )

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred.",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"An error occurred: {str(e)}",
        )


@app.post("/upload_comment/{post_id}")
def upload_comment(post_id: str, comment: CommentBase, db: Session = Depends(get_db)):
    try:
        comment_data = comment.model_dump()  # Validate the input data
        comment_data["post_id"] = post_id
        db_comment = Comment(**comment_data)

        db.add(db_comment)
        db.commit()
        db.refresh(db_comment)

        return db_comment
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred.",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"An error occurred: {str(e)}",
        )


@app.get("/like_comment/{post_id}/{comment_id}")
def like_comment(post_id: str, comment_id: str, db=Depends(get_db)):
    try:
        comment = (
            db.query(Comment)
            .filter(Comment.id == comment_id, Comment.post_id == post_id)
            .first()
        )
        if comment:
            comment.upvotes += 1
            db.commit()
            db.refresh(comment)
            return {
                "message": "Comment liked successfully",
            }
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found."
        )
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred.",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"An error occurred: {str(e)}",
        )


@app.delete("/delete_comment/{post_id}/{comment_id}")
def delete_comment(post_id: str, comment_id: str, db=Depends(get_db)):
    try:
        comment = (
            db.query(Comment)
            .filter(Comment.id == comment_id, Comment.post_id == post_id)
            .first()
        )
        if comment:
            db.delete(comment)
            db.commit()
            return {"message": "Comment deleted successfully"}
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found."
        )

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred.",
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"An error occurred: {str(e)}",
        )


@app.post("/AI_bot/")
def AI_bot(question: QuestionBase, request: Request, db: Session = Depends(get_db)):
    response = LLM(question.question, db)
    try:
        if response.get("related_posts", None):
            for post in response.get("related_posts", []):
                if post["id"]:
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
    except RateLimitError as e:
        raise HTTPException(status_code=429, detail=f"Rate limit exceeded: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
