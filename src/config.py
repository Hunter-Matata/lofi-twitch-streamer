import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    AUDIO_DIR = "audio"
    LOGS_DIR = "logs"
    RTMP_URL = os.getenv("RTMP_URL")
    STREAM_KEY = os.getenv("STREAM_KEY")
    BACKGROUND = os.getenv("BACKGROUND")
    MAX_DURATION = int(os.getenv("MAX_DURATION", 169200))
    CROSSFADE_DURATION = float(os.getenv("CROSSFADE_DURATION", 3.0))
    VALIDATION_TIMEOUT = int(os.getenv("VALIDATION_TIMEOUT", 10))

    @classmethod
    def validate(cls):
        if not cls.RTMP_URL or not cls.STREAM_KEY:
            raise ValueError("RTMP_URL and STREAM_KEY must be set in environment")
        if not os.path.exists(cls.AUDIO_DIR):
            raise ValueError(f"Audio directory '{cls.AUDIO_DIR}' does not exist")

        os.makedirs(cls.LOGS_DIR, exist_ok=True)