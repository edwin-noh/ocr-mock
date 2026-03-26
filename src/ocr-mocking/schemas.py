from enum import Enum
from pydantic import BaseModel


class FileType(str, Enum):
    pdf = "pdf"
    image = "image"


class DocumentType(str, Enum):
    invoice = "certificate"
    receipt = "payslip"
    contract = "contract"
    id_card = "id_card"
    passport = "passport"
    other = "other"


class OCRResponse(BaseModel):
    file_id: str
    file_type: FileType
    document_type: DocumentType
    filename: str
    extracted_text: str