from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from auth import verify_password, create_access_token
from database import db
from utils.s3 import upload_to_s3
import uuid

router = APIRouter()

@router.post("/login")
async def ops_login(email: str = Form(...), password: str = Form(...)):
    user = await db.users.find_one({"email": email, "role": "ops"})
    if not user or not verify_password(password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token({"sub": email, "role": "ops"})
    return {"access_token": token, "token_type": "bearer"}

@router.post("/upload")
async def upload_file(file: UploadFile = File(...), user_id: str = Form("ops_user")):
    if "." not in file.filename:
        raise HTTPException(status_code=400, detail="File must have an extension")
    
    ext = file.filename.rsplit(".", 1)[-1].lower()
    if ext not in {"pptx", "docx", "xlsx"}:
        raise HTTPException(status_code=400, detail="Only pptx, docx, xlsx files are allowed")

    key = await upload_to_s3(file, ext, user_id)
    file_id = str(uuid.uuid4())

    await db.files.insert_one({
        "file_id": file_id,
        "s3_key": key,
        "uploaded_by": user_id,
        "file_type": ext
    })

    return {
        "message": "File uploaded successfully",
        "file_id": file_id,
        "s3_key": key
    }
