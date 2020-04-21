import typing
from abc import ABC, abstractmethod
from utils.producers import AbstractMetricProducer, Metric
from utils.configuration import Configuration


class AbstractStorage(ABC):

    @abstractmethod
    def __init__(self, config: Configuration):
        pass

    @abstractmethod
    def persist(self, metric: typing.List[Metric]) -> typing.Iterator:
        pass

    @abstractmethod
    def register(self, producer: AbstractMetricProducer):
        pass
