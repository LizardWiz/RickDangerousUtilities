from datetime import datetime, timezone
import shutil
import os
from .gamesystem import BatoceraGameSystem
from .gamelist import Gamelist
from .gamelistchecker import GamelistChecker

def get_gamesystem(system: str):
    return BatoceraGameSystem(system)


def get_gamelist(system: str):
    return Gamelist(gamelist=system)


def get_gamelistchecker(gamelist: Gamelist, gamesystem: BatoceraGameSystem):
    return GamelistChecker(gamelist, gamesystem)


def safe_write_check(file_path: str, file_time: str):
    if os.path.exists(file_path + "--" + file_time) and os.path.isfile(file_path + "--" + file_time):
        if os.path.getsize(file_path) == 0:
            # this somehow failed badly
            shutil.copy2(file_path + "--" + file_time, file_path)
            return False

        os.remove(file_path + "--" + file_time)

    return True


def safe_write_backup(file_path: str, file_time=""):
    if file_time == "":
        file_time = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")

    if os.path.exists(file_path) and os.path.isfile(file_path):
        shutil.copy2(file_path, file_path + "--" + file_time)

    return file_time


def get_path(file: str):
    return os.path.dirname(file)


def get_system_longname(system: str, path: str):
    # todo: create ini class
    return path.replace("./", f"/userdata/roms/{system}/")


def get_system_shortname(system: str, path: str):
    # todo: create ini class
    return path.replace(f"/userdata/roms/{system}", "./")
