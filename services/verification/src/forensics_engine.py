# services/verification/src/forensics_engine.py
from typing import Dict, Any, List
import numpy as np
from PIL import Image

# Import algorithm modules
from algorithms.ela_analysis import ELAAnalyzer
from algorithms.metadata_analysis import MetadataAnalyzer
from algorithms.noise_analysis import NoisePatternAnalyzer
from algorithms.jpeg_analysis import JPEGQualityAnalyzer

class AdvancedForensicsEngine:
    """Modular Image Forensics Engine"""
    
    def __init__(self):
        # Initialize each algorithm as independent objects
        self.analyzers = {
            'enhanced_ela': ELAAnalyzer(),
            'metadata_consistency': MetadataAnalyzer(),
            'noise_pattern': NoisePatternAnalyzer(),
            'jpeg_quality': JPEGQualityAnalyzer()
        }
        
        # Set weights for algorithms
        self.weights = {
            'enhanced_ela': 0.35,
            'metadata_consistency': 0.25,
            'noise_pattern': 0.20,
            'jpeg_quality': 0.20
        }
    
    async def analyze_image(self, image: Image.Image, exif_data: Dict) -> Dict[str, Any]:
        """Comprehensive image analysis"""
        image_array = np.array(image)
        results = {}
        
        # Execute each algorithm
        for algo_name, analyzer in self.analyzers.items():
            try:
                if algo_name == 'metadata_consistency':
                    result = analyzer.analyze(exif_data, image_array)
                else:
                    result = analyzer.analyze(image_array)
                
                results[algo_name] = result
            except Exception as e:
                results[algo_name] = {
                    "score": 0.0,
                    "success": False,
                    "error": str(e),
                    "algorithm": analyzer.name
                }
        
        # Calculate final weighted score
        final_score = self._calculate_weighted_score(results)
        
        # Determine risk level
        risk_level = self._determine_risk_level(final_score)
        
        return {
            'individual_scores': {k: v.get('score', 0.0) for k, v in results.items()},
            'algorithm_details': results,
            'final_score': round(final_score, 3),
            'risk_level': risk_level,
            'is_potentially_edited': final_score > 0.4
        }
    
    def _calculate_weighted_score(self, results: Dict[str, Dict]) -> float:
        """Calculate weighted average score"""
        total_score = 0.0
        total_weight = 0.0
        
        for algo_name, weight in self.weights.items():
            if algo_name in results and results[algo_name].get('success', False):
                score = results[algo_name].get('score', 0.0)
                total_score += score * weight
                total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0.0
    
    def _determine_risk_level(self, score: float) -> str:
        """Determine risk level based on score"""
        if score < 0.3:
            return "low"
        elif score < 0.6:
            return "medium"
        else:
            return "high"
    
    @property
    def algorithms(self) -> Dict[str, str]:
        """Get list of available algorithms"""
        return {name: analyzer.name for name, analyzer in self.analyzers.items()}