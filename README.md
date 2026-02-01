# 🚀 Robust Multimodal Thumbnail Generation System

This system is an end-to-end automated pipeline designed to convert short natural-language prompts into high-fidelity, YouTube-ready thumbnails. It solves the "hallucination problem" inherent in modern diffusion models by using a **Decoupled Semantic-Compositor** architecture.



---

## 🛠️ System Architecture

The system is built on four core modules:

1.  **Semantic Planner (LLM):** Utilizes GPT-4o to decompose abstract prompts into structured design instructions.
2.  **Visual Generator (Diffusion):** Leverages DALL-E 3 to create high-quality, text-free background imagery.
3.  **Deterministic Compositor (PIL):** Programmatically renders typography to ensure 100% spelling accuracy and legibility.
4.  **Automated Validator (OCR/CV):** A feedback loop using Tesseract OCR and Computer Vision heuristics to verify contrast, safe zones, and textual fidelity.

---

## 📋 Prerequisites

* **Python:** 3.9+
* **Tesseract OCR:** Must be installed on your system.
    * **Windows:** [Download Installer from UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)
    * **macOS:** `brew install tesseract`
    * **Linux:** `sudo apt-get install tesseract-ocr`
* **OpenAI API Key:** Required for LLM and Image Generation.

---

## ⚙️ Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd thumbnail_system
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure Environment:**
    Create a `.env` file in the root directory and add your API key:
    ```text
    OPENAI_API_KEY=sk-xxxx...
    ```

4.  **Update Configuration:**
    Ensure the `TESSERACT_CMD_PATH` in `src/config.py` correctly points to your Tesseract executable (especially on Windows).

---

## 🚀 Usage

### Basic Command
```bash
python main.py "Tutorial: How to Code in Python"
