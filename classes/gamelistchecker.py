from classes.gamelist import Gamelist
from classes.gamesystem import GameSystem
import os
import classes.utils as utils
from glob import glob

class GamelistChecker:
    def __init__(self, gamelist: Gamelist, gamesystem: GameSystem):
        self._gamelist = gamelist
        self._gamesystem = gamesystem
        self._files = {}

        return


    def _get_romfiles(self):
        roms = self._gamelist.get_roms()
        directories_processed = []
        files = []
        for rom in roms:
            long_rom = utils.get_system_longname(self._gamelist.system, rom)
            if os.path.isdir(long_rom):
                if long_rom not in files:
                    files.append(long_rom)
            else:
                directory = utils.get_path(long_rom)
                if directory in directories_processed:
                    continue

                for filetype in self._gamesystem.filetypes:
                    directory_files = glob(f"{directory}/*{filetype}")
                    if len(directory_files) > 0:
                        files.extend(directory_files)
                directories_processed.append(directory)

        self._files["roms"] = [files, []]

        return
    

    def _get_mediafiles(self, fields: list):
        medias = self._gamelist.get_mediadirs(fields)

        directories_processed = []
        files = []
        for media in medias.keys():
            directories = medias[media]
            for directory in directories:
                long_directory = utils.get_system_longname(self._gamelist._system, directory)
                if long_directory in directories_processed:
                    continue
                directory_files = glob(f"{long_directory}/*")
                for directory_file in directory_files:
                    if os.path.isfile(directory_file):
                        files.append(directory_file)

                directories_processed.append(long_directory)

            self._files[media] = [files, []]           

        return True
    

    def process(self, fields: list):
        games = self._gamelist.get_games(["system", "name", "path"] + fields)
        self._get_romfiles()
        self._get_mediafiles(fields)

        return