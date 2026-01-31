class VideoGenerationPipeline:
    def __init__(self, content_fetcher, script_builder, audio_generator, video_generator, assets_manager):
        self.content_fetcher = content_fetcher
        self.script_builder = script_builder
        self.audio_generator = audio_generator
        self.video_generator = video_generator
        self.assets_manager = assets_manager

    def run(self, prompt_file, duration=60):
        print("--- Starting Generation Pipeline ---")


        raw_content = self.content_fetcher.generate_script(prompt_file, duration)

        story, script_data = self.script_builder.parse_response(raw_content)
        self.assets_manager.save_script(story, "full_story.txt")
        
        if not script_data:
            print("Error: Could not parse script timestamps.")
            return


        audio_path = self.assets_manager.save_audio(filename="narration.mp3")
        self.audio_generator.generate_narration(script_data, audio_path)


        bg_video = self.assets_manager.get_background_video()

        output_path = self.assets_manager.get_output_path()
        self.video_generator.create_video(bg_video, audio_path, script_data, output_path)

        print("--- Pipeline Finished Successfully ---")