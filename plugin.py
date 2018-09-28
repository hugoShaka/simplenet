"""Abstract class for all SimplenetPlugins"""

import os
import logging

import docopt


class SimplenetPlugin:
    """Abstract class for all SimplenetPlugins"""

    name = None

    def __init__(self, plugin_args):
        """
        Initialize the plugin
        :param plugin_args: arguments of the command
        """
        # self.name should be defined before calling super()
        assert self.name is not None

        self.log = logging.getLogger(__name__)
        self.args = docopt.docopt(self.__doc__, argv=plugin_args)
        self.pwd = os.path.dirname(os.path.abspath(__file__))
        self.temp_dir = self.pwd + "/.tmp"
        self.plugin_dir = "%s/plugins/%s" % (self.pwd, self.name)
        self.log.debug(plugin_args)

    def start(self):
        """Starts the plugin"""
        raise NotImplementedError

    def clean(self):
        """Cleans what the plugin have done"""
        raise NotImplementedError

    def build(self):
        """Build tools needed for the plugin"""
        raise NotImplementedError
