# A.R.M.O.R.
Altered-Reality Monitoring and Operational Response

Detect difference between current version of installed software and the newest one.  
ARMOR is designed to help developers and devops to keep application up to date.
ARMOR is built on top of Prometheus monitoring application. 

Repository structure: 
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



In order to override: helm template armor --values gcp.yaml 