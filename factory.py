import inspect
import logging
from party3rd import *
from gcp import *
from aws import *
from azure import *
from utils.collectors import *
from utils.configuration import Configuration


class CollectorFactory(object):
    _instance = None
    collectors = dict()
    config: Configuration

    def __init__(self, config: Configuration):
        self.__init_collectors(VersionCollector)
        self.config = config

    def instantiate_collector(self, application: str, *args) -> VersionCollector:
        logging.debug(f'Processing handler {application}')
        return self.collectors[application](self.config, *args)

    # todo think how to do it right.
    def get_predefined_collector(self, version: NodeVersion):
        return PredefinedVersionCollector(self.config, version)

    def __init_collectors(self, clazz):
        for class_ in clazz.__subclasses__():
            if class_.__name__ in self.collectors:
                raise KeyError(class_.__name__ + ": Already exist , plz check collectors")
            # from module import subclass.
            if len(class_.__subclasses__()) != 0:
                self.__init_collectors(class_)
            if not inspect.isabstract(class_):
                logging.info(f'New collector was found : {class_.__name__}')
                self.collectors[class_.__name__] = class_
