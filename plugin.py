""" Base class for all taemin plugin """

import docopts

class SimplenetPlugin():
    helper = {}

    def __init__(self, taemin):
        self.log = logging.getLogger()

    def start(self):
        self.log.info("Starting plugin %s", __name__)

    def clean(self):
        pass

    def build(self):
        pass
