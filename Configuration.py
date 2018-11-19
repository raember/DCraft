import json
import logging
import os
import copy


class Configuration:
    """Configuration class. Handles the management of all the configurations."""
    filename = 'config.json'
    path = ''
    log = None
    data = {}
    skel = {}

    def __init__(self):
        self.log = logging.getLogger(self.__class__.__name__)

    def __getitem__(self, item):
        return self.data[item]

    def load(self, path=''):
        """
        Loads data from file.
        :param path: Path to config file or directory. Defaults to filename variable.
        :type path: str
        :return: Success
        :rtype: bool
        """
        if path == '':
            path = self.filename
        elif os.path.isdir(path):
            path += self.filename
        self.path = path
        if not os.path.exists(path):
            return False
        try:
            with open(path, 'r') as config_file:
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

    def save(self, path=''):
        """
        Saves data to file.
        :param path: Path to config file or directory. Defaults to filename variable.
        :type path: str
        :return: Success
        :rtype: bool
        """
        if path == '':
            path = self.path
        if os.path.isdir(path):
            path += self.filename
        try:
            with open(path, 'w') as fp:
                json.dump(self.data, fp, indent=2)
        except FileNotFoundError as ex:
            self.log.error(ex)
            return False
        except Exception as ex:
            self.log.error(ex)
            return False

    def complete_data(self):
        """Completes datastructure."""
        self.data: dict = self._complete_with_skel(self.data, self.skel)

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
            return copy.deepcopy(skel)
        if type(skel) == list:
            # Prepare datastructures
            skellist: list = skel
            if not type(data) == list:
                datalist = []
            else:
                datalist: list = data
            # Recurse copy value
            for element in skellist:
                if not element in datalist:
                    datalist.append(Configuration._complete_with_skel(None, element))
            return datalist
        elif type(skel) == dict:
            # Prepare datastructures
            skeldict: dict = skel
            if not type(data) == dict:
                datadict = {}
            else:
                datadict: dict = data
            # Recurse copy value
            for key in skeldict:
                if key not in datadict:
                    datadict[key] = None
                datadict[key] = Configuration._complete_with_skel(datadict[key], skeldict[key])
            return datadict
        else:
            return data
