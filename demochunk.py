from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from typing import List, Optional
from docx import Document
from pydantic import BaseModel
import uvicorn
import os
from uuid import uuid4
import requests

app = FastAPI()

UPLOAD_FOLDER = "uploads"

host = "127.0.0.1"
port = 8000
uri = f"http://{host}:{str(port)}"

print("I will be opening at " + uri)


class ChunkBody(BaseModel):
    sections: List[str]
    chunk_size: Optional[int] = 700


def parse_document(file_path: str) -> List[str]:
    """
    Parse the uploaded Word document and return a list of sections.
    """
    sections = []
    doc = Document(file_path)
    for paragraph in doc.paragraphs:
        sections.append(paragraph.text)
    return sections


def chunk_document(paragraphs: List[str], chunk_size: int = 700) -> List[str]:
    sections = []
    for temp in paragraphs:
        if len(temp) > chunk_size:
            for i in range(0, len(temp), chunk_size):
                if len(temp) >= i + chunk_size:
                    sections.append(temp[i : i + chunk_size])
                else:
                    sections.append(temp[i:-1])
        else:
            sections.append(temp)
    return sections


# "C:\Users\004IMU744\Documents\ 28110920192dsdw0192.docx"


@app.post("/upload/")
async def upload_word_file(file: UploadFile = File(...)):
    """
    Uploads a Word document.
    """
    if (
        file.content_type!= "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ):
        raise HTTPException(status_code=400, detail="Only Word documents are allowed.")

    filename = str(uuid4())
    file_path = os.path.join(UPLOAD_FOLDER, f"{filename}.docx")

    with open(file_path, "wb") as f:
        f.write(await file.read())

    sections = parse_document(file_path)
    sections = chunk_document(sections , 700)
    # single service route
    # return {"fileName":filename}

    return {"sections":sections}


if __name__ == "__main__":
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    uvicorn.run(app, host=host, port=port)
