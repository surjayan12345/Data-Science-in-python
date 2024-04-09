from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from typing import List
from docx import Document
import os
import uvicorn

app = FastAPI()

UPLOAD_FOLDER = "uploads"


def parse_document(file_path: str) -> List[str]:
    """
    Parse the uploaded Word document and return a list of sections.
    """
    sections = []
    doc = Document(file_path)
    current_chunk = ""
    current_chunk_word_count = 0
    chunk_size = 700

    for paragraph in doc.paragraphs:
        current_chunk += paragraph.text + "\n"
        current_chunk_word_count += len(paragraph.text.split())

        if current_chunk_word_count >= chunk_size:
            sections.append(current_chunk.strip())
            current_chunk = ""
            current_chunk_word_count = 0

    if current_chunk:  # Add remaining text as a section
        sections.append(current_chunk.strip())

    return sections


@app.post("/upload/")
async def upload_word_file(file: UploadFile = File(...)):
    """
    Uploads a Word document.
    """
    if file.content_type != "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        raise HTTPException(status_code=400, detail="Only Word documents are allowed.")

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())

    sections = parse_document(file_path)
    return {"sections": sections}


@app.post("/parse/")
async def parse_uploaded_document(file_name: str):
    """
    Parses the uploaded Word document and returns sections.
    """
    file_path = os.path.join(UPLOAD_FOLDER, file_name)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found.")

    sections = parse_document(file_path)
    return {"sections": sections}


@app.post("/chunk/")
async def chunk_sections(sections: List[str], chunk_size: int = 700):
    """
    Chunks the given sections based on the provided chunk size.
    """
    chunked_sections = []
    current_chunk = ""
    current_chunk_word_count = 0

    for section in sections:
        words = section.split()
        for word in words:
            current_chunk += word + " "
            current_chunk_word_count += 1
            if current_chunk_word_count >= chunk_size:
                chunked_sections.append(current_chunk.strip())
                current_chunk = ""
                current_chunk_word_count = 0

        if current_chunk:
            chunked_sections.append(current_chunk.strip())
            current_chunk = ""
            current_chunk_word_count = 0

    return {"chunked_sections": chunked_sections}


if __name__ == "__main__":
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    uvicorn.run(app, host="0.0.0.0", port=8000)