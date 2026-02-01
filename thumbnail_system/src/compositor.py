from PIL import Image, ImageDraw, ImageFont
import numpy as np
from src.config import Config
from src.utils import logger

class Compositor:
    def __init__(self):
        self.font_path = Config.FONT_PATH
        
    def _get_dynamic_font(self, text: str, max_width: int, draw_obj: ImageDraw) -> ImageFont.FreeTypeFont:
        """
        Recursively reduces font size until text fits within safe width.
        """
        size = Config.MAX_FONT_SIZE
        while size > Config.MIN_FONT_SIZE:
            try:
                font = ImageFont.truetype(self.font_path, size)
            except OSError:
                # Fallback if custom font missing
                font = ImageFont.load_default()
                return font
            
            # Check width
            bbox = draw_obj.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            
            if text_width <= max_width:
                return font
            
            size -= 5
        
        logger.warning("Text too long even at minimum font size. Truncation risk.")
        return ImageFont.truetype(self.font_path, Config.MIN_FONT_SIZE)

    def _analyze_local_contrast(self, bg_image: Image.Image, area: tuple) -> float:
        """
        Returns luminance (0.0 - 1.0) of the specific area where text will sit.
        """
        crop = bg_image.crop(area)
        grayscale = crop.convert("L")
        stat = np.array(grayscale)
        return np.mean(stat) / 255.0

    def render(self, background: Image.Image, text: str) -> Image.Image:
        logger.info("Compositing text layer...")
        final_img = background.copy()
        draw = ImageDraw.Draw(final_img)
        
        # 1. Determine safe bounds
        safe_width = Config.OUTPUT_WIDTH - (Config.MARGIN_X * 2)
        
        # 2. Get Font
        font = self._get_dynamic_font(text, safe_width, draw)
        
        # 3. Calculate Position (Center Weighted)
        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        
        x = (Config.OUTPUT_WIDTH - text_w) // 2
        y = (Config.OUTPUT_HEIGHT - text_h) // 2
        
        # 4. CONTRAST GUARDRAIL
        # Check if the background behind text is too bright for yellow text
        text_area = (x, y, x + text_w, y + text_h)
        bg_luminance = self._analyze_local_contrast(final_img, text_area)
        
        # If background is bright (> 0.5), or very messy, add a shadow box (Scrim)
        if bg_luminance > 0.4:
            logger.info(f"Low contrast detected (Lum: {bg_luminance:.2f}). Injecting Scrim.")
            overlay = Image.new('RGBA', final_img.size, (0,0,0,0))
            overlay_draw = ImageDraw.Draw(overlay)
            
            padding = 20
            # Semi-transparent black box
            overlay_draw.rectangle(
                [x - padding, y - padding, x + text_w + padding, y + text_h + padding],
                fill=(0, 0, 0, 180)
            )
            final_img = Image.alpha_composite(final_img.convert('RGBA'), overlay).convert('RGB')
            draw = ImageDraw.Draw(final_img) # Re-init draw on new surface
            
        # 5. Draw Text
        draw.text(
            (x, y), text, 
            font=font, 
            fill=Config.DEFAULT_FONT_COLOR,
            stroke_width=Config.STROKE_WIDTH, 
            stroke_fill=Config.STROKE_COLOR
        )
        
        text_bounds = (x, y, x + text_w, y + text_h)
        return final_img, text_bounds