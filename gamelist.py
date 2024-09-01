import xml.etree.ElementTree as ET
import utils

class GameList:
    def __init__(self, gamelist=None):
        self._fields = ["name", "desc", "image", "rating", "releasedate", "developer", "publisher", "genre", "players", "playcount", "lastplayed", "favorite"] 
        self._do_not_overwrite = ["playcount", "lastplayed", "favorite"]
        self._path = gamelist if gamelist else None
        self._system = self._get_system(gamelist) if gamelist else None
        if gamelist is None:
            self._gamelist = None
        else:
            self.parse(gamelist)


    def _get_system(self, path: str):
        parts = path.split("/")
        if len(parts) <= 2:
            return None
        if parts(len(parts) - 1) != "gamelist.xml":
            return None
        
        return parts(len(parts) - 2)
    

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
            # get game attributes
            attributes = {}
            for attribute in src_game:
                if attribute.text is not None:
                    attributes[attribute.tag] = attribute.text
            # now write sorted attributes
            game = ET.Element("game")
            for field in self._fields:
                if field in attributes.keys():
                    elem = ET.SubElement(game, field)
                    elem.text = attributes[field]
                    del attributes[field]
            # sort the rest
            for field in sorted(attributes.keys()):
                elem = ET.SubElement(game, field)
                elem.text = attributes[field]

            dest_root.append(game)                    

            self._gamelist = ET.ElementTree(dest_root)

        return 


    def save(self):
        file_time = utils.safe_write_backup(self._path)

        self._indent(space="\t", level=0)
        with open(self._path, "wb") as fh:
            self._gamelist.write(fh, "utf-8")

        return utils.safe_write_check(self._path, file_time)
    

    def merg(self, merge_xml: ET.ElementTree):
        return
    

    def get_games(self, fields: list):
        games_list = []
        root = self._gamelist.getroot()

        games = [elem for elem in root if elem.tag == "game"]
        for game in game:
            game_list = []
            for field in field:
                game_field = game.find(field)
                if game_field:
                    game_list.append(game_field.text)
                else:
                    game_list.append("")

            games_list.append(game_list)

        return games_list
    

    def get_xml(self):
        return self._gamelist