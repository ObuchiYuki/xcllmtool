import unittest
import json
from typing import cast

from xcstrings import XCStrings, XCStringUnit, XCStringDeviceVariation, XCStringEntry
from util.logger import Logger

class TestXCStrings(unittest.TestCase):
    def test_list_keypath(self):
        sample_json = """
        {
            "sourceLanguage": "en",
            "version": "1.0",
            "strings" : {
                "title" : {
                    "localizations" : {
                        "en" : { "stringUnit" : { "state" : "translated", "value" : "Title" } },
                        "ja" : { "variations" : { "device" : { 
                            "iPhone" : { "stringUnit": { "state" : "translated", "value" : "タイトル 1" } },
                            "iPad" : { "stringUnit":  { "state" : "translated", "value" : "タイトル 2" } } 
                        }}}
                    }
                }
            }
        }
        """

        xcstrings = XCStrings.from_json(sample_json)
        keypathes = list(xcstrings.list_keys())

        self.assertEqual(len(keypathes), 3)
        
        en_key = keypathes[0]
        self.assertEqual(en_key.key, "title")
        self.assertEqual(en_key.locale, "en")
        self.assertEqual(en_key.device, None)

        ja_iphone_key = keypathes[1]
        self.assertEqual(ja_iphone_key.key, "title")
        self.assertEqual(ja_iphone_key.locale, "ja")
        self.assertEqual(ja_iphone_key.device, "iPhone")

        ja_ipad_key = keypathes[2]
        self.assertEqual(ja_ipad_key.key, "title")
        self.assertEqual(ja_ipad_key.locale, "ja")
        self.assertEqual(ja_ipad_key.device, "iPad")      

    def test_load_from_json(self):
        sample_json = """
        {
            "sourceLanguage": "en",
            "version": "1.0",
            "strings" : {
                "title" : {
                    "localizations" : {
                        "en" : { "stringUnit" : { "state" : "translated", "value" : "Title" } },
                        "ja" : { "stringUnit" : { "state" : "translated", "value" : "タイトル" } }
                    }
                }
            }
        }
        """

        xcstrings = XCStrings.from_json(sample_json)

        self.assertEqual(xcstrings.source_language, "en")
        self.assertEqual(len(xcstrings.strings), 1)
        self.assertIn("title", xcstrings.strings)

        title = xcstrings.strings["title"]
        self.assertEqual(title.extraction_state, None)
        self.assertEqual(len(title.localizations), 2)
        self.assertIn("en", title.localizations)

        en = title.localizations["en"]

        self.assertTrue(isinstance(en, XCStringUnit))
        en_unit: XCStringUnit = cast(XCStringUnit, en)

        self.assertEqual(en_unit.state, "translated")
        self.assertEqual(en_unit.value, "Title")

        jp = title.localizations["ja"]
        self.assertTrue(isinstance(jp, XCStringUnit))
        jp_unit: XCStringUnit = cast(XCStringUnit, jp)

        self.assertEqual(jp_unit.state, "translated")
        self.assertEqual(jp_unit.value, "タイトル")

    def test_load_from_json_with_device_variation(self):
        sample_json = """
        {
            "sourceLanguage": "en",
            "version": "1.0",
            "strings" : {
                "title" : {
                    "localizations" : {
                        "en" : { "stringUnit" : { "state" : "translated", "value" : "Title" } },
                        "ja" : { "variations" : { 
                            "device" : {
                                "iphone" : { "stringUnit" : { "state" : "needs_review", "value" : "KURURI KI" } },
                                "other" : { "stringUnit" : { "state" : "needs_review", "value" : "KURURI KI" } }
                            }
                        }}
                    }
                }
            }
        }
        """

        xcstrings = XCStrings.from_json(sample_json)

        self.assertEqual(xcstrings.source_language, "en")
        self.assertEqual(len(xcstrings.strings), 1)
        self.assertIn("title", xcstrings.strings)

        title = xcstrings.strings["title"]
        self.assertEqual(title.extraction_state, None)
        self.assertEqual(len(title.localizations), 2)
        self.assertIn("en", title.localizations)

        en = title.localizations["en"]

        self.assertTrue(isinstance(en, XCStringUnit))
        en_unit: XCStringUnit = cast(XCStringUnit, en)

        self.assertEqual(en_unit.state, "translated")
        self.assertEqual(en_unit.value, "Title")

        jp = title.localizations["ja"]
        self.assertTrue(isinstance(jp, XCStringDeviceVariation))
        jp_variation: XCStringDeviceVariation = cast(XCStringDeviceVariation, jp)

        self.assertEqual(len(jp_variation.devices), 2)
        self.assertIn("iphone", jp_variation.devices)
        self.assertIn("other", jp_variation.devices)

        iphone = jp_variation.devices["iphone"]
        self.assertTrue(isinstance(iphone, XCStringUnit))
        iphone_unit: XCStringUnit = cast(XCStringUnit, iphone)

        self.assertEqual(iphone_unit.state, "needs_review")
        self.assertEqual(iphone_unit.value, "KURURI KI")

        other = jp_variation.devices["other"]
        self.assertTrue(isinstance(other, XCStringUnit))
        other_unit: XCStringUnit = cast(XCStringUnit, other)
        self.assertEqual(other_unit.state, "needs_review")
        self.assertEqual(other_unit.value, "KURURI KI")

        
        
if __name__ == '__main__':
    unittest.main()