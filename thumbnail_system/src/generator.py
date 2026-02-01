from abc import ABC, abstractmethod
from PIL import Image
import requests
from io import BytesIO
from openai import OpenAI
from src.config import Config
from src.utils import logger

class BaseGenerator(ABC):
    @abstractmethod
    def generate(self, prompt: str) -> Image.Image:
        pass

class OpenAIGenerator(BaseGenerator):
    def __init__(self):
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)

    def generate(self, prompt: str) -> Image.Image:
        logger.info(f"Requesting DALL-E 3 Image... Prompt: {prompt[:50]}...")
        
        try:
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size=Config.DALLE_GEN_SIZE, # 1792x1024
                quality=Config.DALLE_QUALITY,
                style=Config.DALLE_STYLE,
                n=1,
            )

            image_url = response.data[0].url
            logger.info("Image generated. Downloading...")
            
            # Download image
            img_response = requests.get(image_url)
            img = Image.open(BytesIO(img_response.content))
            
            # Post-Processing: Resize/Crop to 1280x720
            # DALL-E 3 landscape is 1792x1024. We need 1280x720.
            # We will resize maintaining aspect ratio, then center crop.
            
            target_ratio = Config.OUTPUT_WIDTH / Config.OUTPUT_HEIGHT
            img_ratio = img.width / img.height
            
            if img_ratio > target_ratio:
                # Image is wider than target
                new_height = Config.OUTPUT_HEIGHT
                new_width = int(new_height * img_ratio)
            else:
                # Image is taller than target
                new_width = Config.OUTPUT_WIDTH
                new_height = int(new_width / img_ratio)
                
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Center Crop
            left = (img.width - Config.OUTPUT_WIDTH) / 2
            top = (img.height - Config.OUTPUT_HEIGHT) / 2
            right = (img.width + Config.OUTPUT_WIDTH) / 2
            bottom = (img.height + Config.OUTPUT_HEIGHT) / 2
            
            img = img.crop((left, top, right, bottom))
            
            return img

        except Exception as e:
            logger.error(f"DALL-E Generation failed: {e}")
            # Return a blank black image so the pipeline doesn't crash completely
            return Image.new('RGB', (Config.OUTPUT_WIDTH, Config.OUTPUT_HEIGHT), color=(0,0,0))