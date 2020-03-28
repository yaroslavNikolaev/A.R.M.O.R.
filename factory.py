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
        clazz = VersionCollector
        self.__init_collectors(clazz)
        self.config = config

    def instantiate_collector(self, application: str, *args) -> VersionCollector:
        logging.debug(f'Processing application {application}')
        if application not in self.collectors:
            logging.warning(f"Be aware, Application collector is not exist for {application}. Mock will be used")
            return MockCollector(self.config)
        return self.collectors[application](self.config, *args)

    # i'm not sure
    def instantiate_k8_service_collector(self) -> VersionCollector:
        k8_service = self.config.kubernetes_application()
        return self.instantiate_collector(k8_service)

    def __init_collectors(self, clazz):
        for class_ in clazz.__subclasses__():
            # from module import subclass.
            if len(class_.__subclasses__()) != 0:
                self.__init_collectors(class_)
            if not inspect.isabstract(class_):
                application = class_.get_application_name()
                package = str(inspect.getmodule(class_).__name__).split(".")[0]
                full_name = package + "." + application
                if full_name in self.collectors:
                    raise KeyError(full_name + ": Already exist , plz check collectors")
                logging.info(f'New collector was found : {full_name}')
                self.collectors[full_name] = class_
