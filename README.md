# Reddit Story Generator

A fully automated pipeline to generate short-form video content from text prompts (e.g., Reddit stories) using AI-generated scripts, narration, and background video.

## Features

- **Content Generation**: Pluggable AI providers — Google Gemini (default), OpenAI, or OpenRouter — selected via `config.toml` or CLI flags.
- **Narration**: Generates voiceovers using `edge-tts`.
- **Video Composition**: Automatically edits background video, adds subtitles, and syncs audio using `moviepy`.
- **CLI Interface**: Easy-to-use command-line interface.
- **Robustness**: Retry logic for transient API errors and a comprehensive test suite.

## Prerequisites

- Python 3.9+ (3.11+ recommended; `tomli` backports TOML support below 3.11)
- An API key for at least one provider:
  - [Google AI Studio](https://aistudio.google.com/) (Gemini, default)
  - [OpenAI](https://platform.openai.com/)
  - [OpenRouter](https://openrouter.ai/)
- `ffmpeg` (Required by `moviepy`)

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
    - Paste the API key(s) for the provider(s) you plan to use:
      ```
      GEMINI_API_KEY=your_actual_api_key_here
      OPENAI_API_KEY=your_actual_api_key_here
      OPENROUTER_API_KEY=your_actual_api_key_here
      ```

4.  **(Optional) Configure the default provider**:
    - Copy the template and edit:
      ```bash
      cp config.template.toml config.toml
      ```
    - Choose the provider, model, and the env var name that holds its key. Defaults: `gemini` / `gemini-2.5-flash`.

5.  **Prepare Assets**:
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

Override the provider and/or model from `config.toml` on the command line:
```bash
python main.py Prompts/AITA.txt --provider openrouter --model anthropic/claude-sonnet-4
python main.py Prompts/AITA.txt --provider openai --model gpt-4o
```

Use a custom config file:
```bash
python main.py Prompts/AITA.txt --config my-config.toml
```

### Output
Generated videos will be saved in `outputFile/finalVideo/` with a timestamped filename (e.g., `video_20231027_123456.mp4`).

## Testing

The project includes a comprehensive test suite.

Run tests:
```bash
pytest
```

## Structure

- `src/cli.py`: Main entry point and CLI logic.
- `src/generator/`: Core components.
    - `providers/`: AI provider implementations (Gemini, OpenAI, OpenRouter) and factory.
    - `config.py`: TOML + environment configuration loading.
    - `script_builder.py`: Parsing and timestamping scripts.
    - `audio_generator.py`: TTS generation.
    - `video_generator.py`: Video editing and composition.
    - `text_renderer.py`: Caption image rendering.
    - `asset_manager.py`: File path management.
    - `pipeline.py`: Orchestrates the entire flow.
- `tests/`: Unit and integration tests.
