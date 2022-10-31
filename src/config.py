# This file implements functions and ressources used to configure the server/client

import configparser as cp

class Configuration:

    def __init__(conf_path):
        self.config = cp.ConfigParser()
    
        try:
            self.config.read(conf_path)
        except Exception as e:
            raise e


