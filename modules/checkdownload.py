import json
import logging
import math
import os
import shutil
from collections import OrderedDict
from datetime import datetime
from glob import glob

from modules.emailhelper import send_email
from modules.imagecompression import Lepton

logger = logging.getLogger('Folder-Monitor')


class DownloadAndMove:
    def __init__(self, dropbox_project_dir, local_project_dir, nas_project_dir):
        self._dropbox_project_dir = dropbox_project_dir
        self._local_project_dir = local_project_dir
        self._nas_project_dir = nas_project_dir
        self._project_name = os.path.basename(self._dropbox_project_dir)
        self._list_dropbox_unnecessaries = ['.dropbox', '.ini']
        self.file_count = 0

    def get_storage_file(self, storage_project_dir, dropbox_file_path):
        return os.path.join(storage_project_dir, os.path.relpath(dropbox_file_path, self._dropbox_project_dir))

    def _move_cluster_status_file(self, dropbox_status_file):
        local_status_file = self.get_storage_file(self._local_project_dir, dropbox_status_file)
        if not os.path.isdir(os.path.dirname(local_status_file)):
            os.makedirs(os.path.dirname(local_status_file))
        if not os.path.exists(local_status_file):
            shutil.move(dropbox_status_file, local_status_file)
            self.file_count += 1
            logger.debug('File {} has been moved.'.format(dropbox_status_file))

    def _decompress_and_move_images_to_local(self, dropbox_comp_image_file):
        decompr_img_file = self.get_storage_file(self._local_project_dir,
                                                 os.path.splitext(dropbox_comp_image_file)[0] + '.JPG')

        if not os.path.isdir(os.path.dirname(decompr_img_file)):
            os.makedirs(os.path.dirname(decompr_img_file))

        try:
            lepton = Lepton()
            lepton.decompress(dropbox_comp_image_file, decompr_img_file)
            self.file_count += 1
        except (ValueError, FileNotFoundError) as err_msg:
            logger.error(str(err_msg))
        else:
            os.remove(dropbox_comp_image_file)
            logger.debug('File {} has been moved.'.format(dropbox_comp_image_file))

    def _move_videos_and_srt_to_nas(self, dropbox_movie_or_srt_file_name):
        movie_or_srt_nas_file = self.get_storage_file(self._nas_project_dir, dropbox_movie_or_srt_file_name)

        if not os.path.isdir(os.path.dirname(movie_or_srt_nas_file)):
            os.makedirs(os.path.dirname(movie_or_srt_nas_file))

        if not os.path.exists(movie_or_srt_nas_file):
            shutil.move(dropbox_movie_or_srt_file_name, movie_or_srt_nas_file)
            self.file_count += 1
            logger.debug('File {} has been moved.'.format(dropbox_movie_or_srt_file_name))

    def _move_supporting_files_to_nas(self, dropbox_supporting_file_name):

        supporting_file_nas = self.get_storage_file(self._nas_project_dir, dropbox_supporting_file_name)

        if not os.path.isdir(os.path.dirname(supporting_file_nas)):
            os.makedirs(os.path.dirname(supporting_file_nas))

        if not os.path.exists(supporting_file_nas):
            shutil.move(dropbox_supporting_file_name, supporting_file_nas)
            self.file_count += 1
            logger.debug('File {} has been moved.'.format(dropbox_supporting_file_name))

    @staticmethod
    def _email_json_file_issue(json_file_list):
        send_email(
            ['dweepmalakar@skylarkdrones.com', 'krnekhelesh@skylarkdrones.com'],
            'Json file problem at {}'.format(datetime.now().isoformat(sep=' ', timespec='seconds')),
            """
Hi,
            
The video error log file {} has no dictionary! Please ensure that there is a compatible JSON file to log errors.
            
Kind Regards,
Folder Monitor Script
            """.format(json_file_list)
        )

    def _check_status_file(self):
        downloaded_cluster_list = []
        problematic_json_file = []

        for root_dir, dirs, files in os.walk(self._local_project_dir):
            for file in files:
                if file.lower().endswith('.json') and os.path.basename(root_dir).startswith('Cluster'):
                    status_file = os.path.join(root_dir, file)
                    with open(status_file) as status_data:
                        try:
                            data = json.load(status_data, object_pairs_hook=OrderedDict)
                        except json.decoder.JSONDecodeError:
                            problematic_json_file.append(root_dir)
                        else:
                            if 'DownloadComplete' not in data:
                                total_file = float(data['ImageCount'])
                                image_dir = os.path.join(root_dir, 'Comp-Ortho-Data-Set')
                                if len(glob(os.path.join(image_dir, '*.JPG'))) == math.ceil(
                                                total_file / 2) and total_file != 0:
                                    downloaded_cluster_list.append(os.path.basename(root_dir))
                                    with open(status_file, 'w') as new_status_data:
                                        data['DownloadComplete'] = True
                                        json.dump(data, new_status_data)

        if downloaded_cluster_list:
            send_email(
                ['dweepmalakar@skylarkdrones.com', 'krnekhelesh@skylarkdrones.com',
                 'vaibhav.srinivasa@skylarkdrones.com'],
                'Cluster Download Report at {}'.format(datetime.now().isoformat(sep=' ', timespec='seconds')),
                """
Hi,

The following clusters data set have been fully downloaded and are ready for Ortho generation in Drone Deploy,

{downloaded_clusters}

Kind regards,
Folder Monitor Script
                """.format(downloaded_clusters='\n'.join(downloaded_cluster_list))
            )

        if problematic_json_file:
            self._email_json_file_issue(problematic_json_file)

    def check_create_move(self):
        logging.info('Performing files check ...')

        for root_dir, dirs, files in os.walk(self._dropbox_project_dir):
            for file in files:

                absolute_file_path = os.path.join(root_dir, file)
                for file_str in self._list_dropbox_unnecessaries:
                    if file_str in absolute_file_path:
                        # Do not move any files if it is one of dropbox's internal files like .dropbox_cache etc.
                        logger.log('File named {} is detected, so ignoring the file'.format(absolute_file_path))
                        continue

                if file.lower().endswith('.json'):
                    self._move_cluster_status_file(absolute_file_path)
                elif file.lower().endswith('.lep'):
                    self._decompress_and_move_images_to_local(absolute_file_path)
                elif file.lower().endswith(('.mp4', '.mov', '.srt')):
                    self._move_videos_and_srt_to_nas(absolute_file_path)
                else:
                    self._move_supporting_files_to_nas(absolute_file_path)

        logger.info('{} files were detected and moved'.format(self.file_count))

        self._check_status_file()
