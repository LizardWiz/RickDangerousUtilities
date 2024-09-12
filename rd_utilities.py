import zipimport
import sys
import os
import platform
import requests
from datetime import datetime, timezone
import traceback
import utils
from availableupdates import AvailableUpdates
from inifile import IniFile
from gamelist import Gamelist
if platform.uname()[1] == "BATOCERA":
    from gamesystem import BatoceraGameSystem as GameSystem
else:
    from gamesystem import GameSystem as GameSystem

sys.path.insert(0, './packages')
from dialog import Dialog
from mega import Mega

dlgs = []
tool_ini = "rd_utilities.ini"
d = Dialog()
d.autowidgetsize = True
mega = Mega()

available_updates = AvailableUpdates()
ini_file = IniFile(tool_ini)

def get_total_size_of_updates(updates: list):
    total_size = 0

    for update in updates:
        total_size += int(update[4])

    return utils.convert_filesize(str(total_size))


def check_update():
    return "Make check_update()"


def cls():
    os.system('cls' if os.name == 'nt' else 'clear')


def check_internet():
    url = "http://www.google.com/"
    try:
        resp = requests.get(url)
    except requests.exceptions.RequestException as e:
        return False

    return True


def dlg_improvements_official(update_dir=None, delete=False, process_improvements=True, updates=None):
    reboot_msg = "Updates installed:"
    menu_choices = []
    update_list = available_updates.updates if updates is None else updates.updates
    total_updates = 0
    total_size = 0
    for update in sorted(update_list.keys()):
        menu_choices.append([f"{update} ({update_list[update]['file_size']})", "", False])
        total_updates += 1
        total_size += update_list[update]['bytes']
    
    auto_clean = ini_file.get_config_value("CONFIG_ITEMS", "auto_clean")
    if auto_clean is None:
        auto_clean is True
    show_all_updates = ini_file.get_config_value("CONFIG_ITEMS", "show_all_updates")
    if show_all_updates is None:
        show_all_updates is False
    
    help_label = "Show All"
    title_msg  = "Download and Install Official Updates" if update_dir is None else "Manually Install Official Updates"
    code, tags = d.checklist(text=f"Auto Clean is {'off' if auto_clean is False else 'on'}\nShow All Updates is {'off' if show_all_updates is None else 'off'}\n\nNumber of available updates: {total_updates} ({utils.convert_filesize(total_size)})\n", #Number of updates needed: {} ({})\nRecommended number of updates: {} ({})\n\n{} Updates".format("on" if auto_clean == True else "off", "on" if show_all_updates == True else "off", len(available_updates), get_total_size_of_updates(available_updates), len(needed_updates), get_total_size_of_updates(needed_updates), len(recommended_updates), get_total_size_of_updates(recommended_updates), update_text),
                            choices=menu_choices,
                            ok_label="Apply Selected", 
                            extra_button=True, 
                            extra_label="Apply All", 
                            help_button=True, 
                            help_label=help_label, 
                            title=title_msg)
    
    selected_updates = []
    if code == d.OK:
        for tag in tags:
            for update in update_list.keys():
                if f"{update} ({update_list[update]['file_size']})" == tag:
                    reboot_msg += "\n" + tag
                    selected_updates.append(update)
                    break

    if len(selected_updates) == 0:
        d.msgbox("No updates selected!")
    else:
        if process_improvements == False:
            return selected_updates

        print()
        if update_dir is None:
            for update in selected_updates:
                if not os.path.exists("/tmp/improvements"):
                    os.makedirs("/tmp/improvements")
                file_data = available_updates.get_file_data_by_folder(update_list[update]["file_id"], update_list[update]["root_folder"])
                ret = mega.download_file(update_list[update]["file_id"], update_list[update]["key"], file_data, dest_path="/tmp/improvements", verbose=True)

    return code


def dlg_improvements():
    cls()
    result = True
    code, tag = d.menu("Select Option", 
                    choices=[("1", "Download and Install Updates"),
                             ("2", "Manually Install Downloaded Updates"), 
                             ("3", "Update Status"), 
                             ("4", "Validate Downloaded Updates"), 
                             ("5", "Manual Updates Story")],
                    title="Improvements")

    if code == d.OK:
        if tag == "1":
            if not check_internet():
                d.msgbox("You need to be connected to the internet for this.")
            else:
                #space_warning()
                dlg_improvements_official()
        #elif tag == "2":
        #    space_warning()
        #    downloaded_update_question_dialog()
        #elif tag == "3":
        #    check_update_status_dialog()
        #elif tag == "4":
        #    validate_manual_updates()
        #elif tag == "5":
        #    get_manual_updates_story()

    return code

def dlg_main(test="check_update"):
    result = True
    global update_available_result
    #if update_available_result == "no connection":
    #    update_available_result = update_available()

    code, tag = d.menu("Main Menu", 
                    choices=[("1", "Improvements"),    
                             ("2", "System Tools and Utilities"),
                             ("3", "Installation"),
                             ("4", "Settings"), 
                             ("5", "Support")],
                             
                    title=test,
                    backtitle="Rick Dangerous Utilities",
                    cancel_label=" Exit ")
    
    if code == d.OK:
        if tag == "1":
            dlg(dlg_improvements)
        #elif tag == "2":
        #    misc_menu()
        #elif tag == "3":
        #    if not check_internet():
        #        d.msgbox("You need to be connected to the internet for this.")
        #        main_dialog()
        #    else:
        #        installation_dialog()
        #elif tag == "4":
        #    settings_dialog()
        #elif tag == "5":
        #    support_dialog()

    return code


def dlg(*args, **kwargs):
    global dlgs
    dlgs.insert(0, [args[0], kwargs])

    while len(dlgs) > 0:
        if len(dlgs[0][1]) > 0:
            result = dlgs[0][0](**dlgs[0][1])
        else:
            result = dlgs[0][0]()

        if result == d.CANCEL or result == d.ESC:
            del dlgs[0]

    return

def main():
    global mega
    mega = mega.login()

    available_updates.mega = mega
    available_updates.get_available_updates("https://mega.nz/folder/yDAliCBL#ex6Y7QagY_4hu0kUfu35jQ/file/bChAhCJS", status=True)
    dlg(dlg_main, test="check_update")
    cls()

    return


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        #print("")
        nothing = None
    except:
        title_text = ""
        if os.path.exists(tool_ini):
            title_text = "A copy of this exception is logged in /userdata/.utilities_tool/exception.log for your records\n\n"
            # TO DO: make ini stuff
            #version = get_config_value("CONFIG_ITEMS", "tool_ver")
            version = "Pre-Release"
            if version is not None:
                title_text += "Version: " + version + "\n\n"
            utils.log_this("/userdata/.utilities_tool/exception.log", f"*****\nDate: {datetime.now(timezone.utc)}\nVersion: {version}\n\n{traceback.format_exc()}")
            utils.log_this(f"/userdata/.utilities_tool/exception.log", "\n\n")

        d.msgbox(title_text + traceback.format_exc(), title="Something has gone really bad...")
