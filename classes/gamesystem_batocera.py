import re
import os
from gamesystem import GameSystem

class BatoceraGameSystem(GameSystem):
    def __init__(self, system: str):
        super().__init__(system)
        self._filetypes = self._get_filetypes()
        print(self._filetypes)


    def _get_filetypes(self):
        file_types = []
        info_file = f"/userdata/roms/{self._system}/_info.txt"
        if os.path.exists(info_file) and os.path.isfile(info_file):
            with open(info_file, 'r') as configfile:
                lines = configfile.readlines()
                for line in lines:
                    # i am not sure whether " or ' is allowed, so i will check for both
                    line_list = re.findall(r'"([^"]*)"', line)
                    if len(line_list) == 1:
                        items = line_list[0].split(" ")
                        for item in items:
                            if len(item.strip()) > 0:
                                if item.strip() not in file_types:
                                    file_types.append(item.strip())
                    line_list = re.findall(r"'([^']*)'", line)
                    if len(line_list) == 1:
                        items = line_list[0].split(" ")
                        for item in items:
                            if len(item.strip()) > 0:
                                if item.strip() not in file_types:
                                    file_types.append(item.strip())

        return file_types