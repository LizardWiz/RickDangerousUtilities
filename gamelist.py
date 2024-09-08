import xml.etree.ElementTree as ET
import utils as utils

class Gamelist:
    def __init__(self, gamelist=None, overwrite=False):
        self._fields = ["name", "path", "desc", "image", "rating", "releasedate", "developer", "publisher", "genre", "players", "playcount", "lastplayed", "favorite"] 
        self._do_not_overwrite = ["playcount", "lastplayed", "favorite"]
        self._overwrite = overwrite
        self._path = gamelist if gamelist else None
        self._system = self._get_system(gamelist) if gamelist is not None else None
        if gamelist is None:
            self._gamelist = None
        else:
            self.parse(gamelist)


    @property
    def system(self):
        return self._system
    
    @property
    def gamelist(self):
        return self._gamelist
    
    @gamelist.setter
    def gamelist(self, value):
        self._gamelist = value


    def _get_system(self, path: str):
        parts = path.split("/")
        if len(parts) <= 2:
            return None
        if parts[len(parts) - 1] != "gamelist.xml":
            return None
        
        return parts[len(parts) - 2]
    

    def _indent(self, space="  ", level=0):
        # Reduce the memory consumption by reusing indentation strings.
        indentations = ["\n" + level * space]

        def _indent_children(elem, level):
            # Start a new indentation level for the first child.
            child_level = level + 1
            try:
                child_indentation = indentations[child_level]
            except IndexError:
                child_indentation = indentations[level] + space
                indentations.append(child_indentation)

            if not elem.text or not elem.text.strip():
                elem.text = child_indentation

            for child in elem:
                if len(child):
                    _indent_children(child, child_level)
                if not child.tail or not child.tail.strip():
                    child.tail = child_indentation
                if child == elem[len(elem) - 1]:
                    child.tail = indentations[level]

        _indent_children(self._gamelist.getroot(), 0)
    
    
    def sort(self):
        # this will sort the game entries by desc
        games_list = {}
        src_root = self._gamelist.getroot()

        children = [elem for elem in src_root if elem.tag == "game"]
        for child in children:
            game = child.find("name")
            path = child.find("path")
            if game.text is not None:
                if path.text is not None:
                    games_list[game.text.lower() + "-" + path.text.lower()] = ET.tostring(child)

        for child in children:
            del src_root[child]

        for game in sorted(games_list.keys()):
            src_root.append(ET.fromstring(game))

        return
    

    def _sort_elements(self, game: ET.Element, overwrite=False):
        # get game attributes
        elements = {}
        all = []
        for element in game:
            all.append(element.tag)
            if element.text is not None:
                if not self._overwrite and element.tag in self._do_not_overwrite:
                    continue
                elements[element.tag] = element.text
        for element in all:
            nodes = game.findall(element)
            for node in nodes:
                game.remove(node)

        # now write sorted attributes
        for field in self._fields:
            if field in elements.keys():
                ET.SubElement(game, field).text = elements[field]
                del elements[field]
        # sort the rest
        for field in sorted(elements.keys()):
            ET.SubElement(game, field).text = elements[field]

        return game
    

    def parse(self, gamelist: str):
        # this will produce a gamelist with ordered elements
        self._system = self._get_system(gamelist)
        self._path = gamelist
        src_tree = ET.parse(gamelist)
        src_root = src_tree.getroot()

        dest_root = ET.Element("gamelist")

        # get non game elements
        children = [elem for elem in src_root if elem.tag != "game"]
        for child in children:
            dest_root.append(child)

        # now get game elements
        games = [elem for elem in src_root if elem.tag == "game"]
        for src_game in games:
            path = src_game.find("path")
            if path is None:
                continue
            if path.text is None:
                continue
            
            game = self._sort_elements(src_game)
            dest_root.append(game)

        self._gamelist = ET.ElementTree(dest_root)

        return 


    def save(self, filename=None):
        if filename is None:
            filename = self._path
        file_time = utils.safe_write_backup(filename)

        self._indent(space="\t", level=0)
        with open(filename, "wb") as fh:
            self._gamelist.write(fh, "utf-8")

        return utils.safe_write_check(filename, file_time)
    

    def merge(self, merge_gamelist: 'Gamelist'):
        root = self._gamelist.getroot()
        merge_root = merge_gamelist.gamelist.getroot()
        merge_games = [elem for elem in merge_root if elem.tag == "game"]
        for merge_game in merge_games:
            path = merge_game.find("path")
            if path is not None:
                if path.text is None:
                    continue         

            game = root.find(f".//game[path=\"{path.text}\"]")
            if game is None:
                root.append(merge_game)
                continue

            for attribute in merge_game.attrib:
                game.set(attribute, merge_game.get(attribute))

            for merge_element in merge_game:
                element = game.find(merge_element.tag)
                if element is None:
                    game.append(merge_element)
                    continue

                element.text = merge_element.text

        merge_gamelist.gamelist = self._gamelist

        return
    

    def get_games(self, fields: list):
        games_list = []
        root = self._gamelist.getroot()

        games = [elem for elem in root if elem.tag == "game"]
        for game in games:
            game_list = []
            for field in fields:
                if field == "system":
                    game_list.append(self._system)
                    continue
                game_field = game.find(field)
                if game_field is not None:
                    game_list.append(game_field.text)
                else:
                    game_list.append("")

            games_list.append(game_list)

        return games_list
    

    def get_mediadirs(self, media_types: list):
        media = {}
        for media_type in media_types:
            paths = []
            elements = self._gamelist.findall(f"./game/{media_type}")
            for element in elements:
                if element.text is None or element.text.strip() == "":
                    continue
                path = utils.get_path(utils.get_system_shortname(self._system, element.text))
                if path not in paths:
                    paths.append(path)
            if len(paths) > 0:
                media[media_type] = paths

        return media
    
    def get_roms(self):
        roms = []
        elements = self._gamelist.findall(f"./game/path")
        for element in elements:
            rom = utils.get_system_shortname(self._system, element.text)
            if element not in roms:
                roms.append(rom)

        return roms