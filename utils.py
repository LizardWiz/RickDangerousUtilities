from datetime import datetime, timezone
import shutil
import os


def safe_write_check(file_path: str, file_time: str):
    if os.path.getsize(file_path) == 0:
        # this somehow failed badly
        shutil.copy2(file_path + "--" + file_time, file_path)
        return False

    os.remove(file_path + "--" + file_time)

    return True


def safe_write_backup(file_path: str, file_time=""):
    if file_time == "":
        file_time = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")

    shutil.copy2(file_path, file_path + "--" + file_time)

    return file_time
