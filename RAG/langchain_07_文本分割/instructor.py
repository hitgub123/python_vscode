import instructor, os
from pydantic import BaseModel
from typing import List


class User(BaseModel):
    name: str
    age: int


class Poem(BaseModel):
    title: str
    author: str
    content: str

def get_client():
    client = instructor.from_provider(
        "google/gemini-2.5-flash",
        api_key=os.environ.get("gemini_api_key2"),
        mode=instructor.Mode.JSON,
    )
    return client




def get_user():
    text = "John is 25 years old"
    client = get_client()
    result = client.chat.completions.create(
        response_model=User,
        messages=[{"role": "user", "content": text}],
    )
    print(result)


def get_users():
    text = "John is 25 years old,Ann is 2 years old,Lily is 5 years old"
    client = get_client()    
    result = client.chat.completions.create(
        response_model=List[User],
        messages=[{"role": "user", "content": text}],
    )
    # [User(name='John', age=25), User(name='Ann', age=2), User(name='Liyi', age=5)]
    print(result)

def get_poems():
    client = get_client()
    with open("doc/唐诗三百首.txt", "r", encoding="utf-8") as f:
        text = f.read()
        # print(text[:1000])
        result = client.chat.completions.create(
            response_model=List[Poem],
            messages=[{"role": "user", "content": text}],
        )
        # [User(name='John', age=25), User(name='Ann', age=2), User(name='Liyi', age=5)]
        print(result)

if __name__ == "__main__":
    get_poems()