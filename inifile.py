from configparser import ConfigParser
import os

class IniFile:
    def __init__(self, ini_file, status=False):
        self._ini_file = ini_file
        self._config = self._read_config()

        return
    

    def _read_config(self):
        if os.path.exists(self._ini_file):
            if os.path.isfile(self._ini_file):
                config = ConfigParser()
                config.optionxform = str
                config.read(self._ini_file)
                return config
            
        return None
    

    def get_config_section(self, section: str):
        if self._config is not None:
            if self._config.has_section(section):
                return self._config.items(section)

        return None
    

    def get_config_value(self, section: str, key: str, return_none=True):
        if self._config is not None:
            if self._config.has_option(section, key):
                return self._config[section][key]

        if return_none == False:
            return ""

        return None
    

    def set_config_value(self, section: str, key: str, value: str):
        if self._config is not None:
            if self._config.has_section(section) == False:
                self._config.add_section(section)

            self._config[section][key] = value

            with open(self._ini_file, 'w') as configfile:
                self._config.write(configfile)

            return True

        return False