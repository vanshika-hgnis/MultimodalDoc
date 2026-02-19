import os
import easyocr

# Set model path BEFORE creating reader
MODEL_DIR = os.path.abspath("models/easyocr")

os.makedirs(MODEL_DIR, exist_ok=True)

os.environ["EASYOCR_MODULE_PATH"] = MODEL_DIR

_reader = None


def get_ocr_reader():
    global _reader
    if _reader is None:
        print("Initializing EasyOCR reader...")
        _reader = easyocr.Reader(
            ["en"], gpu=False, model_storage_directory=MODEL_DIR, download_enabled=True
        )
    return _reader
