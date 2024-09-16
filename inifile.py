from configparser import ConfigParser
import os

class IniFile:
    def __init__(self, ini_file, status=False):
        self._ini_file = ini_file
        self._config = self._read_config()
        self._type = "config"

        return
    

    def _read_config(self):
        if os.path.exists(self._ini_file):
            if os.path.isfile(self._ini_file):
                config = ConfigParser()
                config.optionxform = str
                config.read(self._ini_file)
                return config
            
        return None
    

    def delete_config_option(self, section: str, key: str):
        if self._config is not None:
            if not self._config.has_section(section):
                self._create_config_section(section)
            if self._config.has_option(section, key):
                self._config.remove_option(section, key)

        return
    

    def get_config_section(self, section: str):
        if self._config is not None:
            if self._config.has_section(section):
                return self._config.items(section)

        return None
    

    def get_config_value(self, section: str, key: str, return_none=True):
        if self._config is not None:
            if not self._config.has_section(section):
                self._create_config_section(section)
            if self._config.has_option(section, key):
                return self._config[section][key]

        if return_none == False:
            return ""

        return None
    

    def set_config_value(self, section: str, key: str, value: str):
        if self._config is not None:
            if self._config.has_section(section) == False:
                self._create_config_section(section)

            self._config[section][key] = value
            self.save()

            return True

        return False


    def refresh(self):
        self._config = self._read_config()

        return
    

    def save(self):
        with open(self._ini_file, 'w', encoding="UTF-8") as configfile:
            self._config.write(configfile)

        return
    

    def set_type(self, type: str):
        self._type = type

        return