import boto3
from os import getenv
from uuid import uuid4
from botocore.exceptions import BotoCoreError, ClientError

AWS_ACCESS_KEY_ID = getenv("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = getenv("AWS_SECRET_ACCESS_KEY", "")
AWS_REGION = getenv("AWS_REGION", "ap-south-1")
BUCKET = getenv("AWS_BUCKET_NAME", "")

s3 = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

async def upload_to_s3(file, ext, user_id):
    try:
        key = f"{user_id}/{uuid4()}.{ext}"
        content = await file.read()
        s3.upload_fileobj(
            Fileobj=bytearray_to_stream(content),
            Bucket=BUCKET,
            Key=key
        )
        return key
    except (BotoCoreError, ClientError) as e:
        raise Exception(f"Upload to S3 failed: {str(e)}")

def generate_presigned_url(key: str):
    try:
        return s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": BUCKET, "Key": key},
            ExpiresIn=3600
        )
    except Exception as e:
        raise Exception(f"Could not generate download link: {str(e)}")

def bytearray_to_stream(data: bytes):
    from io import BytesIO
    return BytesIO(data)
