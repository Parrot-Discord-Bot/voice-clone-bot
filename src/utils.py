import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMP_DIR = os.path.join(PROJECT_ROOT, "temp")
VOICE_DIR = os.path.join(PROJECT_ROOT, "voices")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "outputs")
CHECKPOINTS_DIR = os.path.join(PROJECT_ROOT, "checkpoints")
SPEAKERS_DIR = os.path.join(CHECKPOINTS_DIR, "base_speakers/EN")
CONVERTERS_DIR = os.path.join(CHECKPOINTS_DIR, "converter")
ENV_FILE = os.path.join(PROJECT_ROOT, ".env")

def debug(message):
    print(f"DEBUG: {message}")

def error(message):
    print(f"ERROR: {message}")