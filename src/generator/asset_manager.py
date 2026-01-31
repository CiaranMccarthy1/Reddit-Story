import os
from pathlib import Path
from datetime import datetime

class AssetManager:
    def __init__(self, project_root):
        self.root = Path(project_root)
        self.assets_dir = self.root / "assets"
        self.output_dir = self.root / "outputFile"
        self.temp_dir = self.root / "temp"
        self.current_session_id = None

        self.final_video_dir = self.output_dir / "finalVideo"

        for path in [self.assets_dir, self.output_dir, self.temp_dir, self.final_video_dir]: 
            path.mkdir(parents=True, exist_ok=True)

    def create_session(self):
        """Creates a new unique session for temp files and output naming."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.current_session_id = f"video_{timestamp}"
        
        # Create unique temp subdir
        session_temp_dir = self.temp_dir / self.current_session_id
        session_temp_dir.mkdir(parents=True, exist_ok=True)
        
        return self.current_session_id

    def get_background_video(self):

        videos = list(self.assets_dir.glob("*.mp4"))
        if videos:
            return str(videos[0])
        raise FileNotFoundError("No background video found in 'assets/' folder.")

    def get_font_path(self):
        # Specific check for Windows Ariel font
        win_path = Path("C:/Windows/Fonts/arial.ttf")
        if win_path.exists():
            return str(win_path)
            
        return "Arial" # Fallback for other OS or if ImageMagick is somehow working for them later

    def _get_current_temp_dir(self):
        if self.current_session_id:
            return self.temp_dir / self.current_session_id
        return self.temp_dir

    def save_script(self, text, filename="story.txt"):
        path = self._get_current_temp_dir() / filename
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        return str(path)

    def save_audio(self, audio_bytes=None, filename="narration.mp3"):
        return str(self._get_current_temp_dir() / filename)

    def get_output_path(self, i: int = None, extension=".mp4"):
        if i is not None:
             filename = f"video{i}{extension}"
        elif self.current_session_id:
            # Match the session ID
            filename = f"{self.current_session_id}{extension}"
        else:
            # Fallback if no session was created (e.g. legacy test)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"video_{timestamp}{extension}"
            
        final_path = self.final_video_dir / filename
        
        return str(final_path)