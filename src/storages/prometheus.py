import logging, time, typing, concurrent, threading
import prometheus_client
from storages.abstract import AbstractStorage
from utils.configuration import Configuration
from prometheus_client.core import GaugeMetricFamily, CollectorRegistry
from utils.producers import AbstractMetricProducer, Metric

COMMON_LABEL_TITLES = []


class MultiThreadCollectorRegistry(CollectorRegistry):

    def collect(self):
        """Yields metrics from the collectors in the registry."""
        futures = []
        result = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            for collector in self._collector_to_names:
                futures.append(executor.submit(collector.collect))
            for future in futures:
                result += future.result()
            return result


class PrometheusStorage(AbstractStorage):
    cluster: str
    port: int
    info_title = "armor_metrics"
    version_title = 'Information about internally used applications versions'
    label_titles = ["cluster", "severity", "resource", "tool", "using", "vendor"]
    registry = MultiThreadCollectorRegistry(auto_describe=True)

    def __init__(self, config: Configuration):
        super().__init__(config)
        self.cluster = config.name()
        self.port = config.port()
        threading.Thread(target=self._launch_http_server).start()

    def _launch_http_server(self):
        logging.info(f"Prometheus storage is going to launch http server on {self.port}")
        prometheus_client.start_http_server(self.port, registry=self.registry)
        while True:
            time.sleep(1)

    def persist(self, metrics: typing.List[Metric]) -> typing.List[GaugeMetricFamily]:
        return map(self.__covert_to_prometheus_metric, metrics)

    def __covert_to_prometheus_metric(self, metric: Metric) -> GaugeMetricFamily:
        channel_metric = GaugeMetricFamily(self.info_title, self.version_title, labels=self.label_titles)
        resource = metric.source.resource_definition()
        app_name = metric.source.short_app_name()
        severity = metric.severity.value
        labels = [self.cluster, severity, resource, app_name, str(metric.source), str(metric.target)]
        channel_metric.add_metric(labels, metric.diff)
        return channel_metric

    def register(self, producer: AbstractMetricProducer):
        wrapper = PrometheusWrapper(producer, self)
        self.registry.register(wrapper)


class PrometheusWrapper(object):
    producer: AbstractMetricProducer
    storage: PrometheusStorage

    def __init__(self, producer: AbstractMetricProducer, storage: PrometheusStorage):
        self.producer = producer
        self.storage = storage

    def collect(self) -> typing.Iterator[GaugeMetricFamily]:
        return self.storage.persist(self.producer.collect())
