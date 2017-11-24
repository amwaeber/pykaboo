from configparser import ConfigParser

import os

from utility.create_config import write_config

write_config()

PROJECT_PATH = os.path.join(os.path.dirname(__file__), '..')

config = ConfigParser()
config.read(os.path.join(PROJECT_PATH, 'config.ini'))

global_confs = {}

for key in config['globals']:
    global_confs[key] = str(config['globals'][key])
