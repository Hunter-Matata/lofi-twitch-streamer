import subprocess
import logging
import time
import os
import threading
from src.config import Config

class StreamManager:
    def __init__(self):
        self.process = None
        self.current_playlist = None
        self.stdout_thread = None
        self.stderr_thread = None

    def log_output(self, pipe, name):
        """Log FFmpeg output in real-time"""
        try:
            for line in iter(pipe.readline, ''):
                if line.strip():
                    if "error" in line.lower() or "failed" in line.lower():
                        logging.error(f"FFmpeg {name}: {line.strip()}")
                    else:
                        logging.info(f"FFmpeg {name}: {line.strip()}")
        except Exception as e:
            logging.error(f"Error reading {name}: {e}")

    def create_playlist_file(self, tracks):
        """Create FFmpeg concat playlist file"""
        playlist_path = "current_playlist.txt"
        with open(playlist_path, 'w') as f:
            for track in tracks:
                abs_path = os.path.abspath(track).replace("'", "\\'")
                f.write(f"file '{abs_path}'\n")
        return playlist_path

    def build_stream_command(self, tracks):
        """Build FFmpeg command with concat demuxer"""
        self.current_playlist = self.create_playlist_file(tracks)

        cmd = ["ffmpeg", "-nostdin", "-re", "-y"]

        cmd.extend([
            "-f", "concat", 
            "-safe", "0", 
            "-stream_loop", "-1",  # Loop playlist forever
            "-i", self.current_playlist
        ])

        # Add background video
        if Config.BACKGROUND and Config.BACKGROUND != "NONE":
            cmd.extend(["-stream_loop", "-1", "-i", Config.BACKGROUND])
        else:
            cmd.extend(["-loop", "1", "-f", "lavfi", "-i", "color=c=black:s=1280x720"])

        cmd.extend([
            "-map", "1:v",  # Video from background
            "-map", "0:a",  # Audio from concat playlist
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-b:v", "2500k",
            "-maxrate", "2500k",
            "-bufsize", "5000k",
            "-g", "60",
            "-c:a", "aac",
            "-b:a", "128k",
            "-ar", "44100",
            "-avoid_negative_ts", "make_zero",
            "-fflags", "+genpts",
            "-reconnect", "1",  # Auto-reconnect on network issues
            "-reconnect_at_eof", "1",
            "-reconnect_streamed", "1",
            "-reconnect_delay_max", "10",
            "-f", "flv",
            f"{Config.RTMP_URL}/{Config.STREAM_KEY}",
            "-loglevel", "verbose",  # More detailed logging
            "-stats"  # Show encoding statistics
        ])
        
        return cmd
    
    def start_stream(self, tracks):
        """Start streaming with monitoring"""
        try:
            cmd = self.build_stream_command(tracks)
            logging.info(f"Starting monitored stream with {len(tracks)} tracks")
            logging.info(f"FFmpeg command: {' '.join(cmd)}")

            env = os.environ.copy()
            env['PYTHONUNBUFFERED'] = '1'

            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env,
                stdin=subprocess.DEVNULL,
                bufsize=1  # Line buffered for real-time output
            )

            # Start output monitoring threads
            self.stdout_thread = threading.Thread(
                target=self.log_output, 
                args=(self.process.stdout, "STDOUT"),
                daemon=True
            )
            self.stderr_thread = threading.Thread(
                target=self.log_output, 
                args=(self.process.stderr, "STDERR"),
                daemon=True
            )
            
            self.stdout_thread.start()
            self.stderr_thread.start()

            time.sleep(5)
            if self.process.poll() is not None:
                logging.error(f"FFmpeg died immediately with return code: {self.process.returncode}")
                self.cleanup_playlist()
                raise RuntimeError("FFmpeg process died immediately")

            logging.info("Monitored stream started successfully")
            return self.process

        except Exception as e:
            logging.error(f"Failed to start stream: {e}")
            self.cleanup_playlist()
            raise

    def cleanup_playlist(self):
        """Clean up playlist file"""
        if self.current_playlist and os.path.exists(self.current_playlist):
            try:
                os.remove(self.current_playlist)
            except:
                pass
            self.current_playlist = None

    def stop_stream(self):
        """Stop current stream and cleanup"""
        if self.process:
            try:
                logging.info("Stopping stream...")
                self.process.terminate()
                self.process.wait(timeout=15)
                logging.info(f"Stream stopped with return code: {self.process.returncode}")
            except subprocess.TimeoutExpired:
                logging.warning("Stream didn't stop gracefully, killing...")
                self.process.kill()
                self.process.wait()
            finally:
                self.process = None

        self.cleanup_playlist()

    def is_running(self):
        """Check if stream is still running"""
        return self.process is not None and self.process.poll() is None

    def get_process_info(self):
        """Get detailed process information"""
        if self.process:
            return {
                "pid": self.process.pid,
                "returncode": self.process.returncode,
                "running": self.is_running()
            }
        return None