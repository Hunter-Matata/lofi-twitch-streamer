import os
import random
import logging
from src.audio_validator import AudioValidator
from src.config import Config

class PlaylistManager:
    def __init__(self):
        self.validator = AudioValidator()

    def get_valid_tracks(self):
        """Get all valid audio tracks from audio directory"""
        if not os.path.exists(Config.AUDIO_DIR):
            raise RuntimeError(f"Audio directory '{Config.AUDIO_DIR}' not found")

        all_files = [
            f for f in os.listdir(Config.AUDIO_DIR)
            if f.lower().endswith(('.mp3', '.wav', '.flac', '.m4a'))
        ]

        valid_tracks = []
        for filename in all_files:
            filepath = os.path.join(Config.AUDIO_DIR, filename)
            if self.validator.validate_audio_file(filepath):
                valid_tracks.append(filepath)
            else:
                logging.warning(f"Skipping invalid audio file: {filename}")

        if not valid_tracks:
            raise RuntimeError("No valid audio files found in audio directory")

        return valid_tracks

    def create_shuffled_playlist(self):
        """Create a shuffled playlist of valid tracks"""
        tracks = self.get_valid_tracks()
        random.shuffle(tracks)
        logging.info(f"Created playlist with {len(tracks)} tracks")
        return tracks
