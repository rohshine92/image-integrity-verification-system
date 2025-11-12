from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from PIL import Image
import io
from typing import Dict, Any, List
from forensics_engine import AdvancedForensicsEngine

app = FastAPI(title="Advanced Image Analysis Service")

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

class EnhancedAnalysisResult(BaseModel):
    filename: str
    is_potentially_edited: bool
    confidence_score: float
    risk_level: str
    analysis_details: Dict[str, Any]
    detection_methods: List[str]
    recommendations: List[str]

# Initialize forensics engine
forensics_engine = AdvancedForensicsEngine()

@app.post("/analyze", response_model=EnhancedAnalysisResult)
async def enhanced_analyze_image(file: UploadFile = File(...)):
    """Analyze image using advanced multi-algorithm techniques"""
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")
        
        # Extract EXIF data
        exif_data = {}
        try:
            exif_dict = image._getexif()
            if exif_dict:
                from PIL.ExifTags import TAGS
                for tag_id, value in exif_dict.items():
                    tag = TAGS.get(tag_id, tag_id)
                    exif_data[str(tag)] = str(value)
        except:
            exif_data = {}
        
        # Perform forensic analysis
        analysis_result = await forensics_engine.analyze_image(image, exif_data)
        
        # Generate recommendations
        recommendations = generate_recommendations(analysis_result)
        
        return EnhancedAnalysisResult(
            filename=file.filename,
            is_potentially_edited=analysis_result['is_potentially_edited'],
            confidence_score=analysis_result['final_score'],
            risk_level=analysis_result['risk_level'],
            analysis_details=analysis_result['individual_scores'],
            detection_methods=list(forensics_engine.algorithms.keys()),
            recommendations=recommendations
        )
        
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)

def generate_recommendations(analysis_result: Dict[str, Any]) -> List[str]:
    """Generate recommendations based on analysis results"""
    recommendations = []
    scores = analysis_result['individual_scores']
    
    if scores.get('enhanced_ela', 0) > 0.5:
        recommendations.append("High ELA score detected - check for JPEG recompression artifacts")
    
    if scores.get('metadata_consistency', 0) > 0.3:
        recommendations.append("Metadata inconsistencies found - verify image source and editing history")
    
    if scores.get('noise_pattern', 0) > 0.4:
        recommendations.append("Irregular noise patterns detected - possible splicing or copy-move manipulation")
    
    if scores.get('jpeg_quality', 0) > 0.4:
        recommendations.append("JPEG quality inconsistencies suggest multiple compression cycles")
    
    if analysis_result['risk_level'] == 'high':
        recommendations.append("HIGH RISK: Multiple manipulation indicators detected - thorough manual review recommended")
    elif analysis_result['risk_level'] == 'medium':
        recommendations.append("MEDIUM RISK: Some suspicious indicators - additional verification suggested")
    else:
        recommendations.append("LOW RISK: Image appears to be authentic with minimal editing traces")
    
    return recommendations

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Advanced verification service health check"""
    return HealthResponse(service="verification-service", status="healthy")

@app.get("/algorithms")
async def list_algorithms():
    """List available forensic algorithms"""
    return {
        "available_algorithms": list(forensics_engine.algorithms.keys()),
        "description": {
            "enhanced_ela": "Multi-quality Error Level Analysis for JPEG compression artifacts",
            "metadata_consistency": "EXIF metadata consistency and editing software detection",
            "noise_pattern": "Sensor noise pattern analysis for splicing detection",
            "jpeg_quality": "JPEG compression quality consistency analysis"
        }
    }