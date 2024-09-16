import zipimport
import sys
import os
import platform
import requests
from datetime import datetime, timezone
import traceback
from pathlib import Path
import utils
from availableupdates import AvailableUpdates
from inifile import IniFile
from gamelist import Gamelist
from dynamicdialog import DynamicDialog
if platform.uname()[1] == "BATOCERA":
    from gamesystem import BatoceraGameSystem as GameSystem
    game_system = "BATOCERA"
else:
    from gamesystem import GameSystem as GameSystem
    game_system = "retropie"

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
game_system = GameSystem(game_system)


def parse_available_updates(available_updates: dict):
    # this will return a dict with values being the update name
    #
    # keys are:
    # all
    # applied = update was upplied
    # needed = update was not applied
    # bad = update
    # [directory] = directory for special available updates i.e. roms/batocera for base image updates in RD image
    #
    # usage:
    # sort
    # combine needed/bad for "needed" updates
    # after first "needed" update everything else is "recommended" unless it is a base image update
    updates = {}

    for update in available_updates.keys():
        if available_updates[update]["applied"] == 0:
            if "needed" not in updates.keys():
                updates["needed"] = [update]
            else:
                updates["needed"].append(update)
        if available_updates[update]["applied"] == 1:
            if "needed" not in updates.keys():
                updates["needed"] = [update]
            else:
                updates["neededd"].append(update)
        if available_updates[update]["applied"] == -1:
            if "bad" not in updates.keys():
                updates["bad"] = [update]
            else:
                updates["bad"].append(update)

        if available_updates[update]["type"] != "all":
            if available_updates[update]["type"] not in updates.keys():
                updates[available_updates[update]["type"]] = [update]
            else:
                updates[available_updates[update]["type"]].append(update)

        if "all" not in updates.keys():
            updates["all"] = [update]
        else:
            updates["all"].append(update)

    return updates


def process_improvements(updates: list, status=True, auto_clean=False, official=True):
    while len(updates) > 0:
        print(f"Processing {'un' if not official else ''}official update: {os.path.basename(updates[0])} ({utils.convert_filesize(os.path.getsize(updates[0]))})...")
        print("Extracting...")

        # unzip file
        zip_file = game_system.extract_zipfile(updates[0], ini_file)
        if zip_file == False:
            text = f"Error unzipping file: {updates[0]}\n\nWould you like to continue processing and skip this fie?"
            code = d.yesno(text=text, ok_label="Continue")
            if code == d.OK:
                return False
        
        # create pre/post script commands
        pre_script = utils.prepare_script(f'{ini_file.get_config_value("CONFIG_ITEMS", "tmp_directory")}/{ini_file.get_config_value("CONFIG_ITEMS", "extract_directory")}/{ini_file.get_config_value("CONFIG_ITEMS", "pre_script")}')
        post_script = utils.prepare_script(f'{ini_file.get_config_value("CONFIG_ITEMS", "tmp_directory")}/{ini_file.get_config_value("CONFIG_ITEMS", "extract_directory")}/{ini_file.get_config_value("CONFIG_ITEMS", "post_script")}')
        # merge gamelists
        directory = ini_file.get_config_value("CONFIG_ITEMS", "tmp_directory")
        gamelists = Path(directory).rglob('gamelist.xml')
        if len(gamelists) > 0:
            print("Merging gamelists...")
        for gamelist in gamelists:
            game_list = Gamelist(gamelist=str(gamelist), official=official)
            merge_path = utils.clean_path(f'{ini_file.get_config_value("CONFIG_ITEMS", "check_gamelists_roms_dir")}/{game_list.system}/gamelist.xml')
            if os.path.exists(merge_path):
                merge_game_list = Gamelist(gamelist=merge_path)
                game_list.merge(merge_game_list, official=official)
            game_list.save()
            game_list.write_origins()

        # success!
        del updates[0]


    return


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


def dlg_updates_official(update_dir=None, delete=False, process_improvements=True, updates=None):
    reboot_msg = "Updates installed:"
    menu_choices = []
    update_list = available_updates.get_available_updates() if updates is None else updates.updates
    total_updates = 0
    total_size = 0
    for update in sorted(update_list.keys()):
        menu_choices.append([f"{update} ({update_list[update]['file_size']})", "", update_list[update]])
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


def dlg_image_manual():
    directories = {"Image Packages": "batocera", "Rom Packs": "roms", "All": "all", "Needed": "needed", "Bad": "bad"}
    title_msg  = "Manually Install Image Components"
    menu_choices = []

    update_list = available_updates.get_updates()
    parsed_update_list = parse_available_updates(update_list)
    dyn_image_show = DynamicDialog(ini_file, option="image_show", translator=directories, values=parsed_update_list)
    dyn_image_select = DynamicDialog(ini_file, option="image_select")

    updates = {}
    if directories[dyn_image_show.value] in parsed_update_list:
        updates = parsed_update_list[directories[dyn_image_show.value]]
    total_updates = 0
    total_size = 0

    for update in sorted(updates):
        menu_choices.append([f"[{utils.get_dict_key_by_value(directories, update_list[update]['type'])}] {update} ({update_list[update]['file_size']})", "", dyn_image_show.get_selected(update_list[update]['applied'] != 1, dyn_image_select)])
        total_updates += 1
        total_size += update_list[update]['bytes']

    code, tags = d.checklist(
        text=f"Showing {dyn_image_show.value}",
        choices=sorted(menu_choices),
        ok_label="Apply Selected", 
        extra_button=bool(dyn_image_select.next_value), 
        extra_label=dyn_image_select.next_value  + (" All" if dyn_image_select.next_value != "As Is" else ""), 
        help_button=bool(dyn_image_show.next_value), 
        help_label=f"Show {dyn_image_show.next_value}", 
        title=title_msg
    )

    if code == d.HELP:
        dyn_image_show.next()
    elif code == d.EXTRA:
        dyn_image_select.next()

    return code


def dlg_image():
    result = True
    code, tag = d.menu("Select Option", 
                    choices=[("1", "Manually Install Image Components"), 
                             ("2", "Image Component Status"), 
                             ("3", "Validate Downloaded Image Components"), 
                             ("4", "Manual Image Components Story")],
                    title="Image")

    if code == d.OK:
        if tag == "1":
            dlg(dlg_image_manual)

    return code


def dlg_updates():
    cls()
    result = True
    code, tag = d.menu("Select Option", 
                    choices=[("1", "Download and Install Updates"),
                             ("2", "Manually Install Downloaded Updates"), 
                             ("3", "Update Status"), 
                             ("4", "Validate Downloaded Updates"), 
                             ("5", "Manual Updates Story")],
                    title="Updates")

    if code == d.OK:
        if tag == "1":
            if not check_internet():
                d.msgbox("You need to be connected to the internet for this.")
            else:
                #space_warning()
                dlg_updates_official()
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
                    choices=[("1", "Image Components"),    
                             ("2", "Updates"),
                             ("3", "System Tools and Utilities"),
                             ("4", "Installation"),
                             ("5", "Settings"), 
                             ("6", "Support")],
                             
                    title=test,
                    backtitle="Rick Dangerous Utilities",
                    cancel_label=" Exit ")
    
    if code == d.OK:
        if tag == "1":
            dlg(dlg_image)
        if tag == "2":
            dlg(dlg_updates)
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
    DynamicDialog(ini_file).set_defaults()
    game_list = Gamelist("./gamelist.xml")
    game_list.write_origins(ini_file)
    global mega
    mega = mega.login()

    available_updates.mega = mega
    available_updates.get_available_updates(ini_file.get_config_value("CONFIG_ITEMS", "mega_base"), ini_file, status=True)
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
