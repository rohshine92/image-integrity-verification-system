#!/bin/bash

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔍 Image Integrity Verification - Improved Testing${NC}"
echo "============================================================"

# find image
echo -e "${BLUE}📁 Preparing test images...${NC}"
if [ -d "test_img" ]; then
    echo "Contents of test_img directory:"
    ls -la test_img/
    
    # original image
    if [ -f "test_img/img_1746.jpg" ]; then
        cp test_img/img_1746.jpg original_image.jpg
        echo -e "${GREEN}✅ Original image: original_image.jpg${NC}"
    fi
    
    # find modified image
    for file in test_img/IMG_modified* test_img/modified* test_img/*edit* test_img/*alter* test_img/*change*; do
        if [ -f "$file" ]; then
            cp "$file" modified_image.jpg
            echo -e "${GREEN}✅ Modified image: modified_image.jpg (from $(basename "$file"))${NC}"
            break
        fi
    done
    
    if [ ! -f "modified_image.jpg" ]; then
        echo -e "${YELLOW}⚠️  No modified image found. Available files:${NC}"
        ls test_img/
    fi
else
    echo -e "${YELLOW}⚠️  test_img directory not found${NC}"
fi

echo ""
echo -e "${BLUE}🏥 Step 1: Health Check All Services${NC}"
echo "------------------------------------"

# check the service
echo "Docker services status:"
docker-compose ps

echo ""
# API Service
echo -n "API Service (8000): "
api_response=$(curl -s http://localhost:8000/health 2>/dev/null)
if [ $? -eq 0 ] && [ -n "$api_response" ]; then
    echo -e "${GREEN}✅ HEALTHY${NC}"
    echo "  $api_response"
else
    echo -e "${RED}❌ UNHEALTHY${NC}"
fi

echo ""
# Verification Service
echo -n "Verification Service (8003): "
verification_response=$(curl -s http://localhost:8003/health 2>/dev/null)
if [ $? -eq 0 ] && [ -n "$verification_response" ]; then
    echo -e "${GREEN}✅ HEALTHY${NC}"
    echo "  $verification_response"
else
    echo -e "${RED}❌ UNHEALTHY${NC}"
    echo "  Checking logs..."
    docker-compose logs --tail=5 verification
fi

echo ""
# Gateway Service
echo -n "Gateway Service (8002): "
gateway_response=$(curl -s http://localhost:8002/health 2>/dev/null)
if [ $? -eq 0 ] && [ -n "$gateway_response" ]; then
    echo -e "${GREEN}✅ HEALTHY${NC}"
    echo "  $gateway_response"
else
    echo -e "${RED}❌ UNHEALTHY${NC}"
    echo "  Checking logs..."
    docker-compose logs --tail=5 gateway
fi

echo ""
echo -e "${BLUE}📸 Step 2: Testing Original Image${NC}"
echo "--------------------------------"
if [ -f "original_image.jpg" ]; then
    echo "🔍 Analyzing original image for metadata..."
    curl -s -X POST "http://localhost:8000/upload" -F "file=@original_image.jpg" | jq '.' 2>/dev/null || echo "JSON parsing failed"
    
    echo ""
    echo "🔍 Analyzing original image for tampering..."
    curl -s -X POST "http://localhost:8003/analyze" -F "file=@original_image.jpg" | jq '.' 2>/dev/null || echo "Analysis failed or returned empty"
else
    echo -e "${YELLOW}⚠️  Original image not found${NC}"
fi

echo ""
echo -e "${BLUE}🎨 Step 3: Testing Modified Image${NC}"
echo "--------------------------------"
if [ -f "modified_image.jpg" ]; then
    echo "🔍 Analyzing modified image for metadata..."
    curl -s -X POST "http://localhost:8000/upload" -F "file=@modified_image.jpg" | jq '.' 2>/dev/null || echo "JSON parsing failed"
    
    echo ""
    echo "🔍 Analyzing modified image for tampering..."
    curl -s -X POST "http://localhost:8003/analyze" -F "file=@modified_image.jpg" | jq '.' 2>/dev/null || echo "Analysis failed or returned empty"
else
    echo -e "${YELLOW}⚠️  Modified image not found${NC}"
fi

echo ""
echo -e "${BLUE}🏥 Step 4: Gateway Aggregated Health${NC}"
echo "-----------------------------------"
echo "🔍 Checking all services through gateway..."
curl -s http://localhost:8002/health | jq '.' 2>/dev/null || curl -s http://localhost:8002/health

echo ""
echo -e "${GREEN}✅ Testing complete!${NC}"
