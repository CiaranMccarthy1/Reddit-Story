

import unittest
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path
import argparse

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.cli import main

class TestCLI(unittest.TestCase):
    
    @patch('src.cli.VideoGenerationPipeline')
    @patch('src.cli.AssetManager')
    @patch('src.cli.build_generator')
    @patch('src.cli.load_config')
    @patch('src.cli.ScriptBuilder')
    @patch('src.cli.AudioGenerator')
    @patch('src.cli.VideoGenerator')
    @patch('argparse.ArgumentParser.parse_args')
    def test_main_success(self, MockParseArgs, MockVideoGen, MockAudioGen, MockScriptBuilder,
                          MockLoadConfig, MockBuildGenerator, MockAssetManager, MockPipeline):
        # Setup arguments
        MockParseArgs.return_value = argparse.Namespace(
            prompt_file='test_prompt.txt', duration=120, provider=None, model=None, config=None
        )
        
        # Run main
        main()
        
        # Verify config loaded and generator built
        MockLoadConfig.assert_called_once()
        MockBuildGenerator.assert_called_once_with(MockLoadConfig.return_value)
        
        # Verify components initialized
        MockAssetManager.assert_called()
        MockScriptBuilder.assert_called()
        MockAudioGen.assert_called()
        MockVideoGen.assert_called()
        
        # Verify pipeline run
        mock_pipeline_instance = MockPipeline.return_value
        mock_pipeline_instance.run.assert_called_with('test_prompt.txt', duration=120)

    @patch('src.cli.build_generator')
    @patch('src.cli.load_config')
    @patch('argparse.ArgumentParser.parse_args')
    def test_main_cli_flags_passed_to_load_config(self, MockParseArgs, MockLoadConfig, MockBuildGenerator):
        MockParseArgs.return_value = argparse.Namespace(
            prompt_file='p.txt', duration=60, provider='openrouter', model='anthropic/claude', config='custom.toml'
        )

        with patch('src.cli.AssetManager'), \
             patch('src.cli.ScriptBuilder'), \
             patch('src.cli.AudioGenerator'), \
             patch('src.cli.VideoGenerator'), \
             patch('src.cli.VideoGenerationPipeline'):
            main()

        MockLoadConfig.assert_called_once_with(
            project_root=unittest.mock.ANY,
            config_path='custom.toml',
            provider='openrouter',
            model='anthropic/claude',
        )

    @patch('argparse.ArgumentParser.parse_args')
    def test_main_failure(self, MockParseArgs):
        # Simulate error
        MockParseArgs.side_effect = Exception("Argument Error")
        
        with self.assertRaises(SystemExit) as cm:
             main()
        
        self.assertEqual(cm.exception.code, 1)
