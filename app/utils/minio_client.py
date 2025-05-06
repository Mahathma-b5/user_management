from minio import Minio
from settings.config import settings
from minio.error import S3Error

def get_minio_client():
    return Minio(
        settings.MINIO_ENDPOINT,
        access_key=settings.MINIO_ACCESS_KEY,
        secret_key=settings.MINIO_SECRET_KEY,
        secure=settings.MINIO_USE_SSL
    )

def ensure_bucket_exists(bucket_name=None):
    """
    Ensures the given bucket exists in MinIO.
    """
    bucket = bucket_name or settings.MINIO_BUCKET_NAME
    client = get_minio_client()
    try:
        if not client.bucket_exists(bucket):
            client.make_bucket(bucket)
        else:
            print(f"Bucket '{bucket}' already exists")
    except S3Error as e:
        print(f"Error ensuring bucket exists: {e}")

def upload_profile_picture(file_data, file_name):
    """
    Uploads a profile picture to MinIO.

    Args:
        file_data (bytes): File content to upload.
        file_name (str): Name of the file.

    Returns:
        str: URL to the uploaded file.
    """
    allowed_extensions = {"jpg", "jpeg", "png", "gif"}
    file_extension = file_name.split(".")[-1].lower()
    if file_extension not in allowed_extensions:
        raise ValueError("Unsupported file type")

    client = get_minio_client()
    ensure_bucket_exists()  # Lazy creation of bucket if needed

    client.put_object(
        settings.MINIO_BUCKET_NAME,
        file_name,
        file_data,
        length=-1,
        part_size=10 * 1024 * 1024
    )

    return f"{settings.MINIO_ENDPOINT}/{settings.MINIO_BUCKET_NAME}/{file_name}"

def get_profile_picture_url(file_name):
    """
    Generates a presigned URL for a profile picture.

    Args:
        file_name (str): Name of the file.

    Returns:
        str: Presigned URL for the file.
    """
    client = get_minio_client()
    ensure_bucket_exists()  # Optional safeguard

    return client.get_presigned_url(
        "GET",
        settings.MINIO_BUCKET_NAME,
        file_name
    )
