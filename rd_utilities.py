import zipimport
import sys
import utils as utils
import platform
from availableupdates import AvailableUpdates
from gamelist import Gamelist
if platform.uname()[1] == "BATOCERA":
    from gamesystem import BatoceraGameSystem as GameSystem
else:
    from gamesystem import GameSystem as GameSystem

print(sys.path)
sys.path.insert(0, './packages')
