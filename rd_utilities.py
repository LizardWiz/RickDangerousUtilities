import classes.utils as utils

gamesystem = utils.get_gamesystem("atari2600")
gamelist = utils.get_gamelist("/userdata/roms/atari2600/gamelist.xml")
gamelist.save("/userdata/roms/atari2600/gamelist-testing.xml")
gamelist_checker = utils.get_gamelistchecker(gamelist, gamesystem)

gamelist_checker.process(["image", "marquee", "video"])