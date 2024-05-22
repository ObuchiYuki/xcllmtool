import re
import typing
from pathlib import Path

T = typing.TypeVar('T', str, int, Path)

def natural_sorted(lst: list[T]) -> list[T]:
    """
    Returns a sorted list of strings in a natural order, handling both zero-padded and non-zero-padded numbers,
    as well as strings without any numbers.
    """
    def convert(text):
        return int(text) if text.isdigit() else text.lower()
    
    def alphanum_key(key):
        key = str(key)
        return [convert(c) for c in re.split('([0-9]+)', key)]
    
    
    return sorted(lst, key=alphanum_key)

def natural_sort(lst: list[T]) -> None:
  """
  Sorts a list of strings in a natural order, handling both zero-padded and non-zero-padded numbers,
  as well as strings without any numbers.
  """
  def convert(text):
      return int(text) if text.isdigit() else text.lower()

  def alphanum_key(key):
      key = str(key)
      return [convert(c) for c in re.split('([0-9]+)', key)]

  
  lst.sort(key=alphanum_key)
