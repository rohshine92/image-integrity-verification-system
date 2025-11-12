# services/verification/src/algorithms/jpeg_analysis.py
import numpy as np
import io
from PIL import Image, ImageChops
from typing import Dict, Any, List

class JPEGQualityAnalyzer:
    """JPEG Compression Quality Consistency Analyzer"""
    
    def __init__(self):
        self.name = "JPEG Quality Analysis"
        self.version = "1.0"
        self.description = "JPEG compression quality consistency analysis"
        self.test_qualities = [50, 60, 70, 80, 90, 95]
    
    def analyze(self, image_array: np.ndarray) -> Dict[str, Any]:
        """Execute JPEG quality analysis"""
        try:
            image = Image.fromarray(image_array)
            
            # Analyze quality consistency
            inconsistency_score = self._analyze_compression_consistency(image)
            
            # Estimate original quality
            estimated_quality = self._estimate_original_quality(image)
            
            return {
                "score": round(inconsistency_score, 3),
                "success": True,
                "algorithm": self.name,
                "details": {
                    "estimated_original_quality": estimated_quality,
                    "qualities_tested": self.test_qualities,
                    "method": "Multi-quality recompression analysis"
                }
            }
        except Exception as e:
            return {
                "score": 0.0,
                "success": False,
                "error": str(e),
                "algorithm": self.name
            }
    
    def _analyze_compression_consistency(self, image: Image.Image) -> float:
        """Analyze compression quality consistency"""
        quality_scores = []
        
        for quality in self.test_qualities:
            # Recompress with specified quality
            buffer = io.BytesIO()
            image.save(buffer, 'JPEG', quality=quality)
            buffer.seek(0)
            compressed = Image.open(buffer)
            
            # Calculate difference from original
            diff = ImageChops.difference(image, compressed)
            diff_score = np.mean(np.array(diff))
            quality_scores.append(diff_score)
        
        # Find minimum difference quality
        min_diff_index = np.argmin(quality_scores)
        min_diff = quality_scores[min_diff_index]
        
        # Calculate inconsistency score (difference with most similar quality)
        inconsistency = min_diff / 255.0
        
        return max(0.0, inconsistency)
    
    def _estimate_original_quality(self, image: Image.Image) -> int:
        """Estimate original JPEG quality"""
        quality_scores = []
        
        for quality in self.test_qualities:
            buffer = io.BytesIO()
            image.save(buffer, 'JPEG', quality=quality)
            buffer.seek(0)
            compressed = Image.open(buffer)
            
            diff = ImageChops.difference(image, compressed)
            diff_score = np.mean(np.array(diff))
            quality_scores.append(diff_score)
        
        # Return quality with smallest difference
        min_diff_index = np.argmin(quality_scores)
        return self.test_qualities[min_diff_index]