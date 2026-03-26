from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from .schemas import DocumentType, FileType, OCRResponse
from typhoon_ocr import ocr_document

import tempfile
from pathlib import Path

import shutil
import os

app = FastAPI(
    title="Typhoon OCR API",
    description="Extract from PDF/image file",
    version="0.1.0",
)

ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/tiff",
}


@app.post("/ocr", response_model=OCRResponse, summary="Text extract OCR")
async def extract_text(
    file: UploadFile = File(..., description="PDF or image file"),
    file_id: str = Form(..., description="file ID"),
    file_type: FileType = Form(..., description="file type: pdf | image"),
    document_type: DocumentType = Form(..., description="document type: certificate | payslip | ..."),
):
    # 1) Content-Type validation
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=415,
            detail=f"It's not supported file type: {file.content_type}. "
                   f"allowed: {', '.join(ALLOWED_CONTENT_TYPES)}",
        )

    # 2) Read file
    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Empty file is not able to process")

    # 3) Store file to temp location
    await file.seek(0)
    suffix = Path(file.filename).suffix  # e.g. ".pdf", ".png"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        
        tmp.flush()
        os.fsync(tmp.fileno())
        tmp_path = tmp.name
        # tmp.write(contents)
        # tmp_path = Path(tmp.name)
        file_size = os.path.getsize(tmp_path)
        print(f"Temporary file created: {tmp_path}, Size: {file_size} bytes")
    try:
        # default result format is MD
        extracted_text = ocr_document(tmp_path, base_url="http://localhost:11434/v1", api_key="ollama", model='scb10x/typhoon-ocr1.5-3b')
    finally:
        # tmp_path.unlink(missing_ok=True)  # delete temp file
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    # 3) TODO: Typhoon OCR 호출 (다음 단계에서 구현)
    # extracted_text = f"[OCR 미구현] file_id={file_id}, size={len(contents)} bytes"
    
    return OCRResponse(
        file_id=file_id,
        file_type=file_type,
        document_type=document_type,
        filename=file.filename or "unknown",
        extracted_text=extracted_text,
    )


@app.get("/health", summary="Health Check")
async def health():
    return {"status": "ok"}