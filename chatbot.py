from dotenv import load_dotenv
from utils import read_json_file, write_json_file
import json

load_dotenv()

from langchain_openai import ChatOpenAI


system_prompt = """
You are an AI model specialized in answering questions related to posts on a discussion forum. You have been provided with a list of posts and their content in JSON format. Your task is to analyze the posts and provide answers to user queries, along with the IDs of the posts where related discussions occur and URLs to access those posts. The URLs should be in the format {url: 'http://127.0.0.1:8000/get_post/' + ID, title: title} concatenated with the post ID. Return the information in JSON format.

Please follow these guidelines:

1. If the provided text contains conflicting information (e.g., different ages), use the first occurrence.
2. Extract relevant information from the provided text and map it to the corresponding keys in the JSON structure.
3. If a particular key's value is not found in the given text, leave the value as an empty string.
4. Do not include any additional information or formatting beyond the requested JSON object.
5. Strictly return the JSON object without any \n or \t characters or markdown formatting.

Example JSON structure:
{
    "answer": "Your answer here",
    "urls": [],
    "ids": []
}
Post data:
"""


def LLM(question: str):
    posts = read_json_file()
    data = {"posts": []}
    for post in posts:
        data["posts"].append(
            {
                "id": post["id"],
                "title": post["title"],
                "content": post["content"],
            }
        )

    messages = [
        {"role": "system", "content": system_prompt + json.dumps(data)},
        {"role": "user", "content": f"Question: {question}"},
    ]

    llm = ChatOpenAI(model="gpt-4o")
    response = llm.invoke(messages)
    return response.content
