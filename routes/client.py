from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from models import User
from auth import get_password_hash, verify_password, create_access_token, get_current_user
from database import db
from utils.emailer import send_email
from utils.s3 import generate_presigned_url
from utils.encryptor import encrypt, decrypt

router = APIRouter()

@router.post("/signup", status_code=201)
async def signup(user: User):
    existing = await db.users.find_one({"email": user.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    token = encrypt(user.email)

    await db.users.insert_one({
        "email": user.email,
        "password": get_password_hash(user.password),
        "role": user.role or "client",
        "is_verified": False
    })

    verification_link = f"http://localhost:8000/client/verify/{token}"
    send_email(
        to_email=user.email,
        subject="Verify your email",
        body=f"<a href='{verification_link}'>Click here to verify your email</a>"
    )

    return {"message": "Verification email sent"}


@router.get("/verify/{token}")
async def verify_email(token: str):
    try:
        email = decrypt(token)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    result = await db.users.update_one(
        {"email": email},
        {"$set": {"is_verified": True}}
    )

    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="User not found or already verified")

    return {"message": "Email verified successfully"}


@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    email = form_data.username
    password = form_data.password

    user = await db.users.find_one({"email": email, "role": "client"})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or not registered")

    if not user.get("is_verified", False):
        raise HTTPException(status_code=403, detail="Please verify your email")

    if not verify_password(password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": email, "role": "client"})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/files")
async def list_files(current_user=Depends(get_current_user)):
    if current_user["role"] != "client":
        raise HTTPException(status_code=403, detail="Access denied")

    files = await db.files.find({}, {"_id": 0}).to_list(100)
    return {"files": files}


@router.get("/download-file/{file_id}")
async def get_download_link(file_id: str, current_user=Depends(get_current_user)):
    if current_user["role"] != "client":
        raise HTTPException(status_code=403, detail="Only client users can download files")

    file = await db.files.find_one({"file_id": file_id})
    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    url = generate_presigned_url(file["s3_key"])
    return {"download_link": url, "message": "success"}
