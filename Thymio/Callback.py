from typing import Callable, Dict, Any
from tdmclient import ClientAsyncCacheNode


class Callback:
    def __init__(self, fn: Callable[[ClientAsyncCacheNode, Dict], Any], variable_keys: set[str]):
        self.fn = fn
        self.variable_keys = variable_keys
