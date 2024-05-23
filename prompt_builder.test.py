import unittest
import json
from typing import cast

from xcstrings import XCStrings, XCStringUnit, XCStringDeviceVariation, XCStringEntry
from prompt_builder import PromptBuilderConfig, PromptBuilder, PromptBulderIterator
from util.logger import Logger

class TestPromptBuilder(unittest.TestCase):
    def test_prompt_builder(self):
        sample_json = """
        {
            "sourceLanguage": "en",
            "strings" : {
                "title" : {
                    "localizations" : {
                        "en" : { "stringUnit" : { "state" : "translated", "value" : "Title" } },
                        "ja" : { "variations" : { "device" : { 
                            "iPhone" : { "state" : "translated", "value" : "タイトル 1" },
                            "iPad" : { "state" : "translated", "value" : "タイトル 2" }
                        } } }
                    }
                }
            }
        }
        """

        xcstrings = XCStrings.from_json(json.loads(sample_json), logger=Logger())

        config = PromptBuilderConfig(
            system_prompt="System Prompt", 
            batch_char_limit=100, 
            source_locale="en",
            target_locale="ja",
            source_device=None,
            separator="\n----\n",
            prefix="- "
        )

        prompt_builder = PromptBuilder(xcstrings, config) 

        for batch in prompt_builder:
            print(batch)


if __name__ == '__main__':
    unittest.main()