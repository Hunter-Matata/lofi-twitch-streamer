import time
import logging
import signal
import sys
import os
from src.config import Config
from src.playlist_manager import PlaylistManager
from src.stream_manager import StreamManager

class LofiStreamer:
    def __init__(self):
        self.setup_logging()
        self.playlist_manager = PlaylistManager()
        self.stream_manager = StreamManager()
        self.running = True
        self.start_time = time.time()

        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

    def setup_logging(self):
        log_file = os.path.join(Config.LOGS_DIR, 'lofi_stream.log')
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )

    def signal_handler(self, signum, frame):
        logging.info(f"Received signal {signum}, shutting down...")
        self.running = False
        self.stream_manager.stop_stream()

    def run(self):
        """Main streaming loop"""
        try:
            Config.validate()
            logging.info("Starting lofi stream...")

            tracks = self.playlist_manager.create_shuffled_playlist()
            logging.info(f"Starting stream with {len(tracks)} tracks")

            self.stream_manager.start_stream(tracks)

            while self.running:
                elapsed = time.time() - self.start_time

                if elapsed >= Config.MAX_DURATION:
                    logging.info("Maximum duration reached, restarting stream")
                    break

                if not self.stream_manager.is_running():
                    stdout, stderr = self.stream_manager.process.communicate() if self.stream_manager.process else ("", "")
                    logging.error(f"Stream crashed unexpectedly: {stderr}")

                    if self.running:
                        logging.info("Restarting stream due to crash...")
                        tracks = self.playlist_manager.create_shuffled_playlist()
                        process = self.stream_manager.start_stream(tracks)

                time.sleep(60)
                logging.debug(f"Stream running continuously... Elapsed: {elapsed/3600:.1f}h / Max: {Config.MAX_DURATION/3600:.1f}h")

        except Exception as e:
            logging.error(f"Fatal error: {e}")
            raise
        finally:
            self.stream_manager.stop_stream()
            logging.info("Stream stopped")

def main():
    try:
        streamer = LofiStreamer()
        streamer.run()
    except Exception as e:
        logging.error(f"Application failed: {e}")
        sys.exit(1)