import inspect
import logging
from party3rd import *
from gcp import *
from aws import *
from azure import *
from utils.collectors import *
from utils.verifiers import *
from utils.configuration import Configuration
from abc import ABCMeta


class CollectorFactory(object):
    _instance = None
    collectors: typing.Dict[str, VersionCollector.__class__]
    config: Configuration

    def __init__(self, config: Configuration):
        self.collectors = collect_application_subclasses(VersionCollector)
        self.config = config

    def instantiate_collector(self, application: str, *args) -> VersionCollector:
        logging.debug(f'Processing application {application}')
        if application not in self.collectors:
            logging.warning(f"Be aware, Application collector is not exist for {application}. Mock will be used")
            return MockCollector(self.config)
        return self.collectors[application](self.config, *args)

    # i'm not sure about code location
    def instantiate_k8_service_collector(self) -> VersionCollector:
        k8_service = self.config.kubernetes_application()
        return self.instantiate_collector(k8_service)


class SeverityManager(object):
    providers: typing.Dict[str, AbstractSeverityVerifier]

    def __init__(self):
        self.providers = dict()
        classes = collect_application_subclasses(AbstractSeverityVerifier)
        for application in classes.keys():
            self.providers[application] = classes[application]()

    def get_severity(self, version: ApplicationVersion, channel: Channel, value: int) -> Severity:
        application = version.app
        if application not in self.providers:
            application = "utils.verifiers.default"
        return self.providers[application].get_severity(channel, value)


def collect_application_subclasses(clazz: ABCMeta) -> dict:
    result = dict()
    for class_ in clazz.__subclasses__():
        # from module import subclass.
        if len(class_.__subclasses__()) != 0:
            sub_result = collect_application_subclasses(class_)
            confluence = result.keys() & sub_result.keys()
            if len(confluence) > 0:
                raise KeyError(
                    f"{str(confluence)}: Already exist , duplicates in source code for subclasses of {str(clazz)}")
            result.update(sub_result)
        if not inspect.isabstract(class_):
            application = class_.get_application_name()
            package = inspect.getmodule(class_).__name__
            full_name = package + "." + application
            if full_name in result:
                raise KeyError(f"{full_name}: Already exist , duplicates in source code for subclasses of {str(clazz)}")
            logging.info(f'New subclass of {str(clazz)} was found : {full_name} , implementation: {str(class_)}')
            result[full_name] = class_
    return result
