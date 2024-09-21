import requests

import json
# logger 
import logging

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

no_of_posts = 4
no_of_comments = 4

def add_sample_posts():
    HOST = "https://shiptalkorchestroaibackend-1.onrender.com"
    # HOST = "http://127.0.0.1:8000"
    endpoint = "/upload_post/"

    with open("./Posts/posts_data.json") as f:
        posts = json.load(f)
    i = 0
    for post in posts[no_of_posts:]:
        i += 1
        logger.info(f"Uploading post {i}")
        data = {
            "title": post["title"],
            "content": post["content"],
            "category": post["category"],
        }
        response = requests.post(HOST + endpoint, json=data)
        j = 0  
        for comment in post.get("comments", []):
            j += 1
            logger.info(f"Uploading comment for post {i}")
            comment_endpoint = f"/upload_comment/{response.json()['id']}"
            comment_data = {
                "content": comment["content"],
                "author": comment["author"],
            }
            try:
                requests.post(HOST + comment_endpoint, json=comment_data)
            except Exception as e:
                logger.error(f"Error uploading comment {j} for post {i}: {e}")

            if j == no_of_comments if no_of_comments else len(post.get("comments", [])):
                break
        
        if i == no_of_posts if no_of_posts else len(posts):
            break

if __name__ == "__main__":
    add_sample_posts()