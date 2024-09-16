import sys
sys.path.insert(0, './packages/')
from mega import Mega
from mega.crypto import base64_to_a32, base64_url_decode, decrypt_attr, decrypt_key, a32_to_str, get_chunks, str_to_a32
from mega.errors import RequestError

import requests
import json
import utils
import re
import os
from datetime import datetime, timezone
from inifile import IniFile


class AvailableUpdates:
    def __init__(self, mega=None, megadir=None, status=False, ini_file=None):
        self._mega = mega
        self._megadir = megadir
        self._dirs = {}
        self._updates = {}
        self._ini = None
        if self._megadir and ini_file:
            if type(ini_file) == "IniFile":
                self._ini.set_type("update")
                self._ini = self._get_mega_ini(megadir)
                self.get_available_updates(megadir, ini_file)

        return

    @property
    def ini(self):
        return self._ini
    
    @property
    def mega(self):
        return self._mega
    
    @mega.setter
    def mega(self, value):
        self._mega = value

    
    def _get_directory_type(self, parent: str):
        ret = "all"

        for key, val in self._dirs.items():
            if val != parent:
                continue
            ret = key
            break

        return ret
        

    def _get_mega_ini(self, megadir: str, ini_file: IniFile):
        parts = megadir.split("/")
        index = 0
        filename = ""
        for part in parts:
            if part == "folder":
                filename = parts[index + 1].split("#")[0] + ".ini"
                break
            
            index += 1

        if len(filename) > 0:
            if not os.path.isfile(filename):
                with open(filename, 'w') as file:
                    file.write("")

            return IniFile(filename)

        return None


    def _decrypt_node_key(self, key_str: str, shared_key: str):
        encrypted_key = base64_to_a32(key_str.split(":")[1])

        return decrypt_key(encrypted_key, shared_key)


    def _get_file_data(self, file_id: str):
        for key, value in self._updates.items():
            if value["file_id"] == file_id:
                return self._get_file_data_by_folder(file_id, value["root_folder"])
            
        return None


    def get_available_updates(self, megadrive: str, ini_file: 'IniFile', status=False):
        self._megadir = megadrive
        self._ini = self._get_mega_ini(megadrive, ini_file)
        self._ini.set_type("update")
        self._updates = {}
        if status == True:
            print()
            print("Finding available updates...")
        (root_folder, shared_enc_key) = self._parse_folder_url(megadrive)
        shared_key = base64_to_a32(shared_enc_key)
        nodes = self._get_nodes_in_shared_folder(root_folder)
        for node in nodes:
            key = self._decrypt_node_key(node["k"], shared_key)
            if node["t"] == 0:  # Is a file
                k = (key[0] ^ key[4], key[1] ^ key[5],
                    key[2] ^ key[6], key[3] ^ key[7])
            elif node["t"] == 1:  # Is a folder
                k = key
            attrs = decrypt_attr(base64_url_decode(node["a"]), k)
            file_name = attrs["n"]
            file_id = node["h"]
            parent = node["p"]
            modified_date = node["ts"]
            if node["t"] == 0:
                attributes = {}
                attributes["file_id"] = file_id
                attributes["modified_date"] = modified_date
                attributes["file_size"] = utils.convert_filesize(node["s"])
                attributes["bytes"] = node["s"]
                #attributes["file_data"] = self._get_file_data(file_id, root_folder)
                attributes["root_folder"] = root_folder
                attributes["key"] = key
                attributes["parent"] = parent
                attributes["applied"] = self._is_update_applied(file_name, modified_date, node["s"], parent, ini_file)
                attributes["type"] = self._get_directory_type(parent)

                if parent not in self._updates.keys():
                    self._updates[parent] = {}
                self._updates[parent][file_name] = attributes
            elif node["t"] == 1:
                self._dirs[file_name] = file_id

        return


    def get_quota(self):
        return self._mega.get_quota()
    

    def _parse_folder_url(self, url: str):
        "Returns (public_handle, key) if valid. If not returns None."
        REGEXP1 = re.compile(
            r"mega.[^/]+/folder/([0-z-_]+)#([0-z-_]+)(?:/folder/([0-z-_]+))*")
        REGEXP2 = re.compile(
            r"mega.[^/]+/#F!([0-z-_]+)[!#]([0-z-_]+)(?:/folder/([0-z-_]+))*")
        m = re.search(REGEXP1, url)
        if not m:
            m = re.search(REGEXP2, url)
        if not m:
            print("Not a valid URL")
            return None
        root_folder = m.group(1)
        key = m.group(2)
        # You may want to use m.groups()[-1]
        # to get the id of the subfolder
        return (root_folder, key)
    

    def _get_nodes_in_shared_folder(self, root_folder: str):
        data = [{"a": "f", "c": 1, "ca": 1, "r": 1}]
        try:
            response = requests.post(
                "https://g.api.mega.co.nz/cs",
                params={'id': 0,  # self.sequence_num
                        'n': root_folder},
                data=json.dumps(data)
            )
        except requests.exceptions.RequestException as e:
            print(e)
        #print(response)
        json_resp = response.json()
        return json_resp[0]["f"]


    def _is_update_applied(self, filename: str, modified_date: int, bytes: int, parent: str, ini_file: 'IniFile'):
        ret = 1
        # installed update value is: [installed date]-[modified date]-[file size]
        section = "INSTALLED_UPDATES"
        for key, val in self._dirs.items():
            if val != parent:
                continue
            ini_section = ini_file.get_config_value("DIR_SECTIONS", key)
            break

        value = self._ini.get_config_value(ini_section, filename)
        if value == None:
            return 0
        parts = value.split("-")
        if len(parts) < 3:
            self._ini.delete_config_option(ini_section, filename)
            return 0
        # installed date < modified date
        if value[0] > modified_date:
            ret = -1
        # modified date not right
        if value[1] != modified_date:
            ret = -1
        # filesize is not right
        if value[2] != bytes:
            ret = -1

        if ret == -1:
            self._ini.set_config_value(ini_section, filename, f"{parts[0]}-{parts[1]}-{parts[2]}-*")

        return ret
    

    def get_file_data_by_folder(self, file_id: str, root_folder: str):
        data = [{'a': 'g', 'g': 1, 'n': file_id}]
        response = requests.post(
            "https://g.api.mega.co.nz/cs",
            params={'id': 0,  # self.sequence_num
                    'n': root_folder},
            data=json.dumps(data)
        )
        json_resp = response.json()
        return json_resp[0]


    def download_found(self, file_data: str, file_key: tuple, iv: tuple, meta_mac: tuple, dest_path=None, dest_filename=None, verbose=False):
        #iv = file_key[4:6] + (0, 0)
        #meta_mac = file_key[6:8]

        return self._mega._execute_download(file_data, file_key, iv, meta_mac, dest_path=dest_path, dest_filename=dest_filename, verbose=verbose)
    
    def get_updates(self, dir=None):
        all = {}

        if dir == None:
            for key in self._dirs.keys():
                all.update(self._updates[self._dirs[key]])
        else:
            if dir in self._dirs:
                all.update(self._updates[self._dirs[dir]])
        
        return all