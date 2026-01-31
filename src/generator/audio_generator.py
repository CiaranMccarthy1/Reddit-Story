from gtts import gTTS

class AudioGenerator:
    def __init__(self):
        pass

    def generate_narration(self, script_data, output_path):
        """
        Combines all script lines into one audio block or generates per line.
        For simplicity, we will combine the text and generate one audio file.
        """
        print("Generating audio...")
        

        full_text = " ".join([item['text'] for item in script_data])
        
        tts = gTTS(text=full_text, lang='en', slow=False)
        tts.save(output_path)
        
        return output_path