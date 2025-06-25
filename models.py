from pydantic import BaseModel, EmailStr
from typing import Optional

class User(BaseModel):
    email: EmailStr
    password: str
    role: Optional[str] = "client"

class FileMetadata(BaseModel):
    file_id: str
    uploader: str
    s3_key: str
    file_type: str
