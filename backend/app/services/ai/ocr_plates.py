import logging
import re
import cv2
import numpy as np

logger = logging.getLogger(__name__)

try:
    import easyocr
    reader = easyocr.Reader(["es", "en"], gpu=False)
    HAS_EASYOCR = True
except ImportError:
    HAS_EASYOCR = False
    logger.warning("easyocr library not found.")

def preprocess_image(image_bytes: bytes) -> np.ndarray:
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        return None
        
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, 11, 17, 17)
    return gray

def is_valid_bolivian_plate(text: str) -> bool:
    text_clean = re.sub(r'[^A-Z0-9]', '', text.upper())
    return bool(re.match(r'^\d{3,4}[A-Z]{3}$', text_clean))

def read_license_plate(image_bytes: bytes) -> dict:
    result_dict = {"plate": "", "confidence": 0.0, "raw_text": "", "is_valid_format": False}
    try:
        gray_img = preprocess_image(image_bytes)
        if gray_img is None:
            return result_dict
            
        if HAS_EASYOCR:
            results = reader.readtext(gray_img, allowlist='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ')
            
            best_plate = ""
            best_conf = 0.0
            raw_text = []
            
            for (bbox, text, prob) in results:
                raw_text.append(text)
                text_clean = re.sub(r'[^A-Z0-9]', '', text.upper())
                if is_valid_bolivian_plate(text_clean):
                    if prob > best_conf:
                        best_plate = text_clean
                        best_conf = prob
            
            result_dict["raw_text"] = " ".join(raw_text)
            
            if best_plate:
                result_dict["plate"] = best_plate
                result_dict["confidence"] = float(best_conf)
                result_dict["is_valid_format"] = True
            else:
                if results:
                    results.sort(key=lambda x: x[2], reverse=True)
                    text_clean = re.sub(r'[^A-Z0-9]', '', results[0][1].upper())
                    result_dict["plate"] = text_clean
                    result_dict["confidence"] = float(results[0][2])
                    result_dict["is_valid_format"] = is_valid_bolivian_plate(text_clean)
        else:
            # Fallback if no easyocr
            pass
            
    except Exception as e:
        logger.error(f"Error in read_license_plate: {e}")
        
    return result_dict
