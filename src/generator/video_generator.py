from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip

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
        
        for i, item in enumerate(script_data):
            start_time = item['start']
            text = item['text']
            

            if i + 1 < len(script_data):
                end_time = script_data[i+1]['start']
            else:
                end_time = duration

            txt_clip = (TextClip(text, fontsize=50, color='white', font='Arial-Bold', stroke_color='black', stroke_width=2, size=(bg_clip.w * 0.8, None), method='caption')
                        .set_position(('center', 'center'))
                        .set_start(start_time)
                        .set_end(end_time))
            
            text_clips.append(txt_clip)


        final_video = CompositeVideoClip([bg_clip] + text_clips)

        final_video.write_videofile(output_path, fps=24, codec='libx264', audio_codec='aac')
        print(f"Video saved to: {output_path}")