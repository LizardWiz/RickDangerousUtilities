import sys
sys.path.insert(0, './packages/')
from mega import Mega
from mega.crypto import base64_to_a32, base64_url_decode, decrypt_attr, decrypt_key, a32_to_str, get_chunks, str_to_a32
from mega.errors import RequestError

import requests
import json
import utils
import re

mega = Mega()

class AvailableUpdates:
    def __init__(self, megadir: str, status=False):
        self._megadir = megadir
        self._updates = {}
        self._get_available_updates(megadir)

        return

    @property
    def updates(self):
        return self._updates

    def _decrypt_node_key(self, key_str: str, shared_key: str):
        encrypted_key = base64_to_a32(key_str.split(":")[1])

        return decrypt_key(encrypted_key, shared_key)


    def _get_available_updates(self, megadrive: str, status=False):
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
            modified_date = node["ts"]
            if node["t"] == 0:
                attributes = {}
                attributes["file_id"] = file_id
                attributes["modified_date"] = modified_date
                attributes["file_size"] = utils.convert_filesize(node["s"])
                attributes["bytes"] = node["s"]
                attributes["file_data"] = self._get_file_data(file_id, root_folder)
                attributes["key"] = k

                self._updates[file_name] = attributes

        return


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


    def _get_file_data(self, file_id: str, root_folder: str):
        data = [{'a': 'g', 'g': 1, 'n': file_id}]
        response = requests.post(
            "https://g.api.mega.co.nz/cs",
            params={'id': 0,  # self.sequence_num
                    'n': root_folder},
            data=json.dumps(data)
        )
        json_resp = response.json()
        return json_resp[0]