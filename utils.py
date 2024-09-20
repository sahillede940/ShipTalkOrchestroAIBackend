import os
import json
from datetime import datetime
from alembic.config import Config
from alembic import context
from sql_app.database import Base, engine


target_metadata = Base.metadata


def run_migrations_online():
    connectable = engine
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


json_file_name = "posts_data"
json_folder = "Posts"
posts_path = f"{json_folder}/{json_file_name}.json"


def read_json_file():
    if os.path.exists(posts_path):
        with open(posts_path, "r") as file:
            data = json.load(file)
            for post in data:
                post["created_at"] = datetime.fromisoformat(post["created_at"])
                for comment in post["comments"]:
                    comment["created_at"] = datetime.fromisoformat(
                        comment["created_at"]
                    )
            return data

    with open(posts_path, "w") as file:
        json.dump([], file)
    return []


def write_json_file(data):
    for post in data:
        post["created_at"] = post["created_at"].isoformat()
        for comment in post["comments"]:
            comment["created_at"] = comment["created_at"].isoformat()

    try:
        temp_json = json_folder + "/" + json_file_name + "_temp.json"
        with open(temp_json, "w") as file:
            json.dump(data, file, indent=4)
        os.remove(posts_path)
        os.rename(temp_json, posts_path)
    except Exception as e:
        print(e)
        return False
