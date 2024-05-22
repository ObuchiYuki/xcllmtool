from dataclasses import dataclass
from collections import deque
from xcstrings import XCStrings, XCStringKeyPath
from openai.types.chat import ChatCompletionMessageParam

@dataclass
class PromptBuilderConfig:
    system_prompt: str
    source_locale: str
    source_device: str | None 
    target_locale: str
    batch_char_limit: int
    separator: str
    prefix: str | None = None

@dataclass
class PromptBatch:
    keys: list[XCStringKeyPath]
    messages: list[ChatCompletionMessageParam]

class PromptBulderIterator:
    xcstrings: XCStrings
    keys: deque[XCStringKeyPath]
    config: PromptBuilderConfig

    def __init__(self, xcstrings: XCStrings, keys: list[XCStringKeyPath], config: PromptBuilderConfig):
        self.xcstrings = xcstrings
        self.keys = deque(keys)
        self.config = config

    def __next__(self) -> PromptBatch:
        if len(self.keys) == 0:
            raise StopIteration
        
        chats: list[ChatCompletionMessageParam] = [
            { "role": "system", "content": self.config.system_prompt }
        ]
        char_count = len(self.config.system_prompt)
        user_message = ""
        is_first = True

        keys: list[XCStringKeyPath] = []
        while char_count < self.config.batch_char_limit and len(self.keys) > 0:
            key = self.keys.pop()
            keys.append(key)
            value = self.xcstrings.get(key)
            if value is not None:
                if not is_first:
                    user_message += self.config.separator
                    char_count += len(self.config.separator)
                else:
                    is_first = False
                if self.config.prefix is not None:
                    user_message += self.config.prefix
                    char_count += len(self.config.prefix)
                user_message += value
                char_count += len(value)
        
        chats.append({ "role": "user", "content": user_message })

        return PromptBatch(keys=keys, messages=chats)

class PromptBuilder:
    xcstrings: XCStrings
    keys: list[XCStringKeyPath]
    config: PromptBuilderConfig

    def __init__(self, xcstrings: XCStrings, config: PromptBuilderConfig):
        self.xcstrings = xcstrings
        self.keys = list(xcstrings.list_keys(locale=config.source_locale, device=config.source_device))
        self.config = config
        
        self.keys = self._filter_keys(self.keys)

    def _filter_keys(self, keys: list[XCStringKeyPath]) -> list[XCStringKeyPath]:
        new_keys = []

        for key in keys:
            key_for_target = key.with_locale(self.config.target_locale)
            if not self.xcstrings.has_entry(key_for_target):
                new_keys.append(key)

        return new_keys

    def __iter__(self) -> PromptBulderIterator:
        return PromptBulderIterator(self.xcstrings, self.keys, self.config)