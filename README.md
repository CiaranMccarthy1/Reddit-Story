# Reddit Story Generator

A fully automated pipeline to generate short-form video content from text prompts (e.g., Reddit stories) using AI-generated scripts, narration, and background video.

## Features

- **Content Generation**: Uses Google Gemini API to write engaging scripts.
- **Narration**: Generates voiceovers using `edge-tts` or `gTTS`.
- **Video Composition**: Automatically edits background video, adds subtitles, and syncs audio using `moviepy`.
- **CLI Interface**: Easy-to-use command-line interface.
- **Robustness**: 100% test coverage ensuring reliability.

## Prerequisites

- Python 3.9+
- Google Gemini API Key (Get one from [Google AI Studio](https://aistudio.google.com/))
- `ffmpeg` (Required by `moviepy` and `pydub`)

## Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/CiaranMccarthy1/reddit_story.git
    cd reddit_story
    ```

2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up Environment Variables**:
    - Copy the template file:
      ```bash
      cp .env.template .env
      ```
    - Open `.env` and paste your API key:
      ```
      GEMINI_API_KEY=your_actual_api_key_here
      ```

4.  **Prepare Assets**:
    - Place background videos (MP4) in `assets/`.
    - (Optional) Verify fonts are available on your system (default uses "Arial").

## Usage

Run the generator by providing a prompt file (text file containing the story or topic):

```bash
python main.py Prompts/AITA.txt
```

You can also specify the target duration in seconds (default is 60s):
```bash
python main.py Prompts/AITA.txt --duration 90
```

### Output
Generated videos will be saved in `outputFile/finalVideo/` with a timestamped filename (e.g., `video_20231027_123456.mp4`).

## Testing

The project includes a comprehensive test suite with 100% code coverage.

Run tests:
```bash
pytest
```

## Structure

- `src/cli.py`: Main entry point and CLI logic.
- `src/generator/`: Core components.
    - `content_fetcher.py`: AI text generation.
    - `script_builder.py`: Parsing and timestamping scripts.
    - `audio_generator.py`: TTS generation.
    - `video_generator.py`: Video editing and composition.
    - `asset_manager.py`: File path management.
    - `pipeline.py`: Orchestrates the entire flow.
- `tests/`: Unit and integration tests.
