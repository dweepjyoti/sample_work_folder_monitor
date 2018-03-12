# Main Program File

import logging
import os
import json
import time

from collections import OrderedDict
from datetime import datetime

from modules.checkdownload import DownloadAndMove
from modules.emailhelper import send_email

logger = logging.getLogger('Folder-Monitor')
logger.setLevel(logging.DEBUG)

# create a file handler
handler = logging.FileHandler('folder-monitor.log')
handler.setLevel(logging.DEBUG)

# create a logging format
formatter = logging.Formatter('%(asctime)s [%(levelname)s][%(module)s]: %(message)s', datefmt="%d/%m/%Y %H:%M:%S")
handler.setFormatter(formatter)

# add the handlers to the logger
logger.addHandler(handler)

# dict info or format in which the folder monitor parameter file should be

logger.info("------------------  Folder-Monitor Start  ------------------")
PARAM_FILE = 'parameters.json'
dropbox_project_dir = None
local_project_dir = None
nas_project_dir = None
sleep_time = 1200

parameter_default = {"DropboxDir": dropbox_project_dir,
                     "LocalImageDir": local_project_dir,
                     "NASDir": nas_project_dir,
                     "SleepTime": sleep_time}


mendatory_keys = ["DropboxDir", "LocalImageDir", "NASDir", "SleepTime"]


try:
    with open(PARAM_FILE, 'r') as parameter_file:
        try:
            parameters = json.load(parameter_file, object_pairs_hook=OrderedDict)
        except json.decoder.JSONDecodeError:
            with open(PARAM_FILE, 'w') as new_param_file:
                json.dump(parameter_default, new_param_file)
            logger.exception("Parameter json file was in incorrect format. It has been reset to default format like {}.".format(
                parameter_default))
            exit()
        else:
            key_check = [True if key in parameters else False for key in mendatory_keys]
            if not all(key_check):
                with open(PARAM_FILE, 'w') as new_param_file:
                    json.dump(parameter_default, new_param_file)
                logger.info("Improper key name for one or more key names in parameters.json.")
                exit()

            if not all((parameters["DropboxDir"], parameters["LocalImageDir"], parameters["NASDir"])):
                logger.info("Folder paths in parameters.json should not be null")
                exit()

            if os.path.exists(parameters["DropboxDir"]):
                dropbox_project_dir = parameters["DropboxDir"]
            else:
                logger.info("Dropbox project folder does not exists.")

            if os.path.exists(parameters["LocalImageDir"]):
                local_project_dir = parameters["LocalImageDir"]
            else:
                logger.info("Local folder to move images, does not exists.")

            if os.path.exists(parameters["NASDir"]):
                nas_project_dir = parameters["NASDir"]
            else:
                logger.info("NAS folder to move videos, does not exists.")

            sleep_time = parameters.get("SleepTime", 1200)


except FileNotFoundError:
    with open(PARAM_FILE, 'w') as new_param_file:
        json.dump(parameter_default, new_param_file)
    logger.info(
        "Parameter json file is not present. Kindly make a json file named 'parameters.json' inside folder_monitor folder with the format {}.".format(
            parameter_default))
    exit()

# dropbox_project_dir = r'E:\Images\Syn' # input('Enter Dropbox root location Eg: /home/dj92/Dropbox (Skylark Drones): ')
# local_project_dir = r'E:\local\Syn' # input('Enter local storage location: ')
# nas_project_dir = r'E:\nas\Syn' # input('Enter NAS storage location: ')

logger.debug('Dropbox dir: {}'.format(dropbox_project_dir))
logger.debug('Local storage dir: {}'.format(local_project_dir))
logger.debug('NAS storage dir: {}'.format(nas_project_dir))

if os.path.isdir(dropbox_project_dir) and os.path.isdir(local_project_dir) and os.path.isdir(nas_project_dir):
    download = DownloadAndMove(dropbox_project_dir, local_project_dir, nas_project_dir)
    while True:
        download.check_create_move()
        download.file_count = 0
        time.sleep(sleep_time)  # DONE: "AIRDATA ACCOUNT PROBLEM", changed frequency to 20 mins

else:
    logger.error('Invalid input directories entered!')
