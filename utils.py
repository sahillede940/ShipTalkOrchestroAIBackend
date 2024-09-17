import os
import json
from datetime import datetime


# Path to the JSON file
json_file_name = "posts_data"
json_folder = "Posts"
posts_path = f"{json_folder}/{json_file_name}.json"


# Function to read data from the JSON file
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


# Function to write data to the JSON file
def write_json_file(data):
    # Convert datetime objects to strings
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
