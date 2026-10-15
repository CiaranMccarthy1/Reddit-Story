
import argparse
import sys
from pathlib import Path
from src.generator.config import load_config, build_generator
from src.generator.script_builder import ScriptBuilder
from src.generator.audio_generator import AudioGenerator
from src.generator.video_generator import VideoGenerator
from src.generator.asset_manager import AssetManager
from src.generator.pipeline import VideoGenerationPipeline

def main():
    parser = argparse.ArgumentParser(description="Reddit Video Generator CLI")
    parser.add_argument("prompt_file", help="Path to the prompt file (e.g., Prompts/AITA.txt)")
    parser.add_argument("--duration", type=int, default=60, help="Target duration of the script in seconds (default: 60)")
    parser.add_argument("--provider", choices=["gemini", "openai", "openrouter"],
                        help="AI provider to use (overrides config.toml)")
    parser.add_argument("--model", help="Model name to use (overrides config.toml)")
    parser.add_argument("--config", help="Path to TOML config file (default: config.toml)")

    try:
        args = parser.parse_args()
        print(f"--- Starting Pipeline for {args.prompt_file} ---")

        project_root = Path(__file__).parent.parent

        config = load_config(
            project_root=project_root,
            config_path=args.config,
            provider=args.provider,
            model=args.model,
        )
        content_fetcher = build_generator(config)
        print(f"Provider: {config.provider} | Model: {content_fetcher.model}")

        # Initialize components
        assets_manager = AssetManager(project_root)
        script_builder = ScriptBuilder()
        audio_generator = AudioGenerator()
        video_generator = VideoGenerator(assets_manager)

        # Initialize pipeline
        pipeline = VideoGenerationPipeline(
            content_fetcher,
            script_builder,
            audio_generator,
            video_generator,
            assets_manager
        )

        # Run pipeline
        pipeline.run(args.prompt_file, duration=args.duration)

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__": # pragma: no cover
    main()
