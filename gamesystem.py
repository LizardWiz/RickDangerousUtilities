import re
import os

class GameSystem:
    def __init__(self, system: str):
        self._system = system
        self._filetypes = None


    @property
    def system(self):
        return self._system
   