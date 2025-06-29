import os
import subprocess
import logging
from src.config import Config

class AudioValidator:
    @staticmethod
    def validate_audio_file(filepath):
        """Validate audio file using ffprobe"""
        if not os.path.exists(filepath):
            return False

        if os.path.getsize(filepath) == 0:
            return False

        try:
            cmd = [
                "ffprobe",
                "-v", "quiet",
                "-print_format", "json",
                "-show_format",
                "-show_streams",
                filepath
            ]
            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=Config.VALIDATION_TIMEOUT,
                check=True
            )
            return len(result.stdout) > 0
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
            logging.warning(f"Failed to validate audio file: {filepath}")
            return False

    @staticmethod
    def get_audio_duration(filepath):
        """Get audio duration in seconds"""
        try:
            cmd = [
                "ffprobe",
                "-v", "quiet",
                "-show_entries", "format=duration",
                "-of", "csv=p=0",
                filepath
            ]
            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=Config.VALIDATION_TIMEOUT,
                check=True,
                text=True
            )
            return float(result.stdout.strip())
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, ValueError):
            return 0.0
