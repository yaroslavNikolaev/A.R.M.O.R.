from utils.configuration import Configuration
from scanners import CollectorFactory

INTRO = '''## A.R.M.O.R. - Altered-Reality Monitoring and Operational Response 

>###Mission
    Detect difference between current version of installed software and the newest one.
    ARMOR is designed to help developers and devops to keep application up to date.
    ARMOR can support any kind of storage in order to persist state of cluster\n'''

STRUCTURE = '''>###Repository structure: 
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
    folder armor-io - contains helm chart for armor\n'''

HOWTO = '''>### How to start to work with A.R.M.O.R
    1. You can take default helm chart or override default values with our own values file. 
    In order to test: helm template armor-io --values gcp.yaml 
    2. Deploy to your central cluster or to 
'''

COLLECTORS = '''>###ARMOR supports following collectors:
<table style="width:100%">  <tr>    <th>Application</th>    <th>Armor convention</th>    <th>Description</th>  </tr>'''


STORAGES = '''\n>###ARMOR supports following storages: 
- Prometheus \n'''

if __name__ == '__main__':
    '''Automatically generate Readme.md'''
    configuration = Configuration()
    factory = CollectorFactory(configuration)
    with open("README.md", "w") as readme:
        readme.write(INTRO)
        readme.write(STRUCTURE)
        readme.write(HOWTO)
        readme.write(COLLECTORS)
        # todo add description to collectors and storages
        description = ""
        for key in sorted(factory.collectors.keys()):
            application = key.split(".")[-1]
            readme.write(f'''<tr>    <th>{application}</th>    <th>{key}</th>    <th>{description}</th>  </tr>\n''')
        readme.write("""</table> \n""")
        readme.write(STORAGES)

