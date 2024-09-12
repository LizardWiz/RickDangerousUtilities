from datetime import datetime, timezone
import shutil
import os


def safe_write_check(file_path: str, file_time: str):
    if os.path.exists(file_path + "--" + file_time) and os.path.isfile(file_path + "--" + file_time):
        if os.path.getsize(file_path) == 0:
            # this somehow failed badly
            shutil.copy2(file_path + "--" + file_time, file_path)
            return False

        os.remove(file_path + "--" + file_time)

    return True


def safe_write_backup(file_path: str, file_time=""):
    if file_time == "":
        file_time = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")

    if os.path.exists(file_path) and os.path.isfile(file_path):
        shutil.copy2(file_path, file_path + "--" + file_time)

    return file_time


def get_path(file: str):
    return os.path.dirname(file)


def get_system_longname(system: str, path: str):
    # todo: create ini class
    return path.replace("./", f"/userdata/roms/{system}/")


def get_system_shortname(system: str, path: str):
    # todo: create ini class
    return path.replace(f"/userdata/roms/{system}", "./")


def convert_filesize(file_size: str, unit="B"):
    retval = ""
    filesize = float(file_size)
    units = ["B", "KB", "MB", "GB", "TB"]
    count = units.index(unit)
    while (filesize) >= 1000:
        count += 1
        filesize /= 1024

    if count == 0:
        retval = str(round(filesize)) + " " + unit
    elif count == 1:
        retval = str(round(filesize)) + " " + units[count]
    else:
        retval = str(round(filesize, count - 1)) + " " + units[count]

    return retval


def log_this(log_file: str, log_text: str, overwrite=False):
    if log_file is None:
        return

    if not os.path.isdir(os.path.dirname(log_file)):
        os.makedirs(os.path.dirname(log_file))

    if overwrite == True or not os.path.isfile(log_file):
        with open(log_file, 'w', encoding='utf-8') as logfile:
            logfile.write(log_text.strip() + "\n")
    else:
        with open(log_file, 'a', encoding='utf-8') as logfile:
            logfile.write(log_text.strip() + "\n")

    return