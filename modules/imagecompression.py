import logging
import os
import subprocess
import sys

from modules.emailhelper import send_email
from .exceptions import LeptonBinaryMissingError

logger = logging.getLogger('Folder-Monitor')

class Lepton:
    PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    LEPTON_BIN = os.path.join(
        PROJECT_DIR,
        'execs',
        'lepton' if sys.platform == 'linux' else 'lepton.exe'
    )

    if not os.path.exists(LEPTON_BIN):
        err_msg = 'Lepton binary cannot be found to perform image decompression!'
        logger.critical(err_msg)
        send_email(
            ['krnekhelesh@skylarkdrones.com', 'dweepmalakar@skylarkdrones.com'],
            'Lepton Binary Missing Error',
            err_msg
        )
        raise LeptonBinaryMissingError

    def compress(self, input_file, output_file):
        if input_file.lower().endswith(".jpg") and output_file.endswith(".lep"):
            arg = [self.LEPTON_BIN, input_file, output_file]
            try:
                subprocess.call(arg, stdout=open(os.devnull, 'wb'), stderr=subprocess.STDOUT)
                return {"input_file": input_file, "success": True}
            except subprocess.CalledProcessError:
                return {"input_file": input_file, "success": False}
        else:
            return {"input_file": input_file, "success": False}

    def decompress(self, input_file, output_file):
        if input_file.endswith(".lep") and output_file.lower().endswith(".jpg"):
            arg = [self.LEPTON_BIN, input_file, output_file]
            if os.path.exists(input_file):
                try:
                    subprocess.call(arg, stdout=open(os.devnull, 'wb'), stderr=subprocess.STDOUT)
                except subprocess.CalledProcessError:
                    raise subprocess.CalledProcessError
            else:
                raise FileNotFoundError('{} does not exist!'.format(input_file))
        else:
            raise ValueError('Only .lep input files and .jpg output files are accepted!')
