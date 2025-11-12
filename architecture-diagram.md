# Architecture Diagram

```
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│    API Service      │    │ Verification Service│    │  Gateway Service    │
│    (Port 8000)      │    │    (Port 8001)      │    │    (Port 8002)      │
│                     │    │                     │    │                     │
│ GET /health         │    │ GET /health         │    │ GET /health         │
│ POST /upload        │    │ POST /analyze       │    │ POST /verify        │
│                     │    │                     │    │                     │
│ - Image upload      │    │ - Error Level       │    │ - Health monitoring │
│ - EXIF extraction   │    │   Analysis          │    │ - Service coordination│
│ - Metadata parsing  │    │ - Tampering detection│   │ - Dependency checks │
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
         ▲                           ▲                           │
         │                           │                           │
         │◄──────────────────────────┼───────────────────────────┘
         │                           │
         │         Health Check Monitoring
         │              (5s timeout)
         │
    ┌─────────┐
    │ Client  │
    │ Requests│
    └─────────┘
```

## Data Flow

### Health Check Flow:
1. Client → Gateway Service `/health`
2. Gateway → API Service `/health` (5s timeout)
3. Gateway → Verification Service `/health` (5s timeout)
4. Gateway ← Aggregated response with dependency status

### Image Processing Flow:
1. Client → API Service `/upload` (image file)
2. API Service → EXIF extraction & metadata analysis
3. Client → Verification Service `/analyze` (image file)  
4. Verification Service → Error Level Analysis processing