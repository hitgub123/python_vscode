import instructor
import os
from pydantic import BaseModel
from typing import List
from docling.document_converter import DocumentConverter
from docling_core.types.doc import DocItem


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


def get_poems():
    converter = DocumentConverter()

    file_path = "doc/唐诗三百首.pdf"

    try:
        result = converter.convert(file_path)
        document_text = ""
        for item in result.document.iterate_items():
            if isinstance(item, tuple):
                item = item[0]
            if isinstance(item, DocItem) and hasattr(item, 'text') and item.text:
                document_text += item.text + "\n"

        client = get_client()
        result = client.chat.completions.create(
            response_model=List[Poem],
            messages=[{"role": "user", "content": document_text}],
        )

        print(result)

        return result

    except Exception as e:
        print(f"Error processing document with Docling: {e}")
        return None


if __name__ == "__main__":
    get_poems()
