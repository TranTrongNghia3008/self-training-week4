import cloudinary
import cloudinary.uploader
import os
from dotenv import load_dotenv

load_dotenv()

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

def upload_media_to_cloudinary(file, folder="media"):
    result = cloudinary.uploader.upload(file, folder=folder, resource_type="auto")
    return {
        "url": result["secure_url"],
        "public_id": result["public_id"],
        "media_type": result["resource_type"]
    }

def delete_media_from_cloudinary(public_id, media_type):
    return cloudinary.uploader.destroy(public_id, resource_type=media_type)
