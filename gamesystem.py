import re
import os
import subprocess
import time
import zipfile
import utils
import datetime
from inifile import IniFile

class GameSystem:
    def __init__(self, system: str):
        self._system = system
        self._filetypes = None


    @property
    def system(self):
        return self._system
   
    @property
    def filetypes(self):
        return self._filetypes
    
    def extract_zipfile(zip_file: str, ini_file: IniFile):
        start_time = datetime.datetime(datetime.timezone.utc)
        total_size = 0
        last_size = 0
        current_size = 0
        dir_name = f'{ini_file.get_config_value("CONFIG_ITEMS", "tmp_directory")}/{ini_file.get_config_value("CONFIG_ITEMS", "extract_directory")}'

        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            total_size = sum([zinfo.file_size for zinfo in zip_ref.filelist])

        if os.path.isdir(dir_name):
            os.system(f"sudo rm -rf {dir_name} > /tmp/test")
            #shutil.rmtree(dir_name)
        os.mkdir(dir_name)
        proc = subprocess.Popen(["/usr/bin/unzip", "-q", zip_file, "-d", dir_name])

        while proc.poll() == None:
            result = subprocess.run(["/usr/bin/du", "-sb", dir_name], stdout=subprocess.PIPE)
            current_size = int(result.stdout.split()[0])
            utils.status_bar(total_size, current_size, start_time)
            time.sleep(.5)
            
        if proc.returncode > 1:
            return False
            
        utils.status_bar(total_size, current_size, start_time, complete=True)

        return True
        
    def _update_config(self, extracted: str):
        return

    def process_improvement(self, file: str, ini_file: IniFile, status=True, auto_clean=False, official=True):
        return True


class BatoceraGameSystem(GameSystem):
    def __init__(self, system: str):
        super().__init__(system)
        self._filetypes = self._get_filetypes()


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
    

    #def extract_zipfile(zip_file: str, ini_file: IniFile):
    #    return super().extract_zip_file(zip_file, ini_file)
   