# services/verification/src/algorithms/metadata_analysis.py
import numpy as np
from typing import Dict, Any

class MetadataAnalyzer:
    """EXIF Metadata Consistency Analyzer"""
    
    def __init__(self):
        self.name = "Metadata Consistency"
        self.version = "1.0"
        self.description = "EXIF metadata consistency and editing software detection"
        self.editing_software = [
            'photoshop', 'gimp', 'lightroom', 'snapseed', 
            'canva', 'pixlr', 'paint.net', 'affinity'
        ]
    
    def analyze(self, exif_data: Dict, image_array: np.ndarray) -> Dict[str, Any]:
        """Execute metadata analysis"""
        try:
            suspicion_indicators = []
            suspicion_score = 0.0
            
            # Check resolution mismatch
            resolution_score = self._check_resolution_mismatch(exif_data, image_array)
            if resolution_score > 0:
                suspicion_score += resolution_score
                suspicion_indicators.append("Resolution mismatch detected")
            
            # Check editing software
            software_score = self._check_editing_software(exif_data)
            if software_score > 0:
                suspicion_score += software_score
                suspicion_indicators.append("Image editing software detected")
            
            # Check timestamps
            timestamp_score = self._check_timestamp_inconsistency(exif_data)
            if timestamp_score > 0:
                suspicion_score += timestamp_score
                suspicion_indicators.append("Timestamp inconsistency found")
            
            # Check orientation changes
            orientation_score = self._check_orientation_changes(exif_data)
            if orientation_score > 0:
                suspicion_score += orientation_score
                suspicion_indicators.append("Image orientation modified")
            
            return {
                "score": round(min(suspicion_score, 1.0), 3),
                "success": True,
                "algorithm": self.name,
                "details": {
                    "indicators": suspicion_indicators,
                    "checks_performed": ["resolution", "software", "timestamp", "orientation"]
                }
            }
        except Exception as e:
            return {
                "score": 0.0,
                "success": False,
                "error": str(e),
                "algorithm": self.name
            }
    
    def _check_resolution_mismatch(self, exif_data: Dict, image_array: np.ndarray) -> float:
        """Check for resolution mismatch"""
        exif_width = exif_data.get('ExifImageWidth')
        exif_height = exif_data.get('ExifImageHeight')
        
        if exif_width and exif_height:
            try:
                actual_height, actual_width = image_array.shape[:2]
                if int(exif_width) != actual_width or int(exif_height) != actual_height:
                    return 0.3
            except:
                pass
        return 0.0
    
    def _check_editing_software(self, exif_data: Dict) -> float:
        """Check for editing software traces"""
        software = str(exif_data.get('Software', '')).lower()
        if any(editor in software for editor in self.editing_software):
            return 0.4
        return 0.0
    
    def _check_timestamp_inconsistency(self, exif_data: Dict) -> float:
        """Check for timestamp inconsistency"""
        datetime_original = exif_data.get('DateTimeOriginal')
        datetime_modified = exif_data.get('DateTime')
        if datetime_original and datetime_modified and datetime_original != datetime_modified:
            return 0.2
        return 0.0
    
    def _check_orientation_changes(self, exif_data: Dict) -> float:
        """Detect orientation changes"""
        orientation = exif_data.get('Orientation')
        if orientation and str(orientation) != '1':
            return 0.1
        return 0.0