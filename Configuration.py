
import json
import logging
import os
from datetime import datetime


class Configuration:
    """Configuration class. Handles the management of all the configurations."""
    filename = ''
    log = None
    data = {}
    skel = {}

    def __init__(self, filename="config.json"):
        self.log = logging.getLogger(self.__class__.__name__)
        self.filename = filename

    def __getitem__(self, item):
        return self.data[item]

    def load(self):
        """
        Loads data from file.
        :return: Success
        :rtype: bool
        """
        if not os.path.exists(self.filename):
            return False
        try:
            with open(self.filename, 'r') as config_file:
                jsonstr = config_file.read()
                if not jsonstr == '':
                    self.data = json.loads(jsonstr)
            return True
        except FileNotFoundError as ex:
            self.log.warning(ex)
            return False
        except Exception as ex:
            self.log.error(ex)
            return False

    def save(self):
        """
        Saves data to file.
        :return: Success
        :rtype: bool
        """
        try:
            with open(self.filename, 'w') as fp:
                json.dump(self.data, fp, indent=2)
        except FileNotFoundError as ex:
            self.log.error(ex)
            return False
        except Exception as ex:
            self.log.error(ex)
            return False

    def _default(self, key, value, node):
        """Checks if key exists in dict and sets it to a default value if not.
        :param key: The key to check for
        :type key: str
        :param value: The default value
        :type value: object
        :param node: The node to observe
        :type node: dict
        :return: True if the default has been set
        :rtype: bool
        """
        if key not in node:
            node[key] = value
            return True
        return False

    def complete_data(self):
        """Completes datastructure.
        :return: self
        :rtype: Configuration
        """
        if Keys.SERVER in self.data:
            server = self.data[Keys.SERVER]
            self._default(Keys.SERVER_ADDRESS, '8.8.8.8', server)
            self._default(Keys.SERVER_PORT, 25565, server)
        return self

    # TODO: Finish this. Write unittest first.
    @staticmethod
    def _complete_with_skel(data, skel):
        """
        Completes the data structure according to the skeleton.
        :param data: The data to complete
        :type data: object
        :param skel: Corresponding skeleton template
        :type skel: object
        :return: Completed data object
        :rtype: object
        """
        if data is None:
            data = skel
            return data
        if type(skel) == list:
            pass
        elif type(skel) == dict:
            skeldict: dict = skel
            for key in skeldict:
                if key not in data:
                    pass
        else:
            if data is None:
                data = skel


class Keys():
    SERVER = 'server'
    SERVER_ADDRESS = 'address'
    SERVER_PORT = 'port'
