import os
import argparse
from src.planner import SemanticPlanner
from src.generator import OpenAIGenerator
from src.compositor import Compositor
from src.validator import Validator
from src.config import Config
from src.utils import logger

def main():
    parser = argparse.ArgumentParser(description="Robust Multimodal Thumbnail Generation System")
    parser.add_argument("prompt", type=str, help="The concept prompt (e.g. 'Quiz: Guess the Country')")
    parser.add_argument("--mock", action="store_true", help="Use mock generator to save API credits")
    args = parser.parse_args()
    
    # Check Environment
    if not Config.OPENAI_API_KEY:
        logger.error("Error: OPENAI_API_KEY not found in environment.")
        return

    os.makedirs(Config.OUTPUT_DIR, exist_ok=True)
    
    # 1. Plan (LLM)
    planner = SemanticPlanner()
    plan = planner.create_plan(args.prompt)
    
    # 2. Generate (Visuals)
    if args.mock:
        from src.generator import MockGenerator
        generator = MockGenerator()
    else:
        generator = OpenAIGenerator()
        
    raw_bg = generator.generate(plan.visual_prompt)
    
    # 3. Composite (Deterministic Text)
    compositor = Compositor()
    final_image, text_coords = compositor.render(raw_bg, plan.title_text)
    
    # 4. Validate (OCR & QC)
    validator = Validator()
    report = validator.validate_result(final_image, plan.title_text, text_bounds=text_coords)
    
    logger.info(f"FINAL QA REPORT: {report}")
    
    # Save Logic
    filename = f"{plan.title_text.replace(' ', '_')[:30]}.png"
    save_path = os.path.join(Config.OUTPUT_DIR, filename)
    final_image.save(save_path)
    
    if report["overall_status"] == "PASS":
        logger.info(f"SUCCESS: Production-ready thumbnail saved to {save_path}")
    else:
        logger.warning(f"WARNING: Thumbnail saved to {save_path}, but failed automated QA.")

if __name__ == "__main__":
    main()