import asyncio
import edge_tts

class AudioGenerator:
    def __init__(self):
        self.voice = "en-US-ChristopherNeural"
        self.rate = "-10%"

    def generate_narration(self, script_data, output_path):
        """
        Combines all script lines into one audio block or generates per line.
        For simplicity, we will combine the text and generate one audio file.
        """
        print("Generating audio (Natural Voice)...")
        
        full_text = " ".join([item['text'] for item in script_data])
        
        print(f"Audio Input Text Length: {len(full_text)} characters")
        if len(full_text) < 100:
             print(f"WARNING: Audio text is very short: '{full_text}'")

        async def _generate():
            communicate = edge_tts.Communicate(full_text, self.voice, rate=self.rate)
            await communicate.save(output_path)

        asyncio.run(_generate())
        
        return output_path