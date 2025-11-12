from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from PIL import Image
import io

app = FastAPI(title="Upload API Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class HealthResponse(BaseModel):
    service: str
    status: str

@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    """Upload and extract metadata from image"""
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        
        # Extract basic image info
        image_info = {
            "filename": file.filename,
            "format": image.format,
            "mode": image.mode,
            "size": image.size,
            "file_size_bytes": len(contents)
        }
        
        # Extract EXIF data if available
        exif_data = {}
        try:
            exif_dict = image._getexif()
            if exif_dict:
                from PIL.ExifTags import TAGS
                for tag_id, value in exif_dict.items():
                    tag = TAGS.get(tag_id, tag_id)
                    exif_data[str(tag)] = str(value)
        except:
            exif_data = {"note": "No EXIF data available"}
        
        return JSONResponse(content={
            "message": "Image uploaded successfully",
            "image_info": image_info,
            "exif_data": exif_data
        })
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Simple health check for upload service"""
    return HealthResponse(service="api-service", status="healthy")