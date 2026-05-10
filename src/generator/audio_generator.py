import asyncio
import edge_tts
import tempfile
import os
from moviepy.editor import AudioFileClip, concatenate_audioclips

class AudioGenerator:
    def __init__(self):
        self.voice = "en-US-ChristopherNeural"
        self.rate = "-10%"

    def generate_narration(self, script_data, output_path):
        """
        Generates audio line by line to calculate precise timestamps, 
        fixing desync issues, and concatenates them into one audio file.
        """
        print("Generating audio (Natural Voice) and syncing timestamps...")
        
        async def _generate_line(text, path):
            communicate = edge_tts.Communicate(text, self.voice, rate=self.rate)
            await communicate.save(path)

        audio_clips = []
        current_start_time = 0.0

        with tempfile.TemporaryDirectory() as temp_dir:
            for i, item in enumerate(script_data):
                text = item['text']
                if not text.strip():
                    continue

                line_path = os.path.join(temp_dir, f"line_{i}.mp3")
                asyncio.run(_generate_line(text, line_path))

                clip = AudioFileClip(line_path)
                audio_clips.append(clip)

                # Overwrite hallucinated timestamp with exact accumulated duration
                item['start'] = current_start_time
                current_start_time += clip.duration

            if audio_clips:
                final_audio = concatenate_audioclips(audio_clips)
                final_audio.write_audiofile(output_path, logger=None)
                
                for clip in audio_clips:
                    clip.close()
                final_audio.close()
            else:
                print("WARNING: No valid text to generate audio.")

        return output_path