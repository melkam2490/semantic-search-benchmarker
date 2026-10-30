from pydantic import BaseModel
from typing import Optional
import tiktoken
import re


# Stores one small piece of a document
class DocumentChunk(BaseModel):
    chunk_id: str
    content: str
    metadata: dict
    parent_doc: str


# Counts tokens in text
def count_tokens(text):
    encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))


# Divides documents into fixed-size pieces
class FixedSizeChunker:

    def __init__(self, chunk_size=256, overlap=40):
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.encoding = tiktoken.get_encoding("cl100k_base")

    def split(self, text, parent_doc="document"):
        tokens = self.encoding.encode(text)
        chunks = []

        start = 0
        number = 1

        while start < len(tokens):
            end = start + self.chunk_size
            chunk_tokens = tokens[start:end]
            content = self.encoding.decode(chunk_tokens)

            chunks.append(
                DocumentChunk(
                    chunk_id=f"{parent_doc}-fixed-{number}",
                    content=content,
                    metadata={
                        "start_token": start,
                        "end_token": min(end, len(tokens))
                    },
                    parent_doc=parent_doc
                )
            )

            number += 1
            if end >= len(tokens):
                break

            start = end - self.overlap

        return chunks


# Divides Markdown documents using their headings
class StructureAwareChunker:

    def split(self, text, parent_doc="document"):
        lines = text.splitlines()
        sections = []
        current_lines = []
        current_heading = "Introduction"
        heading_path = []

        for line in lines:
            if line.startswith("#"):
                if current_lines:
                    sections.append(
                        (current_heading, "\n".join(current_lines))
                    )

                level = len(line) - len(line.lstrip("#"))
                heading = line.lstrip("#").strip()

                heading_path = heading_path[:level - 1]
                heading_path.append(heading)

                current_heading = " > ".join(heading_path)
                current_lines = [line]
            else:
                current_lines.append(line)

        if current_lines:
            sections.append(
                (current_heading, "\n".join(current_lines))
            )

        chunks = []

        for number, (heading, content) in enumerate(sections, start=1):
            chunks.append(
                DocumentChunk(
                    chunk_id=f"{parent_doc}-structure-{number}",
                    content=content,
                    metadata={
                        "heading": heading,
                        "has_code": "```" in content
                    },
                    parent_doc=parent_doc
                )
            )

        return chunks
