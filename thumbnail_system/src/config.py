import os
from dotenv import load_dotenv

# Load environment variables from a .env file if present
load_dotenv()

class Config:
    # --- API Secrets ---
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    if not OPENAI_API_KEY:
        raise ValueError("Missing OPENAI_API_KEY environment variable.")

    # --- Output Specs ---
    OUTPUT_WIDTH = 1280
    OUTPUT_HEIGHT = 720
    OUTPUT_DIR = "output"
    
    # --- DALL-E 3 Settings ---
    # DALL-E 3 supports 1792x1024 (Landscape), which we will crop to 1280x720
    DALLE_GEN_SIZE = "1792x1024" 
    DALLE_QUALITY = "hd"
    DALLE_STYLE = "natural" # or "vivid" based on preference

    # --- YouTube UI Safety Margins (pixels) ---
    MARGIN_X = 100
    MARGIN_Y = 80
    
    # --- Typography ---
    # Ensure this path points to a real Bold TTF file on your system
    FONT_PATH = os.path.join("assets", "fonts", "Roboto-Bold.ttf")
    MAX_FONT_SIZE = 130
    MIN_FONT_SIZE = 40
    DEFAULT_FONT_COLOR = (255, 233, 0) # 'YouTube Yellow'
    STROKE_WIDTH = 6
    STROKE_COLOR = (0, 0, 0)
    
    # --- Quality Control ---
    # On Windows, you might need to specify the path to tesseract.exe
    # os.environ["TESSDATA_PREFIX"] = r"C:\Program Files\Tesseract-OCR\tessdata"
    TESSERACT_CMD_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe" # Update for your OS
    
    MIN_CONTRAST_RATIO = 0.5