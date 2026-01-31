from moviepy.editor import VideoFileClip, AudioFileClip, CompositeVideoClip, ImageClip
from src.generator.text_renderer import create_text_image

class VideoGenerator:
    def __init__(self, asset_manager):
        self.assets = asset_manager

    def create_video(self, background_path, audio_path, script_data, output_path):
        print("Compositing video...")
        
   
        audio = AudioFileClip(audio_path)
        duration = audio.duration

  
        bg_clip = VideoFileClip(background_path)

        target_width = bg_clip.h * 9 / 16
        
 
        x_center = bg_clip.w / 2
        x1 = x_center - (target_width / 2)
        x2 = x_center + (target_width / 2)
        
 
        bg_clip = bg_clip.crop(x1=x1, y1=0, x2=x2, y2=bg_clip.h)
        
        if bg_clip.duration < duration:
            bg_clip = bg_clip.loop(duration=duration)
        else:
            bg_clip = bg_clip.subclip(0, duration)
            
        bg_clip = bg_clip.set_audio(audio)


        text_clips = []
        font_path = self.assets.get_font_path()
        
        for i, item in enumerate(script_data):
            start_time = item['start']
            text = item['text']
            
            if i + 1 < len(script_data):
                end_time = script_data[i+1]['start']
            else:
                end_time = duration
                
            total_duration = end_time - start_time
            
            # 1. Split text into chunks (Targeting 2-3 words per chunk for readability)
            words = text.split()
            chunks = []
            
            idx = 0
            while idx < len(words):
                current_chunk = [words[idx]]
                current_char_count = len(words[idx])
                idx += 1
                
                # Try to add next words if total length isn't too long
                while idx < len(words) and len(current_chunk) < 3 and current_char_count < 20:
                     next_word = words[idx]
                     current_chunk.append(next_word)
                     current_char_count += len(next_word) + 1 # +1 for space
                     idx += 1
                
                chunks.append(" ".join(current_chunk))
            
            # 2. Distribute time evenly
            if not chunks: continue
            chunk_duration = total_duration / len(chunks)
            
            current_start = start_time
            
            for chunk in chunks:
                current_end = current_start + chunk_duration
                
                # Use custom renderer
                text_img = create_text_image(
                    chunk, 
                    font_path, 
                    font_size=80, # Increased font size for single words
                    max_width=bg_clip.w * 0.9
                )
                
                txt_clip = (ImageClip(text_img)
                            .set_position(('center', 'center'))
                            .set_start(current_start)
                            .set_end(current_end)
                            .set_duration(chunk_duration))
                
                text_clips.append(txt_clip)
                current_start = current_end


        final_video = CompositeVideoClip([bg_clip] + text_clips)

        final_video.write_videofile(output_path, fps=24, codec='libx264', audio_codec='aac')
        print(f"Video saved to: {output_path}")