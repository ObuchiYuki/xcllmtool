import openai
from dataclasses import dataclass
from xcstrings import XCStrings, XCStringKeyPath
from prompt_builder import PromptBuilderConfig, PromptBuilder, PromptBulderIterator
from util.logger import Logger
import pandas as pd
import json
from tqdm import tqdm

@dataclass
class TranslatorConfig:
    api_key: str
    model: str
    source_locale: str
    target_locale: str
    batch_char_limit: int
    retry_limit: int = 3

@dataclass
class TranslationResult:
    source_keypath: XCStringKeyPath
    target_keypath: XCStringKeyPath
    translation: str

class Translator:
    config: TranslatorConfig
    logger: Logger

    def __init__(self, config: TranslatorConfig, logger: Logger):
        self.config = config
        self.logger = logger

        openai.OpenAI(
            api_key=config.api_key
        )

    def translate(self, xcstrings: XCStrings):
        prompt_builder = PromptBuilder(
            xcstrings=xcstrings,
            config=PromptBuilderConfig(
                system_prompt=self._build_system_prompt(target_locale=self.config.target_locale),
                source_locale=self.config.source_locale,
                source_device=None,
                target_locale=self.config.target_locale,
                batch_char_limit=self.config.batch_char_limit,
                separator="\n",
                prefix="- "
            )
        )

        translations: list[TranslationResult] = []

        with tqdm(total=len(prompt_builder.keys)) as pbar:
            for message_batch in prompt_builder:
                # print([key.key for key in message_batch.keys])
                
                successed = False
                for i in range(self.config.retry_limit):
                    response = openai.chat.completions.create(
                        model=self.config.model,
                        messages=message_batch.messages
                    )
                    content = response.choices[0].message.content
                    if content is None:
                        continue

                    contents = self.parse_translation_content(content)
                    
                    if not len(contents) == len(message_batch.keys):
                        self.logger.warn(f"Number of translations does not match the number of keys. Retrying... (Attempt {i+1}/{self.config.retry_limit})")
                        continue
                    
                    for source_key, translation in zip(message_batch.keys, contents):
                        target_key = source_key.with_locale(self.config.target_locale)
                        translations.append(TranslationResult(
                            source_keypath=source_key,
                            target_keypath=target_key,
                            translation=translation
                        ))
                        successed = True
                    
                    if successed:
                        break
                
                if not successed:
                    raise Exception("Failed to translate keys after retrying.")
                
                pbar.update(len(message_batch.keys))

        return translations


    def parse_translation_content(self, content: str) -> list[str]:
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]

        content = content.strip()
        content = "\n" + content + "\n"

        translations = content.split("\n- ")
        
        return [translation.strip() for translation in translations if translation.strip() != ""]


    def _build_system_prompt(self, target_locale: str) -> str:
        locale_support = self._get_locale_support(target_locale)
        if locale_support is None:
            return self._build_generic_prompt(target_locale)
        
        language_name, sample_translation = locale_support
        
        return f"""
        Translate the following app strings into '{language_name}'. The input will be given in bullet point format.

        ```
        - Welcome to App
        - Select All
        ```

        The output should be in bullet point format. Do not output anything other than the translated text. 

        ```
        {sample_translation}
        ```
        """
    
    def _build_generic_prompt(self, target_locale: str):
        return f"""
        Translate the following app strings into locale code '{target_locale}'. The input will be given in bullet point format.

        ```
        - Welcome to App
        - Select All
        ```

        The output should be in bullet point format. Do not output anything other than the translated text. 
        For example, for a translation into Japanese, the result will be as follows.

        ```
        - アプリへようこそ
        - すべてを選択
        ```
        """
        
    
    def _get_locale_support(self, locale: str) -> tuple[str, str] | None:
        try:
            language_name: str
            sample_translation: str
            with open(f'locale_support/{locale}.json', 'r') as f:
                json_data = json.load(f)
                language_name = json_data['language']
                sample_translation = json_data['sample']
            
            return language_name, sample_translation
        except:
            return None


