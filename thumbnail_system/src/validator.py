import os
import pytesseract
import difflib
from PIL import Image, ImageOps, ImageFilter, ImageEnhance
from src.config import Config
from src.utils import logger

class Validator:
    def preprocess_for_ocr(self, image: Image.Image) -> Image.Image:
        # Convert to grayscale
        gray = image.convert('L')
        # Boost contrast significantly
        enhancer = ImageEnhance.Contrast(gray)
        gray = enhancer.enhance(3.0) 
        # Invert if the background is dark (Tesseract likes black text on white)
        # binary = ImageOps.invert(gray) 
        threshold = 150
        binary = gray.point(lambda p: 255 if p > threshold else 0)
        return binary

    def validate_result(self, image: Image.Image, expected_text: str, text_bounds: tuple = None) -> dict:
        logger.info("Running Regional QA Validation...")

        tess_path = Config.TESSERACT_CMD_PATH
        logger.info(f"Tess Path: {tess_path}")
        if not os.path.exists(tess_path):
            logger.error(f"CRITICAL: Tesseract executable not found at {tess_path}")
            return {"resolution_pass": True, "ocr_pass": False, "overall_status": "FAIL", "error": "Path invalid"}
        
        pytesseract.pytesseract.tesseract_cmd = tess_path

        report = {"resolution_pass": True, "ocr_pass": False, "overall_status": "FAIL"}

        try:
            if isinstance(image, tuple):
                image = image[0]
            # If we know where the text is, crop to it to ignore background junk
            if text_bounds:
                # Add a small buffer around the bounds
                buffer = 40
                crop_box = (
                    max(0, text_bounds[0] - buffer),
                    max(0, text_bounds[1] - buffer),
                    min(Config.OUTPUT_WIDTH, text_bounds[2] + buffer),
                    min(Config.OUTPUT_HEIGHT, text_bounds[3] + buffer)
                )
                image = image.crop(crop_box)

            processed_img = self.preprocess_for_ocr(image)
            
            # --- CRITICAL CHANGE: PSM 7 or 8 for single lines/words ---
            # PSM 7: Treat image as a single text line.
            # PSM 8: Treat image as a single word.
            custom_config = r'--oem 3 --psm 7' 
            detected_text = pytesseract.image_to_string(processed_img, config=custom_config)
            
            detected_clean = "".join(filter(str.isalnum, detected_text)).upper()
            expected_clean = "".join(filter(str.isalnum, expected_text)).upper()

            similarity = difflib.SequenceMatcher(None, expected_clean, detected_clean).ratio()
            
            report["ocr_detected"] = detected_clean
            report["confidence_score"] = similarity

            if similarity >= 0.5 or expected_clean in detected_clean:
                report["ocr_pass"] = True
            
        except Exception as e:
            logger.error(f"OCR Error: {e}")

        if report["ocr_pass"]: report["overall_status"] = "PASS"
        return report