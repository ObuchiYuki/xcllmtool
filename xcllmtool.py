import sys
from argparse import ArgumentParser
from pathlib import Path

from util.logger import Logger, cast_logging_level

from translator import Translator, TranslatorConfig
from xcstrings import XCStrings

class XCLLMTool:
    def __init__(self):
        parser = ArgumentParser(description="Xcode Localization Management Tool")

        parser.add_argument("input", type=str, help="Source file")
        parser.add_argument("--api-key", required=True, type=str, help="OpenAI API Key")
        parser.add_argument("-s", "--source", required=True, type=str, help="Source locale")
        parser.add_argument("-t", "--target", required=True, type=str, help="Target locale")
        parser.add_argument("-m", "--model", default="gpt-4-turbo", type=str, help="GPT model")
        parser.add_argument("-b", "--batch-size", default=1000, type=int, help="Batch character limit")
        parser.add_argument("-r", "--retry", default=3, type=int, help="Retry limit")
        parser.add_argument("-l", "--log", default="info", type=str, help="Log level")
        parser.add_argument("--override", default=False, action="store_true", help="Override existing translations")
        parser.add_argument("-o", "--output", default=None, type=str, help="Output file (default: [source].translated.xcstrings)")

        self.parser = parser

    def run(self, varg: list[str]):
        logger = Logger(prefix="xcllmtool")
        try:
            args = self.parser.parse_args(varg)

            log = cast_logging_level(args.log)
            
            if log is None or not isinstance(log, str):
                raise ValueError("Log level must be a string")
            
            logger.logging_level = log
            
            source_path = Path(args.input)
            if not source_path.exists():
                raise FileNotFoundError(f"File not found: {source_path}")
            
            api_key = args.api_key
            if api_key is None or not isinstance(api_key, str):
                raise ValueError("API Key must be a string")
            
            source_locale = args.source
            if source_locale is None or not isinstance(source_locale, str):
                raise ValueError("Source locale must be a string")
            
            target_locale = args.target
            if target_locale is None or not isinstance(target_locale, str):
                raise ValueError("Target locale must be a string")
            
            model = args.model
            if model is None or not isinstance(model, str):
                raise ValueError("Model must be a string")
            
            batch_size = args.batch_size
            if batch_size is None or not isinstance(batch_size, int):
                raise ValueError("Batch size must be an integer")
            
            retry = args.retry
            if retry is None or not isinstance(retry, int):
                raise ValueError("Retry limit must be an integer")
            
            override = args.override or False
            output = Path(args.output) if args.output is not None else None
            if override:
                output = source_path
                
            if output is None:
                output = source_path.with_suffix(".translated.xcstrings")

            config = TranslatorConfig(
                api_key=api_key,
                model=model,
                source_locale=source_locale,
                target_locale=target_locale,
                batch_char_limit=batch_size,
                retry_limit=retry
            )

            translator = Translator(config=config, logger=logger)
            xcstrings = XCStrings.load_from_path(source_path, logger=logger)
            results = translator.translate(xcstrings)

            for result in results:
                xcstrings.set(result.target_keypath, result.translation)

            self._write_results(xcstrings, output, logger)

        except Exception as e:
            logger.exception(e)
            sys.exit(1)

    def _write_results(self, xcstrings: XCStrings, output: Path, logger: Logger):
        try:
            with open(output, "w") as f:
                f.write(xcstrings.to_json())
        except Exception as e:
            logger.error(str(e))
            sys.exit(1)

      