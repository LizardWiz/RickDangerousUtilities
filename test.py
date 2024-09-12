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
from mega import Mega


gamelist = Gamelist("/userdata/roms/atari2600/gamelist.xml", overwrite=True)
merge_gamelist = Gamelist("/tmp/improvements/atari2600/gamelist.xml")
gamelist.merge(merge_gamelist)
merge_gamelist.save()

available_updates = AvailableUpdates("https://mega.nz/folder/yDAliCBL#ex6Y7QagY_4hu0kUfu35jQ/file/bChAhCJS")
mega = Mega()
m = mega.login()
quota = m.get_quota()



a = m.download_found("bChAhCJS", (414480369, 126552955, 1899763079, 2856319759), dest_path="/tmp/improvements", folder="yDAliCBL")

