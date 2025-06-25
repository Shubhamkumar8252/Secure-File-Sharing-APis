from fastapi import FastAPI
from routes.client import router as client_router
from routes.ops import router as ops_router
from database import init_db

app = FastAPI(title="Secure File Sharing API")

init_db()

@app.get("/")
def root():
    return {"message": "Secure File Sharing API is running"}

app.include_router(client_router, prefix="/client", tags=["Client"])
app.include_router(ops_router, prefix="/ops", tags=["Ops"])
