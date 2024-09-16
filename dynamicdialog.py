import ast
from inifile import IniFile




class DynamicDialog:
    def __init__(self, ini_file: IniFile, option=None, translator=None, values=None):
        self._option = option
        self._filter = None
        self._ini_file = ini_file
        self._value = ""
        self._next_value = ""
        if self._option:
            self.get()
        if translator and values:
            self._filter = self._get_filter(translator, values)

        return

    @property
    def value(self):
        return self._value
    
    @property
    def next_value(self):
        return self._next_value
    
    @property
    def filter(self):
        return self._filter


    def _save(self, default=False):
        options = self._get_options()
        value = self._value if not default else options[0]
        self._ini_file.set_config_value("DYNAMIC", self._option, f"{value}; {options}")        

        return
    

    def _get_options(self):
        dynamic_data = self._ini_file.get_config_value("DYNAMIC", self._option)
        parts = dynamic_data.split(";")

        if len(parts) != 2:
            return None, None
        if self._filter is not None:
            return self._filter

        try:
            value = parts[0]
            order = ast.literal_eval(parts[1])
            if not isinstance(order, list):
                return None
        except ValueError:
            return None

        return order
    

    def _parse(self):
        dynamic_data = self._ini_file.get_config_value("DYNAMIC", self._option)
        parts = dynamic_data.split(";")

        if len(parts) != 2:
            return None, None

        try:
            value = parts[0]
            order = ast.literal_eval(parts[1])
            if not isinstance(order, list):
                return None, None
        except ValueError:
            return None, None

        if self._filter is not None:
            order = self._filter

        if value not in order:
            value = order[0]
            self._value = value
            self._save()

        return value, order


    def _get_filter(self, translator: dict, values: dict):
        filter = []
        value, order = self._parse()

        for item in order:
            if translator[item] in values.keys():
                filter.append(item)

        return filter


    def set_defaults(self):
        if self._option:
            self._save(default=True)

            return True
        
        section = self._ini_file.get_config_section("DYNAMIC")
        if section is None:
            return False
        for key, val in section:
            self._option = key
            self._save(default=True)

        return True


    def get(self):
        value, order = self._parse()
        if value is None:
            return "", ""
        
        if self._filter and len(self._filter) == 1:
            self._next_value = ""
            return self._value, self._next_value
        
        self._value = value
        index = order.index(value)
        self._next_value = order[(index + 1) % len(order)]

        return self.value, self._next_value


    def next(self):
        value, order = self._parse()
        if value is None:
            return None, None
        
        if self._filter and len(self._filter) == 1:
            self._next_value = ""
            return self._value, self._next_value
        
        index = order.index(self._value)
        self._value = order[(index + 1) % len(order)]
        self._next_value = order[(index + 2) % len(order)]     
        self._save()
        
        return self._value, self._next_value
    

    def get_selected(self, value, selected: 'DynamicDialog'):
        if selected.value == "Deselect":
            return False
        elif selected.value == "Select":
            return True
        
        return value        
