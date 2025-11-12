# services/verification/src/algorithms/ela_analysis.py
import numpy as np
import io
from PIL import Image, ImageChops
from typing import Dict, Any

class ELAAnalyzer:
    """Enhanced Error Level Analysis"""
    
    def __init__(self):
        self.name = "Enhanced ELA"
        self.version = "1.0"
        self.description = "Multi-quality Error Level Analysis for JPEG compression artifacts"
    
    def analyze(self, image_array: np.ndarray) -> Dict[str, Any]:
        """Execute ELA analysis"""
        try:
            score = self._enhanced_ela_analysis(image_array)
            return {
                "score": round(score, 3),
                "success": True,
                "algorithm": self.name,
                "details": {
                    "qualities_tested": [70, 80, 90, 95],
                    "method": "Multi-quality JPEG recompression"
                }
            }
        except Exception as e:
            return {
                "score": 0.0,
                "success": False,
                "error": str(e),
                "algorithm": self.name
            }
    
    def _enhanced_ela_analysis(self, image_array: np.ndarray) -> float:
        """Internal ELA implementation"""
        image = Image.fromarray(image_array)
        qualities = [70, 80, 90, 95]
        ela_scores = []
        
        for quality in qualities:
            # JPEG recompression
            ela_buffer = io.BytesIO()
            image.save(ela_buffer, 'JPEG', quality=quality)
            ela_buffer.seek(0)
            ela_image = Image.open(ela_buffer)
            
            # Calculate difference
            diff = ImageChops.difference(image, ela_image)
            diff_array = np.array(diff)
            
            # Extract statistical features
            mean_diff = np.mean(diff_array)
            std_diff = np.std(diff_array)
            max_diff = np.max(diff_array)
            
            # Calculate entropy
            entropy = self._calculate_entropy(diff_array)
            
            # Normalized score
            score = (mean_diff + std_diff/10 + max_diff/255 + entropy/10) / 4
            ela_scores.append(score)
        
        # Quality consistency check
        consistency = 1.0 - np.std(ela_scores) / (np.mean(ela_scores) + 1e-8)
        final_ela_score = np.mean(ela_scores) * consistency
        
        return min(final_ela_score, 1.0)
    
    def _calculate_entropy(self, image_array: np.ndarray) -> float:
        """Calculate image entropy"""
        hist, _ = np.histogram(image_array.flatten(), bins=256, range=(0, 255))
        hist = hist / np.sum(hist)
        entropy = -np.sum(hist * np.log2(hist + 1e-8))
        return entropy