# Image Integrity Verification System

## Project Title and Description
The Image Integrity Verification System is a microservices-based application designed to verify the integrity of images through various analysis techniques. The system detects potential image tampering and manipulation using Error Level Analysis and metadata examination.

## System Architecture Document

### System Purpose
This system addresses the growing need for digital image forensics in an era where image manipulation has become increasingly sophisticated. The system serves multiple purposes:
- **Advanced Image Forensics**: Uses 4 sophisticated algorithms for comprehensive tampering detection
- **Multi-Algorithm Analysis**: Combines ELA, noise patterns, JPEG quality, and metadata consistency
- **Scalable Analysis Pipeline**: Provides a distributed architecture for processing multiple images

### Service Boundaries
The system is designed with clear separation of concerns:

**API Service**: Responsible solely for image ingestion and metadata extraction. This service handles file uploads, validates image formats, and extracts EXIF data without performing any analysis. Separation allows for independent scaling of upload capacity.

**Verification Service**: Dedicated to advanced image forensics analysis. Implements four sophisticated algorithms:
- Enhanced Error Level Analysis (ELA) for JPEG compression artifacts
- Noise Pattern Analysis for sensor inconsistencies and splicing detection  
- JPEG Quality Analysis for compression quality consistency
- Metadata Consistency Analysis for EXIF validation and editing software detection

**Gateway Service**: Acts as a health monitoring hub and service coordinator. Monitors the health of dependent services and provides centralized status reporting. This separation ensures system observability and reliability.

### Data Flow
1. **Image Upload Flow**: Client → API Service → Metadata Extraction → Response
2. **Analysis Flow**: Client → Verification Service → ELA Processing → Analysis Results
3. **Health Monitoring Flow**: Gateway Service → API Service Health Check → Verification Service Health Check → Aggregated Status

### Communication Patterns
- **Synchronous HTTP REST**: All inter-service communication uses HTTP REST APIs
- **Health Check Protocol**: Each service exposes a `/health` endpoint returning JSON status
- **Timeout Handling**: 5-second timeout for health checks with proper error handling
- **Service Discovery**: Uses Docker Compose service names for internal communication

### Technology Stack
- **FastAPI**: Chosen for its automatic API documentation, async support, and Pydantic integration
- **Docker & Docker Compose**: Provides consistent deployment across environments
- **Pillow (PIL)**: Industry-standard Python library for image processing
- **httpx**: Async HTTP client for inter-service communication
- **Pydantic**: Type validation and serialization for API contracts

## Architecture Overview
The system consists of three FastAPI microservices:

### Service Architecture:
- **API Service (Port 8000)**: Handles image uploads and EXIF metadata extraction
- **Verification Service (Port 8003)**: Performs image integrity analysis using Error Level Analysis  
- **Gateway Service (Port 8002)**: Coordinates health monitoring across all services and manages verification workflows

### Service Communication:
The gateway service actively monitors the health of both the API and verification services, providing centralized health status reporting. Services communicate via HTTP REST APIs for both functional operations and health checks.

## Prerequisites
- Docker (version 20.0 or higher)
- Docker Compose (version 1.29 or higher)
- Python 3.9+ (for local development)

## Installation & Setup
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd image-integrity-verification-system
   ```

2. Build and run all services using Docker Compose:
   ```bash
   docker-compose up --build
   ```

3. Verify all services are running:
   ```bash
   docker-compose ps
   ```

## Usage Instructions

### Health Check Examples
Check the health of all services through the gateway:
```bash
curl http://localhost:8002/health
```

Check individual service health:
```bash
# API Service health
curl http://localhost:8000/health

# Verification Service health  
curl http://localhost:8003/health
```

### Image Upload and Analysis
Upload an image for metadata extraction:
```bash
curl -X POST "http://localhost:8000/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@your_image.jpg"
```

Analyze an image for tampering:
```bash
curl -X POST "http://localhost:8003/analyze" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@your_image.jpg"
```

## API Documentation

### Health Endpoints

#### Gateway Service Health Check
- **URL**: `GET /health`
- **Port**: 8002
- **Response**: 
```json
{
  "service": "gateway-service",
  "status": "healthy",
  "dependencies": {
    "api-service": {
      "status": "healthy",
      "response_time_ms": 15
    },
    "verification-service": {
      "status": "healthy", 
      "response_time_ms": 23
    }
  }
}
```

#### API Service Health Check
- **URL**: `GET /health`
- **Port**: 8000
- **Response**:
```json
{
  "service": "api-service",
  "status": "healthy"
}
```

#### Verification Service Health Check
- **URL**: `GET /health`
- **Port**: 8003
- **Response**:
```json
{
  "service": "verification-service",
  "status": "healthy"
}
```

### Functional Endpoints

#### Image Upload
- **URL**: `POST /upload`
- **Port**: 8000
- **Request**: Multipart form data with image file
- **Response**: Image metadata and EXIF data

#### Image Analysis
- **URL**: `POST /analyze`
- **Port**: 8003  
- **Request**: Multipart form data with image file
- **Response**: Comprehensive forensics analysis with 4 algorithms
```json
{
  "filename": "test_image.jpg",
  "is_potentially_edited": false,
  "confidence_score": 0.234,
  "risk_level": "low",
  "analysis_details": {
    "enhanced_ela": 0.156,
    "metadata_consistency": 0.000,
    "noise_pattern": 0.423,
    "jpeg_quality": 0.357
  },
  "detection_methods": ["enhanced_ela", "metadata_consistency", "noise_pattern", "jpeg_quality"],
  "recommendations": ["LOW RISK: Image appears to be authentic with minimal editing traces"]
}
```

#### Available Algorithms
- **URL**: `GET /algorithms`
- **Port**: 8003
- **Response**: List of available forensic algorithms and descriptions

## Testing

### Manual Testing Steps
1. Start all services: `docker-compose up --build`
2. Test gateway health check: `curl http://localhost:8002/health`
3. Verify all services report as healthy
4. Test image upload with a sample image
5. Test image analysis with the same image
6. Stop one service and verify gateway reports unhealthy status

### Automated Testing
```bash
# Test all health endpoints
curl http://localhost:8000/health
curl http://localhost:8003/health  
curl http://localhost:8002/health

# Test with sample image (replace with actual image path)
curl -X POST "http://localhost:8000/upload" -F "file=@test_image.jpg"
curl -X POST "http://localhost:8003/analyze" -F "file=@test_image.jpg"
```

## Project Structure
```
image-integrity-verification-system/
├── README.md
├── CODE_PROVENANCE.md
├── architecture-diagram.md
├── docker-compose.yml
├── real_image_test.sh
├── services/
│   ├── api/
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── src/
│   │       └── main.py
│   ├── verification/
│   │   ├── Dockerfile  
│   │   ├── requirements.txt
│   │   └── src/
│   │       ├── main.py
│   │       ├── forensics_engine.py
│   │       └── algorithms/
│   │           ├── __init__.py
│   │           ├── ela_analysis.py
│   │           ├── metadata_analysis.py
│   │           ├── noise_analysis.py
│   │           └── jpeg_analysis.py
│   └── gateway/
│       ├── Dockerfile
│       ├── requirements.txt
│       └── src/
│           └── main.py
└── test_img/
```


## Contributing
Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for details.