# config/settings.py
import os
from pathlib import Path
from dotenv import load_dotenv

# 1. Dynamically calculate the absolute path to your root project folder
# __file__ is settings.py -> parent is config/ -> parent.parent is catalyst-portops-sentinel/
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"

# 2. Force python-dotenv to load from this exact absolute path
load_dotenv(dotenv_path=ENV_PATH)

class Settings:
    DNAC_BASE_URL = os.getenv("DNAC_BASE_URL")
    DNAC_USER = os.getenv("DNAC_USER")
    DNAC_PASSWORD = os.getenv("DNAC_PASSWORD")
    WEBEX_WEBHOOK_URL = os.getenv("WEBEX_WEBHOOK_URL")

    # 3. Validate and debug
    if not all([DNAC_BASE_URL, DNAC_USER, DNAC_PASSWORD]):
        print(f"\n[DEBUG] Looked for .env file at: {ENV_PATH}")
        print(f"[DEBUG] DNAC_BASE_URL: {DNAC_BASE_URL}")
        print(f"[DEBUG] DNAC_USER: {DNAC_USER}")
        print(f"[DEBUG] DNAC_PASSWORD: {'***Loaded***' if DNAC_PASSWORD else 'None'}\n")
        raise ValueError("CRITICAL: Missing Cisco Catalyst Center credentials in .env file!")

settings = Settings()