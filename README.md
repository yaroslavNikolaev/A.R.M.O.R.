## A.R.M.O.R. - Altered-Reality Monitoring and Operational Response 

###Mission
    Detect difference between current version of installed software and the newest one.
    ARMOR is designed to help developers and devops to keep application up to date.
    ARMOR can support any kind of storage in order to persist state of cluster
###Repository structure: 
    armor.py - entry endpoint. 
    scanners.py - contains classes which relay on reflection to collect set of 
    mutator.py - simple application to annotate your k8 cluster and check how A.R.M.O.R works. 
    package utils - contains main part of armor framework
        - version.py - script with versions classes, which are used to store application version in A.R.O.R. format.
        - collectors.py - contains common classes of collectors. Main responsibility to collect Application Versions.
        - configuration.py - contains A.R.M.O.R configuration
        - verifiers.py - contains common classes of verifiers. Main responsibility to highlight that how severe version lag. 
        - producer.py - contains common classes of producers. Main responsibility to provide prometheus client output. 
    packages gcp,azure,party3rd,aws - contains collectors for external sources.
    folder armor-io - contains helm chart for armor
### How to start to work with A.R.M.O.R
    1. You can take default helm chart or override default values with our own values file. 
    In order to test: helm template armor-io --values gcp.yaml 
    2. Deploy to your central cluster or to 
###ARMOR supports following collectors:
<table style="width:100%">  <tr>    <th>Application</th>    <th>Armor annotation key</th>    <th>Description</th>  </tr><tr>    <th>aks</th>    <th>armor.io/azure.kubernetes.aks</th>    <th></th>  </tr>
<tr>    <th>memorystore</th>    <th>armor.io/gcp.c_plus_clients.memorystore</th>    <th></th>  </tr>
<tr>    <th>bigtable</th>    <th>armor.io/gcp.java_clients.bigtable</th>    <th></th>  </tr>
<tr>    <th>spanner</th>    <th>armor.io/gcp.java_clients.spanner</th>    <th></th>  </tr>
<tr>    <th>gke</th>    <th>armor.io/gcp.kubernetes.gke</th>    <th></th>  </tr>
<tr>    <th>cloud-postgres</th>    <th>armor.io/gcp.storages.cloud-postgres</th>    <th></th>  </tr>
<tr>    <th>redis-memorystore</th>    <th>armor.io/gcp.storages.redis-memorystore</th>    <th></th>  </tr>
<tr>    <th>velero</th>    <th>armor.io/party3rd.backups.velero</th>    <th></th>  </tr>
<tr>    <th>redis</th>    <th>armor.io/party3rd.c_plus_clients.redis</th>    <th></th>  </tr>
<tr>    <th>alertmanager</th>    <th>armor.io/party3rd.cloud_native.alertmanager</th>    <th></th>  </tr>
<tr>    <th>armor</th>    <th>armor.io/party3rd.cloud_native.armor</th>    <th></th>  </tr>
<tr>    <th>ingress-gce</th>    <th>armor.io/party3rd.cloud_native.ingress-gce</th>    <th></th>  </tr>
<tr>    <th>ingress-nginx</th>    <th>armor.io/party3rd.cloud_native.ingress-nginx</th>    <th></th>  </tr>
<tr>    <th>k8</th>    <th>armor.io/party3rd.cloud_native.k8</th>    <th></th>  </tr>
<tr>    <th>k8master</th>    <th>armor.io/party3rd.cloud_native.k8master</th>    <th></th>  </tr>
<tr>    <th>k8worker</th>    <th>armor.io/party3rd.cloud_native.k8worker</th>    <th></th>  </tr>
<tr>    <th>kubernetes</th>    <th>armor.io/party3rd.cloud_native.kubernetes</th>    <th></th>  </tr>
<tr>    <th>node_exporter</th>    <th>armor.io/party3rd.cloud_native.node_exporter</th>    <th></th>  </tr>
<tr>    <th>prometheus</th>    <th>armor.io/party3rd.cloud_native.prometheus</th>    <th></th>  </tr>
<tr>    <th>auditbeat</th>    <th>armor.io/party3rd.elastic.auditbeat</th>    <th></th>  </tr>
<tr>    <th>elasticsearch</th>    <th>armor.io/party3rd.elastic.elasticsearch</th>    <th></th>  </tr>
<tr>    <th>filebeat</th>    <th>armor.io/party3rd.elastic.filebeat</th>    <th></th>  </tr>
<tr>    <th>journalbeat</th>    <th>armor.io/party3rd.elastic.journalbeat</th>    <th></th>  </tr>
<tr>    <th>kibana</th>    <th>armor.io/party3rd.elastic.kibana</th>    <th></th>  </tr>
<tr>    <th>logstash</th>    <th>armor.io/party3rd.elastic.logstash</th>    <th></th>  </tr>
<tr>    <th>metricbeat</th>    <th>armor.io/party3rd.elastic.metricbeat</th>    <th></th>  </tr>
<tr>    <th>clamav</th>    <th>armor.io/party3rd.monitoring.clamav</th>    <th></th>  </tr>
<tr>    <th>fluentd</th>    <th>armor.io/party3rd.monitoring.fluentd</th>    <th></th>  </tr>
<tr>    <th>grafana</th>    <th>armor.io/party3rd.monitoring.grafana</th>    <th></th>  </tr>
<tr>    <th>kiali</th>    <th>armor.io/party3rd.monitoring.kiali</th>    <th></th>  </tr>
<tr>    <th>zookeeper</th>    <th>armor.io/party3rd.monitoring.zookeeper</th>    <th></th>  </tr>
<tr>    <th>calico</th>    <th>armor.io/party3rd.network.calico</th>    <th></th>  </tr>
<tr>    <th>haproxy</th>    <th>armor.io/party3rd.network.haproxy</th>    <th></th>  </tr>
<tr>    <th>istio</th>    <th>armor.io/party3rd.network.istio</th>    <th></th>  </tr>
<tr>    <th>nginx</th>    <th>armor.io/party3rd.network.nginx</th>    <th></th>  </tr>
<tr>    <th>constant</th>    <th>armor.io/utils.collectors.constant</th>    <th></th>  </tr>
<tr>    <th>mock</th>    <th>armor.io/utils.collectors.mock</th>    <th></th>  </tr>
</table> 

###ARMOR supports following storages: 
- Prometheus 
