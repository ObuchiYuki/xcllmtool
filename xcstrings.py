import json
from os import PathLike
from dataclasses import dataclass
from typing import Literal, TypeAlias, Generator

from util.logger import Logger

XCStringUnitState: TypeAlias = Literal['translated', 'needs_review', "new"]

def cast_XCStringUnitState(value: str) -> XCStringUnitState:
    if value in ['translated', 'needs_review', 'new']:
        return value # type: ignore
    else:
        raise ValueError(f'Invalid value for XCStringUnitState: {value}')

XCStringExtractionState: TypeAlias = Literal['stale', "extracted_with_value", "manual"]

def cast_XCStringExtractionState(value: str) -> XCStringExtractionState:
    if value in ['stale', 'extracted_with_value', "manual"]:
        return value # type: ignore
    else:
        raise ValueError(f'Invalid value for XCStringExtractionState: {value}')

@dataclass
class XCStringUnit:
    value: str
    state: XCStringUnitState

    def to_dict(self) -> dict:
        return {
            "stringUnit": {
                "value": self.value,
                "state": self.state
            }
        }
    
    @staticmethod
    def can_from_dict(data: dict) -> bool:
        if "stringUnit" not in data:
            return False
        
        string_unit_data = data["stringUnit"]
        if not isinstance(string_unit_data, dict):
            return False
        
        if "state" not in string_unit_data:
            return False
        
        if "value" not in string_unit_data:
            return False
        
        return True

    @staticmethod
    def from_dict(data: dict) -> 'XCStringUnit':
        if "stringUnit" not in data:
            raise ValueError('stringUnit is required', data)
        
        string_unit_data = data.get("stringUnit", None)
        if not isinstance(string_unit_data, dict):
            raise ValueError('stringUnit must be a dictionary', data)
        
        state_data = string_unit_data.get("state", None)
        if not isinstance(state_data, str):
            raise ValueError('state must be a string', data)
        state = cast_XCStringUnitState(state_data)
    
        value_data = string_unit_data.get("value", None)
        if not isinstance(value_data, str):
            raise ValueError('value must be a string')
        
        return XCStringUnit(value_data, state)

@dataclass
class XCStringDeviceVariation:
    devices: dict[str, XCStringUnit]

    def to_dict(self) -> dict:
        return {
            "variations": {
                "device": {
                    device: variation.to_dict() for device, variation in self.devices.items()
                }
            }
        }

    @staticmethod
    def can_from_dict(data: dict) -> bool:
        if "variations" not in data:
            return False
        
        variations_data = data["variations"]
        if not isinstance(variations_data, dict):
            return False
        
        if "device" not in variations_data:
            return False
        
        return True

    @staticmethod
    def from_dict(data: dict) -> 'XCStringDeviceVariation':
        if "variations" not in data:
            raise ValueError('variations is required')
        
        variations_data = data["variations"]
        if not isinstance(variations_data, dict):
            raise ValueError('variations must be a dictionary')
        
        device_data = variations_data.get("device", None)   
        if not isinstance(device_data, dict):
            raise ValueError('device must be a dictionary')
        
        device: dict[str, XCStringUnit] = {}

        for device_name, variation_data in device_data.items():
            if not isinstance(variation_data, dict):
                raise ValueError('variation must be a dictionary')
            
            device[device_name] = XCStringUnit.from_dict(variation_data)

        return XCStringDeviceVariation(device)

@dataclass
class XCStringEntry:
    localizations: dict[str, XCStringUnit | XCStringDeviceVariation]
    extraction_state: XCStringExtractionState | None = None
    comment: str | None = None

    def to_dict(self) -> dict:
        return {
            "localizations": {
                locale: localization.to_dict() for locale, localization in self.localizations.items()
            },
            "extractionState": self.extraction_state,
            "comment": self.comment
        }

    @staticmethod
    def from_dict(data: dict, logger: Logger | None = None) -> 'XCStringEntry':
        localizations_data = data['localizations']
        if not isinstance(localizations_data, dict):
            raise ValueError('localizations must be a dictionary')
        
        extraction_state_data = data.get('extractionState', None)
        if extraction_state_data is not None and not isinstance(extraction_state_data, str):
            raise ValueError('extractionState must be a string or null')
        extraction_state = cast_XCStringExtractionState(extraction_state_data) if extraction_state_data is not None else None

        comment_data = data.get('comment', None)
        if comment_data is not None and not isinstance(comment_data, str):
            raise ValueError('comment must be a string or null')
    
        localizations: dict[str, XCStringUnit | XCStringDeviceVariation] = {}

        for locale, value in localizations_data.items():
            if not isinstance(value, dict):
                raise ValueError('localizations values must be dictionaries')
            
            if XCStringUnit.can_from_dict(value):
                localizations[locale] = XCStringUnit.from_dict(value)
            elif XCStringDeviceVariation.can_from_dict(value):
                localizations[locale] = XCStringDeviceVariation.from_dict(value)
            else:
                if logger is not None:
                    logger.warn(f'Unknown localization type for {locale}')

        return XCStringEntry(localizations=localizations, extraction_state=extraction_state, comment=comment_data)
    
@dataclass
class XCStringKeyPath:
    key: str
    locale: str
    device: str | None = None

    def with_locale(self, locale: str) -> 'XCStringKeyPath':
        return XCStringKeyPath(self.key, locale, self.device)
    
@dataclass
class XCStrings:
    source_language: str
    strings: dict[str, XCStringEntry]
    version: str

    def list_keys(self, key: str | None = None, locale: str | None = None, device: str | None = None) -> Generator[XCStringKeyPath, None, None]:
        keys = [key] if key is not None else self.strings.keys()

        for key in keys:
            entry = self.strings[key]
            locales = [locale] if locale is not None else entry.localizations.keys()
            for locale in locales:
                localization = entry.localizations[locale]
                if isinstance(localization, XCStringUnit):
                    yield XCStringKeyPath(key, locale)
                elif isinstance(localization, XCStringDeviceVariation):
                    devices = [device] if device is not None else localization.devices.keys()
                    for device in devices:
                        yield XCStringKeyPath(key, locale, device)

    def remove_locale(self, locale: str) -> None:
        for _, entry in self.strings.items():
            if locale in entry.localizations:
                del entry.localizations[locale]

    def has_entry(self, keypath: XCStringKeyPath) -> bool:
        if keypath.key not in self.strings:
            return False
        
        if keypath.locale not in self.strings[keypath.key].localizations:
            return False
        
        if keypath.device is None:
            return True
        else:
            return keypath.device in self.strings[keypath.key].localizations[keypath.locale].variations # type: ignore

    def get(self, keypath: XCStringKeyPath) -> str | None:
        if keypath.key not in self.strings:
            return None
        
        if keypath.locale not in self.strings[keypath.key].localizations:
            return None
        
        localization = self.strings[keypath.key].localizations[keypath.locale]
        if keypath.device is None:
            if not isinstance(localization, XCStringUnit):
                raise ValueError('No device variation must be get from a string unit')
            return localization.value
        else:
            if not isinstance(localization, XCStringDeviceVariation):
                raise ValueError('Device variation cannot be get from a string unit')
            if keypath.device not in localization.devices:
                return None
            return localization.devices[keypath.device].value

    def set(self, keypath: XCStringKeyPath, value: str | None = None, state: XCStringUnitState | None = None) -> None:
        # If the key doesn't exist, create it
        if keypath.key not in self.strings:
            self.strings[keypath.key] = XCStringEntry({
                keypath.locale: XCStringUnit(value or '', state or 'needs_review')
            })
        
        # If the locale doesn't exist, create it
        elif keypath.locale not in self.strings[keypath.key].localizations:
            self.strings[keypath.key].localizations[keypath.locale] = XCStringUnit(value or '', state or 'needs_review')
        
        # set the value and state
        elif keypath.device is None:
            localization = self.strings[keypath.key].localizations[keypath.locale]
            if not isinstance(localization, XCStringUnit):
                raise ValueError('Device variation must be set on a string unit')
            
            if value is not None:
                localization.value = value
            if state is not None:
                localization.state = state
        
        # set the value and state for a device variation
        elif keypath.device is not None:
            localization = self.strings[keypath.key].localizations[keypath.locale]
            if not isinstance(localization, XCStringDeviceVariation):
                raise ValueError('Device variation cannot be set on a string unit')
            
            if keypath.device not in localization.devices:
                localization.devices[keypath.device] = XCStringUnit(value or '', state or 'needs_review')
            else:
                if value is not None:
                    localization.devices[keypath.device].value = value
                if state is not None:
                    localization.devices[keypath.device].state = state

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    def to_dict(self) -> dict:
        return {
            "sourceLanguage": self.source_language,
            "strings": {
                key: entry.to_dict() for key, entry in self.strings.items()
            },
            "version": self.version
        }

    @staticmethod
    def from_dict(data: dict, logger: Logger | None = None) -> 'XCStrings':
        sourceLanguage: str
        strings: dict[str, XCStringEntry] = {}
        
        source_language_data = data.get("sourceLanguage", None)
        if not isinstance(source_language_data, str):
            raise ValueError('sourceLanguage must be a string')
        sourceLanguage = source_language_data

        strings_data = data.get('strings', None)
        if not isinstance(strings_data, dict):
            raise ValueError('strings must be a dictionary')

        for key, string in strings_data.items():
            strings[key] = XCStringEntry.from_dict(string, logger)

        version = data.get('version', None)
        if not isinstance(version, str):
            raise ValueError('version must be a string')

        return XCStrings(sourceLanguage, strings, version)

    @staticmethod
    def from_json(data: str, logger: Logger | None = None) -> 'XCStrings':
        return XCStrings.from_dict(json.loads(data), logger)

    @staticmethod
    def from_path(path: PathLike, logger: Logger | None = None) -> 'XCStrings':
        with open(path, 'r') as f:
            return XCStrings.from_dict(json.load(f), logger)
            
