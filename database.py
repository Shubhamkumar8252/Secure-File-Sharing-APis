from motor.motor_asyncio import AsyncIOMotorClient
from os import getenv
from dotenv import load_dotenv

load_dotenv()

db = None

def init_db():
    global db
    mongo_uri = getenv("MONGO_URI")
    if not mongo_uri:
        raise Exception("MONGO_URI is not set in the environment variables.")
    
    client = AsyncIOMotorClient(mongo_uri)
    db_instance = client["secure_files"]
    db = db_instance
    globals()["db"] = db_instance  # make it accessible from other modules
