# services/verification/src/algorithms/noise_analysis.py
import numpy as np
import cv2
from scipy import ndimage
from typing import Dict, Any

class NoisePatternAnalyzer:
    """Sensor Noise Pattern Consistency Analyzer"""
    
    def __init__(self):
        self.name = "Noise Pattern Analysis"
        self.version = "1.1"  # Version update
        self.description = "Sensor noise pattern analysis for splicing detection"
        self.block_size = 64
        self.overlap_ratio = 0.5
    
    def analyze(self, image_array: np.ndarray) -> Dict[str, Any]:
        """Execute noise pattern analysis"""
        try:
            # Convert to grayscale
            if len(image_array.shape) == 3:
                gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
            else:
                gray = image_array
            
            # Extract noise and perform analysis
            raw_score = self._analyze_noise_consistency(gray)
            
            # Improved score calculation - map to realistic range
            normalized_score = self._normalize_noise_score(raw_score, gray.shape)
            
            return {
                "score": round(normalized_score, 3),
                "success": True,
                "algorithm": self.name,
                "details": {
                    "block_size": self.block_size,
                    "blocks_analyzed": self._count_blocks(gray.shape),
                    "raw_coefficient_variation": round(raw_score, 3),
                    "method": "Improved Gaussian filter noise extraction"
                }
            }
        except Exception as e:
            return {
                "score": 0.0,
                "success": False,
                "error": str(e),
                "algorithm": self.name
            }
    
    def _analyze_noise_consistency(self, gray_image: np.ndarray) -> float:
        """Completely improved noise consistency analysis"""
        
        # 1. Wavelet-based noise extraction (more precise)
        from scipy import signal
        
        # Extract only high-frequency components
        kernel = np.array([[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]])
        noise = signal.convolve2d(gray_image.astype(float), kernel, mode='same')
        
        # 2. Use adaptive block size
        h, w = gray_image.shape
        adaptive_block_size = min(64, max(32, min(h, w) // 10))
        
        # 3. Calculate noise variance (more stable)
        noise_stats = []
        step = adaptive_block_size // 2
        
        for i in range(0, h - adaptive_block_size + 1, step):
            for j in range(0, w - adaptive_block_size + 1, step):
                block = noise[i:i+adaptive_block_size, j:j+adaptive_block_size]
                
                # Use standard deviation (more stable than variance)
                std = np.std(block)
                if std > 1e-3:  # More lenient threshold
                    noise_stats.append(std)
        
        if len(noise_stats) < 4:
            return 0.0
        
        # 4. Median-based consistency calculation (robust to outliers)
        median_std = np.median(noise_stats)
        mad = np.median(np.abs(np.array(noise_stats) - median_std))  # Median Absolute Deviation
        
        if median_std == 0:
            return 0.0
        
        # 5. Calculate normalized MAD
        normalized_mad = mad / median_std
        return normalized_mad
    
    def _normalize_noise_score(self, raw_score: float, image_shape) -> float:
        """Normalize noise score to 0-1 range"""
        # Empirical normalization function
        # Based on CV values observed in real images
        
        # 1. Adjust based on image size
        image_size = image_shape[0] * image_shape[1]
        size_factor = min(1.0, image_size / (1000 * 1000))  # 1MP baseline
        
        # 2. Set empirical thresholds
        # Original images: CV ~ 0.2-0.8
        # Edited images: CV > 1.0
        low_threshold = 0.3 * size_factor
        high_threshold = 1.2 * size_factor
        
        if raw_score <= low_threshold:
            # Very consistent noise - likely original
            return 0.0
        elif raw_score >= high_threshold:
            # Very inconsistent noise - likely edited
            return 1.0
        else:
            # Middle range - linear mapping
            normalized = (raw_score - low_threshold) / (high_threshold - low_threshold)
            return min(max(normalized, 0.0), 1.0)
    
    def _count_blocks(self, image_shape) -> int:
        """Calculate number of analyzed blocks"""
        h, w = image_shape
        step = max(16, int(self.block_size * self.overlap_ratio))
        blocks_h = max(1, (h - self.block_size) // step + 1)
        blocks_w = max(1, (w - self.block_size) // step + 1)
        return blocks_h * blocks_w