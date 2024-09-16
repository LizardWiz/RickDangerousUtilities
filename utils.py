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


def status_bar(total_size: float, current_size: float, start_time: datetime, complete=False, start_char="\t"):
    current_time = datetime.datetime.utcnow()
    percent_complete = round((current_size / total_size) * 100)
    if percent_complete > 99 and not complete:
        percent_complete = 99
    kbs = return_bps(current_size, (current_time - start_time).total_seconds())
    pad = (12 - len(kbs))

    if not complete:
        print(f"{start_char}{percent_complete if percent_complete < 100 else 99}% complete: [{'='*percent_complete}>{' '*(99 - percent_complete)}] ({kbs}) (total elapsed time: {str(current_time - start_time)[:-7]}){' '*pad}", end = "\r")
    else:
        print(f"{start_char}100% complete: [{'='*100}] ({kbs}) (total elapsed time: {str(current_time - start_time)[:-7]}){' '*pad}")

    return


def return_bps(bytes: float, seconds: float):
    retval = ""
    units = ["B", "KB", "MB", "GB"]
    unit = "B"
    count = 0
    filesize = bytes / seconds
    while (filesize) >= 1000:
        count += 1
        filesize /= 1024

    if count == 0:
        retval = "%0.2f" % filesize + " " + unit + "/s"
    else:
        retval = "%0.2f" % filesize + " " + units[count] + "/s"

    return retval    


def clean_path(path: str):
    # god what a lazy hack
    return path.replace("//", "/")


def prepare_script(script: str):
    commands = []

    if os.path.isfile(script):
        with open(script, 'r', encoding='utf-8') as file:
            lines = file.readlines()

            for line in lines:
                if line.strip()[0:1] == "#":
                    continue
                if len(line.strip()) == 0:
                    continue
                commands.append(line.strip())

    return lines


def get_dict_key_by_value(in_dict: dict, value):
    for key, val in in_dict.items():
        if val == value:
            return key
        
    return None
